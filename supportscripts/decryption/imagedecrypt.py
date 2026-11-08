# Define "image_decrypt" Function
def image_decrypt(images_folder_path: str, encryption_password: str) -> dict[str, str]:
    # Define Constant
    SALT_SIZE = 64

    # Importing Python Modules:S1
    try:
        from pathlib import Path
        import shutil
        import base64
        from cryptography.fernet import Fernet, InvalidToken
        from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '1', 'message': str(error)}

    # Define Folder Path:S2
    try:
        parent_folder_path = Path.cwd()
        tmp_folder_path = Path(parent_folder_path) / 'tmp'
        encoded_images_folder_path = Path(tmp_folder_path) / 'EncodedImages'
        images_folder_path_object = Path(images_folder_path)
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '2', 'message': str(error)}

    # Recreate "EncodedImages" Folder:S3
    try:
        if encoded_images_folder_path.exists() and encoded_images_folder_path.is_dir():
            shutil.rmtree(encoded_images_folder_path)
        encoded_images_folder_path.mkdir(parents = True, exist_ok = True)
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '3', 'message': str(error)}

    # Check If "images" Folder Is Present:S4
    try:
        if not (images_folder_path_object.exists() and images_folder_path_object.is_dir()):
            return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '4', 'message': f'"{images_folder_path_object.name}" Folder Not Present'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '4', 'message': str(error)}

    # Create Encrypted File Path List:S5
    try:
        encrypted_image_file_path_list = sorted(
            file_path for file_path in images_folder_path_object.iterdir()
            if file_path.is_file()
        )
        if not encrypted_image_file_path_list:
            return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '5', 'message': f'No Encrypted Files Found In "{images_folder_path_object.name}" Folder'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '5', 'message': str(error)}

    # Decrypt Encrypted Files:S6
    try:
        for decrypted_number, encrypted_image_file_path in enumerate(encrypted_image_file_path_list, start = 1):
            encrypted_data = encrypted_image_file_path.read_bytes()
            if len(encrypted_data) <= SALT_SIZE:
                return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '6', 'message': f'Invalid or incomplete encrypted file: {encrypted_image_file_path.name}'}
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
                return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '6', 'message': f'Incorrect password or damaged encrypted file: {encrypted_image_file_path.name}'}
            decrypted_file_path = encoded_images_folder_path / f'{encrypted_image_file_path.name}.txt'
            decrypted_file_path.write_bytes(plaintext)
            print(f'{decrypted_number:05d}-> "{encrypted_image_file_path.name}" Has Been Decrypted With Password')
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '6', 'message': str(error)}

    # Clear "images" Folder:S7
    try:
        for images_item_path in images_folder_path_object.iterdir():
            if images_item_path.is_dir():
                shutil.rmtree(images_item_path)
            else:
                images_item_path.unlink()
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decrypt', 'step': '7', 'message': str(error)}

    # Return Success:S8
    return {'status': 'SUCCESS', 'file_name': 'Image-Decrypt', 'step': '8', 'message': 'All The Images Decrypted Successfully'}