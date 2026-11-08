# Define "raw_images_details_insert" Function
def raw_images_details_insert(database_file_path: str, images_folder_path: str) -> dict[str, str]:
    # Define Constant
    image_details_nested_list = []

    # Importing Python Modules:S1
    try:
        from pathlib import Path
        import sqlite3
        import hashlib
        import secrets
        import string
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Raw-Image-Details-Insert', 'step': '1', 'message': str(error)}

    # Define Folder And Database File Path Object:S2
    try:
        images_folder_path_object = Path(images_folder_path)
        database_file_path_object = Path(database_file_path)
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Raw-Image-Details-Insert', 'step': '2', 'message': str(error)}

    # Check If Database File Exists:S3
    try:
        if not database_file_path_object.exists() or not database_file_path_object.is_file():
            return {'status': 'ERROR', 'file_name': 'Raw-Image-Details-Insert', 'step': '3', 'message': 'Database File Not Found'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Raw-Image-Details-Insert', 'step': '3', 'message': str(error)}

    # Check If Images Folder Exists And Is Not Empty:S4
    try:
        if not images_folder_path_object.exists() or not images_folder_path_object.is_dir():
            return {'status': 'ERROR', 'file_name': 'Raw-Image-Details-Insert', 'step': '4', 'message': 'Images Folder Not Found'}
        if not any(images_folder_path_object.iterdir()):
            return {'status': 'INFO', 'file_name': 'Raw-Image-Details-Insert', 'step': '4', 'message': 'Images Folder Is Empty'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Raw-Image-Details-Insert', 'step': '4', 'message': str(error)}

    # Fetch Image Details:S5
    try:
        input_image_file_path_list = sorted(
            file_path for file_path in images_folder_path_object.iterdir()
            if file_path.is_file()
        )
        for input_image_file_path in input_image_file_path_list:
            file_name = input_image_file_path.name
            file_path = str(input_image_file_path)
            file_type = input_image_file_path.suffix.lower().lstrip('.') or 'jpg'
            file_size_bytes = input_image_file_path.stat().st_size
            file_hash = hashlib.md5(input_image_file_path.read_bytes()).hexdigest()
            image_details_nested_list.append(
                (file_name, file_path, file_type, file_size_bytes, file_hash, 'Original')
            )
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Raw-Image-Details-Insert', 'step': '5', 'message': str(error)}

    # Insert Image Details Into Database With Unique File IDs:S6
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_cursor = db_connection.cursor()
            for image_details_tuple in image_details_nested_list:
                while True:
                    file_id = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                    existing_file_id_row = db_cursor.execute(
                        'SELECT 1 FROM raw_images_details WHERE file_id = ?',
                        (file_id,)
                    ).fetchone()
                    if existing_file_id_row is None:
                        break
                db_cursor.execute('''
                    INSERT INTO raw_images_details (file_id, file_name, file_path, file_type, file_size_bytes, file_hash, file_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (file_id,) + image_details_tuple)
            db_connection.commit()
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Raw-Image-Details-Insert', 'step': '6', 'message': str(error)}

    # Return Success:S7
    return {'status': 'SUCCESS', 'file_name': 'Raw-Image-Details-Insert', 'step': '7', 'message': 'Image Details Inserted Successfully'}