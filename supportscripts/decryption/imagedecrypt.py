# Define "image_decrypt" Function
def image_decrypt(database_file_path: str, images_folder_path: str, encryption_password: str) -> dict[str, str]:
    # Define Constant
    SALT_SIZE = 64

    # Importing Python Modules:S1
    try:
        from pathlib import Path
        import shutil
        import base64
        import sqlite3
        import hashlib
        from cryptography.fernet import Fernet, InvalidToken
        from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '1', 'message': str(error)}

    # Define Folder Path:S2
    try:
        parent_folder_path = Path.cwd()
        database_file_path_object = Path(database_file_path)
        images_folder_path_object = Path(images_folder_path)
        tmp_folder_path = Path(parent_folder_path) / 'tmp'
        encoded_images_folder_path = Path(tmp_folder_path) / 'EncodedImages'
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '2', 'message': str(error)}

    # Recreate "EncodedImages" Folder:S3
    try:
        if encoded_images_folder_path.exists() and encoded_images_folder_path.is_dir():
            shutil.rmtree(encoded_images_folder_path)
        encoded_images_folder_path.mkdir(parents = True, exist_ok = True)
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '3', 'message': str(error)}

    # Create List Of No-Extension Encrypted Files From "images" Folder:S4
    try:
        if not images_folder_path_object.exists():
            return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '4', 'message': 'Images Folder Not Found'}
        encrypted_image_file_path_list = [
            file_path
            for file_path in images_folder_path_object.iterdir()
            if file_path.is_file() and file_path.suffix == ''
        ]
        if not encrypted_image_file_path_list:
            return {'status': 'INFO', 'file_name': 'Image-Decrypt', 'step': '4', 'message': 'No Encrypted Files Found In "images" Folder'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '4', 'message': str(error)}

    # Decrypt Encrypted Files From "images" Folder:S5
    try:
        for encrypted_image_file_path in encrypted_image_file_path_list:
            encrypted_data = encrypted_image_file_path.read_bytes()
            if len(encrypted_data) <= SALT_SIZE:
                return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '5', 'message': f'Invalid or incomplete encrypted file: {encrypted_image_file_path.name}'}
            salt = encrypted_data[:SALT_SIZE]
            ciphertext = encrypted_data[SALT_SIZE:]
            kdf = Argon2id(
                salt = salt,
                length = 32,
                iterations = 3,
                lanes = 4,
                memory_cost = 64 * 1024,
            )
            decryption_key = base64.urlsafe_b64encode(kdf.derive(encryption_password.encode('utf-8')))
            try:
                plaintext = Fernet(decryption_key).decrypt(ciphertext)
            except InvalidToken:
                return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '5', 'message': f'Incorrect password or damaged encrypted file: {encrypted_image_file_path.name}'}
            decrypted_file_path = encoded_images_folder_path / f'{encrypted_image_file_path.name}.txt'
            decrypted_file_path.write_bytes(plaintext)
            print(f'"{encrypted_image_file_path.name}" Has Been Decrypted With Password')
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '5', 'message': str(error)}

    # Create Decrypted Text File Details Dictionary From "EncodedImages" Folder:S6
    try:
        decrypted_text_file_details_dict = {
            file_path.name: hashlib.md5(file_path.read_bytes()).hexdigest()
            for file_path in encoded_images_folder_path.iterdir()
            if file_path.is_file() and file_path.suffix.lower() == '.txt'
        }
        if not decrypted_text_file_details_dict:
            return {'status': 'INFO', 'file_name': 'Image-Decrypt', 'step': '6', 'message': 'No Decrypted Text Files Found In "EncodedImages" Folder'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '6', 'message': str(error)}

    # Compare Decrypted File Hashes With "encoded_images_details" Table:S7
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_connection.row_factory = sqlite3.Row
            db_cursor = db_connection.cursor()
            for decrypted_file_name, decrypted_file_hash in decrypted_text_file_details_dict.items():
                encoded_image_details_row = db_cursor.execute(
                    'SELECT file_hash FROM encoded_images_details WHERE file_name = ?',
                    (decrypted_file_name,)
                ).fetchone()
                if not encoded_image_details_row:
                    return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '7', 'message': f'No Encoded Image Details Found For "{decrypted_file_name}"'}
                encoded_file_hash = encoded_image_details_row['file_hash']
                if decrypted_file_hash != encoded_file_hash:
                    return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '7', 'message': f'Hash Mismatch For "{decrypted_file_name}"'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '7', 'message': str(error)}

    # Delete "images" Folder:S8
    try:
        if images_folder_path_object.exists() and images_folder_path_object.is_dir():
            shutil.rmtree(images_folder_path_object)
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '8', 'message': str(error)}

    # Return Success:S9
    return {'status': 'SUCCESS', 'file_name': 'Image-Decrypt', 'step': '9', 'message': 'All The Images Decrypted Successfully'}
