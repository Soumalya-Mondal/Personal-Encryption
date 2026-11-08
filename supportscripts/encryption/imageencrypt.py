# Define "image_encrypt" Function
def image_encrypt(database_file_path: str, encryption_password: str) -> dict[str, str]:
    # Define Constant
    SALT_SIZE = 64
    encrypted_images_details_nested_list = []

    # Importing Python Modules:S1
    try:
        from pathlib import Path
        import shutil
        import base64
        import secrets
        import hashlib
        import sqlite3
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encrypt', 'step': '1', 'message': str(error)}

    # Define Folder Path And Database File Path Object:S2
    try:
        parent_folder_path = Path.cwd()
        database_file_path_object = Path(database_file_path)
        tmp_folder_path = Path(parent_folder_path) / 'tmp'
        encoded_images_folder_path = Path(tmp_folder_path) / 'EncodedImages'
        encrypted_images_folder_path = Path(tmp_folder_path) / 'EncryptedImages'
        images_folder_path_object = Path(parent_folder_path) / 'images'
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encrypt', 'step': '2', 'message': str(error)}

    # Recreate "EncryptedImages" Folder:S3
    try:
        if encrypted_images_folder_path.exists() and encrypted_images_folder_path.is_dir():
            shutil.rmtree(encrypted_images_folder_path)
        encrypted_images_folder_path.mkdir(parents = True, exist_ok = True)
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encrypt', 'step': '3', 'message': str(error)}

    # Check "EncodedImages" Folder Exists And Is Not Empty:S4
    try:
        encoded_images_folder_path_object = Path(encoded_images_folder_path)
        if not (encoded_images_folder_path_object.exists() and encoded_images_folder_path_object.is_dir()):
            return {'status': 'ERROR', 'file_name': 'Image-Encrypt', 'step': '4', 'message': '"EncodedImages" Folder Not Present'}
        if not any(encoded_images_folder_path_object.iterdir()):
            return {'status': 'INFO', 'file_name': 'Image-Encrypt', 'step': '4', 'message': '"EncodedImages" Folder Is Empty'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encrypt', 'step': '4', 'message': str(error)}

    # Fetch Encoded Image Details From Database:S5
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_connection.row_factory = sqlite3.Row
            db_cursor = db_connection.cursor()
            encoded_images_details_rows = db_cursor.execute('''
                SELECT ed.*
                FROM encoded_images_details ed
                INNER JOIN raw_images_details rd ON ed.raw_file_id = rd.file_id
                WHERE rd.file_status = ?
                ORDER BY ed.id
            ''', ('Encoded',)).fetchall()
        if not encoded_images_details_rows:
            return {'status': 'INFO', 'file_name': 'Image-Encrypt', 'step': '5', 'message': 'No Encoded Image Details Found In Database'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encrypt', 'step': '5', 'message': str(error)}

    # Encrypt Encoded Text Files:S6
    try:
        print('')
        for encoded_image_details_row in encoded_images_details_rows:
            encoded_text_file_path = Path(encoded_image_details_row['file_path'])
            plaintext = encoded_text_file_path.read_bytes()
            salt = secrets.token_bytes(SALT_SIZE)
            kdf = Argon2id(
                salt = salt,
                length = 32,
                iterations = 3,
                lanes = 4,
                memory_cost = 64 * 1024,
            )
            encryption_key = base64.urlsafe_b64encode(kdf.derive(encryption_password.encode('utf-8')))
            ciphertext = Fernet(encryption_key).encrypt(plaintext)
            encrypted_file_path = encrypted_images_folder_path / encoded_text_file_path.stem
            with encrypted_file_path.open('xb') as output:
                output.write(salt + ciphertext)
            print(f'"{encoded_text_file_path.name}" Has Been Encrypted With Password')
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encrypt', 'step': '6', 'message': str(error)}

    # Delete And Recreate "images" Folder, Copy Encrypted Files:S7
    try:
        if images_folder_path_object.exists() and images_folder_path_object.is_dir():
            shutil.rmtree(images_folder_path_object)
        images_folder_path_object.mkdir(parents = True, exist_ok = True)
        encrypted_image_file_path_list = sorted(
            file_path for file_path in encrypted_images_folder_path.iterdir()
            if file_path.is_file()
        )
        for encrypted_file_path in encrypted_image_file_path_list:
            shutil.copy(str(encrypted_file_path), str(images_folder_path_object))
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encrypt', 'step': '7', 'message': str(error)}

    # Fetch Encrypted Image Details:S8
    try:
        for encrypted_image_file_path in encrypted_image_file_path_list:
            raw_file_id = encrypted_image_file_path.stem
            file_name = encrypted_image_file_path.name
            original_file_path = str(encrypted_image_file_path)
            copied_file_path = str(images_folder_path_object / encrypted_image_file_path.name)
            file_size_bytes = encrypted_image_file_path.stat().st_size
            file_hash = hashlib.md5(encrypted_image_file_path.read_bytes()).hexdigest()
            encrypted_images_details_nested_list.append(
                (raw_file_id, file_name, original_file_path, copied_file_path, file_size_bytes, file_hash)
            )
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encrypt', 'step': '8', 'message': str(error)}

    # Insert Encrypted Image Details Into Database:S9
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_cursor = db_connection.cursor()
            db_cursor.executemany('''
                INSERT INTO encrypted_images_details (raw_file_id, file_name, original_file_path, copied_file_path, file_size_bytes, file_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', encrypted_images_details_nested_list)
            db_connection.commit()
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encrypt', 'step': '9', 'message': str(error)}

    # Update Raw Images Status To "Encrypted":S10
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_cursor = db_connection.cursor()
            for encoded_image_details_row in encoded_images_details_rows:
                db_cursor.execute(
                    'UPDATE raw_images_details SET file_status = ? WHERE file_id = ?',
                    ('Encrypted', encoded_image_details_row['raw_file_id'])
                )
            db_connection.commit()
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encrypt', 'step': '10', 'message': str(error)}

    # Delete "tmp" Folder:S11
    try:
        shutil.rmtree(tmp_folder_path)
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encrypt', 'step': '11', 'message': str(error)}

    # Return Success:S12
    return {'status': 'SUCCESS', 'file_name': 'Image-Encrypt', 'step': '12', 'message': 'All The Images Encrypted Successfully'}