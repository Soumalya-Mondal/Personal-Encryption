# Define "image_encode" Function
def image_encode(database_file_path: str) -> dict[str, str]:
    # Define Constant
    encoded_images_details_nested_list = []

    # Importing Python Modules:S1
    try:
        from pathlib import Path
        import shutil
        import base64
        import sqlite3
        import hashlib
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encode', 'step': '1', 'message': str(error)}

    # Define Folder Path And Database File Path Object:S2
    try:
        parent_folder_path = Path.cwd()
        database_file_path_object = Path(database_file_path)
        tmp_folder_path = Path(parent_folder_path) / 'tmp'
        converted_images_folder_path = Path(tmp_folder_path) / 'ConvertedImages'
        encoded_images_folder_path = Path(tmp_folder_path) / 'EncodedImages'
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encode', 'step': '2', 'message': str(error)}

    # Recreate "EncodedImages" Folder:S3
    try:
        if encoded_images_folder_path.exists() and encoded_images_folder_path.is_dir():
            shutil.rmtree(encoded_images_folder_path)
        encoded_images_folder_path.mkdir(parents = True, exist_ok = True)
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encode', 'step': '3', 'message': str(error)}

    # Check "ConvertedImages" Folder Exists And Is Not Empty:S4
    try:
        converted_images_folder_path_object = Path(converted_images_folder_path)
        if not (converted_images_folder_path_object.exists() and converted_images_folder_path_object.is_dir()):
            return {'status': 'ERROR', 'file_name': 'Image-Encode', 'step': '4', 'message': '"ConvertedImages" Folder Not Present'}
        if not any(converted_images_folder_path_object.iterdir()):
            return {'status': 'INFO', 'file_name': 'Image-Encode', 'step': '4', 'message': '"ConvertedImages" Folder Is Empty'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encode', 'step': '4', 'message': str(error)}

    # Fetch Converted Image Details From Database:S5
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_connection.row_factory = sqlite3.Row
            db_cursor = db_connection.cursor()
            converted_images_details_rows = db_cursor.execute('''
                SELECT cd.*
                FROM converted_images_details cd
                INNER JOIN raw_images_details rd ON cd.raw_file_id = rd.file_id
                WHERE rd.file_status = ?
                ORDER BY cd.id
            ''', ('Converted',)).fetchall()
        if not converted_images_details_rows:
            return {'status': 'INFO', 'file_name': 'Image-Encode', 'step': '5', 'message': 'No Converted Image Details Found In Database'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encode', 'step': '5', 'message': str(error)}

    # Convert Input Images To Base64 Text Files:S6
    try:
        print('')
        for converted_image_details_row in converted_images_details_rows:
            converted_image_file_path = Path(converted_image_details_row['file_path'])
            base64_text = base64.b64encode(converted_image_file_path.read_bytes()).decode('ascii')
            encoded_image_file_path = encoded_images_folder_path / f'{converted_image_file_path.stem}.txt'
            encoded_image_file_path.write_text(base64_text, encoding = 'ascii')
            print(f'"{converted_image_file_path.name}" File Encoded Into Base64')
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encode', 'step': '6', 'message': str(error)}

    # Fetch Encoded Image Details:S7
    try:
        encoded_image_file_path_list = sorted(
            file_path for file_path in encoded_images_folder_path.iterdir()
            if file_path.is_file()
        )
        for encoded_image_file_path in encoded_image_file_path_list:
            raw_file_id = encoded_image_file_path.stem
            file_name = encoded_image_file_path.name
            file_path = str(encoded_image_file_path)
            file_type = 'txt'
            file_size_bytes = encoded_image_file_path.stat().st_size
            file_hash = hashlib.md5(encoded_image_file_path.read_bytes()).hexdigest()
            encoded_images_details_nested_list.append(
                (raw_file_id, file_name, file_path, file_type, file_size_bytes, file_hash)
            )
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encode', 'step': '7', 'message': str(error)}

    # Insert Encoded Image Details Into Database:S8
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_cursor = db_connection.cursor()
            db_cursor.executemany('''
                INSERT INTO encoded_images_details (raw_file_id, file_name, file_path, file_type, file_size_bytes, file_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', encoded_images_details_nested_list)
            db_connection.commit()
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encode', 'step': '8', 'message': str(error)}

    # Update Raw Images Status To "Encoded":S9
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_cursor = db_connection.cursor()
            for converted_image_details_row in converted_images_details_rows:
                db_cursor.execute(
                    'UPDATE raw_images_details SET file_status = ? WHERE file_id = ?',
                    ('Encoded', converted_image_details_row['raw_file_id'])
                )
            db_connection.commit()
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Encode', 'step': '9', 'message': str(error)}

    # Return Success:S10
    return {'status': 'SUCCESS', 'file_name': 'Image-Encode', 'step': '10', 'message': 'All The Images Encoded Into Base64 Successfully'}