# Define "image_check" Function
def image_check(database_file_path: str, images_folder_path: str) -> dict[str, object]:
    # Define Constant
    encrypted_images_details_list = []

    # Importing Python Modules:S1
    try:
        from pathlib import Path
        import sqlite3
        import hashlib
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Check', 'step': '1', 'message': str(error)}

    # Define Folder And Database File Path Object:S2
    try:
        database_file_path_object = Path(database_file_path)
        images_folder_path_object = Path(images_folder_path)
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Check', 'step': '2', 'message': str(error)}

    # Check Database File Exists:S3
    try:
        if not (database_file_path_object.exists() and database_file_path_object.is_file()):
            return {'status': 'ERROR', 'file_name': 'Image-Check', 'step': '3', 'message': 'Database File Not Found'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Check', 'step': '3', 'message': str(error)}

    # Check Images Folder Exists And Is Not Empty:S4
    try:
        if not (images_folder_path_object.exists() and images_folder_path_object.is_dir()):
            return {'status': 'ERROR', 'file_name': 'Image-Check', 'step': '4', 'message': 'Images Folder Not Found'}
        if not any(images_folder_path_object.iterdir()):
            return {'status': 'INFO', 'file_name': 'Image-Check', 'step': '4', 'message': 'Images Folder Is Empty'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Check', 'step': '4', 'message': str(error)}

    # Fetch Encrypted Images Copied File Path And Hash From Database:S5
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_connection.row_factory = sqlite3.Row
            db_cursor = db_connection.cursor()
            encrypted_images_details_rows = db_cursor.execute('''
                SELECT eid.copied_file_path, eid.file_hash
                FROM encrypted_images_details eid
                INNER JOIN raw_images_details rid ON eid.raw_file_id = rid.file_id
                WHERE rid.file_status = ?
                ORDER BY eid.id
            ''', ('Encrypted',)).fetchall()
        if not encrypted_images_details_rows:
            return {'status': 'INFO', 'file_name': 'Image-Check', 'step': '5', 'message': 'No Encrypted Image Details Found In Database'}
        encrypted_images_details_list = [
            {'copied_file_path': row['copied_file_path'], 'file_hash': row['file_hash']}
            for row in encrypted_images_details_rows
        ]
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Check', 'step': '5', 'message': str(error)}

    # Verify Encrypted Image Files Exists And Hash Match:S6
    try:
        for encrypted_image_details in encrypted_images_details_list:
            encrypted_image_file_path = Path(encrypted_image_details['copied_file_path'])
            if not (encrypted_image_file_path.exists() and encrypted_image_file_path.is_file()):
                return {'status': 'ERROR', 'file_name': 'Image-Check', 'step': '6', 'message': f'File Not Found: {encrypted_image_file_path.name}'}
            actual_file_hash = hashlib.md5(encrypted_image_file_path.read_bytes()).hexdigest()
            if actual_file_hash != encrypted_image_details['file_hash']:
                return {'status': 'ERROR', 'file_name': 'Image-Check', 'step': '6', 'message': f'Hash Mismatch: {encrypted_image_file_path.name}'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Check', 'step': '6', 'message': str(error)}

    # Return Success:S7
    return {'status': 'SUCCESS', 'file_name': 'Image-Check', 'step': '7', 'message': 'All Encrypted Images Verified Successfully'}