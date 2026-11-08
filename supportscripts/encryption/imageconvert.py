# Define "image_convert" Function
def image_convert(database_file_path: str) -> dict[str, str]:
    # Define Constant
    converted_images_details_nested_list = []

    # Importing Python Modules:S1
    try:
        from pathlib import Path
        import shutil
        import subprocess
        import sqlite3
        import hashlib
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Convert', 'step': '1', 'message': str(error)}

    # Define Folder Path And Database File Path Object:S2
    try:
        parent_folder_path = Path.cwd()
        database_file_path_object = Path(database_file_path)
        tmp_folder_path = Path(parent_folder_path) / 'tmp'
        converted_images_folder_path = Path(tmp_folder_path) / 'ConvertedImages'
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Convert', 'step': '2', 'message': str(error)}

    # Recreate "tmp" And "ConvertedImages" Folders:S3
    try:
        if ((tmp_folder_path.exists()) and (tmp_folder_path.is_dir())):
            shutil.rmtree(tmp_folder_path)
        tmp_folder_path.mkdir(parents = True, exist_ok = True)
        converted_images_folder_path.mkdir(parents = True, exist_ok = True)
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Convert', 'step': '3', 'message': str(error)}

    # Fetch Raw Image Details From Database:S4
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_connection.row_factory = sqlite3.Row
            db_cursor = db_connection.cursor()
            raw_images_details_rows = db_cursor.execute(
                'SELECT file_id, file_path FROM raw_images_details WHERE file_status = ? ORDER BY id',
                ('Original',)
            ).fetchall()
        if not raw_images_details_rows:
            return {'status': 'INFO', 'file_name': 'Image-Convert', 'step': '4', 'message': 'No Raw Image Details Found In Database'}
        input_images_file_path_list = [Path(row['file_path']) for row in raw_images_details_rows]
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Convert', 'step': '4', 'message': str(error)}

    # Convert Input Images To "*.JPG" Format:S5
    try:
        for image_number, input_image_file_path in enumerate(input_images_file_path_list, start = 1):
            converted_image_file_path = Path(converted_images_folder_path) / f'img{image_number:05d}.jpg'
            ffmpeg_command = [
                'ffmpeg',
                '-y',
                '-i', str(input_image_file_path),
                '-q:v', '1',
                '-qmin', '1',
                '-qmax', '1',
                '-pix_fmt', 'yuvj444p',
                str(converted_image_file_path)
            ]
            subprocess.run(ffmpeg_command, check = True, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
            print(f'{image_number:05d}-> "{input_image_file_path.name}" Converted To "{converted_image_file_path.name}"')
    except subprocess.CalledProcessError as error:
        return {'status': 'ERROR', 'file_name': 'Image-Convert', 'step': '5', 'message': f'FFmpeg Failed To Convert "{input_image_file_path.name}"'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Convert', 'step': '5', 'message': str(error)}

    # Fetch Converted Image Details:S6
    try:
        converted_image_file_path_list = sorted(
            file_path for file_path in converted_images_folder_path.iterdir()
            if file_path.is_file()
        )
        for image_number, converted_image_file_path in enumerate(converted_image_file_path_list, start = 1):
            raw_file_id = raw_images_details_rows[image_number - 1]['file_id']
            file_name = converted_image_file_path.name
            file_path = str(converted_image_file_path)
            file_type = 'jpg'
            file_size_bytes = converted_image_file_path.stat().st_size
            file_hash = hashlib.md5(converted_image_file_path.read_bytes()).hexdigest()
            converted_images_details_nested_list.append(
                (raw_file_id, file_name, file_path, file_type, file_size_bytes, file_hash)
            )
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Convert', 'step': '6', 'message': str(error)}

    # Insert Converted Image Details Into Database:S7
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_cursor = db_connection.cursor()
            db_cursor.executemany('''
                INSERT INTO converted_images_details (raw_file_id, file_name, file_path, file_type, file_size_bytes, file_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', converted_images_details_nested_list)
            db_connection.commit()
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Convert', 'step': '7', 'message': str(error)}

    # Update Raw Images Status To "Converted":S8
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_cursor = db_connection.cursor()
            for raw_image_details_row in raw_images_details_rows:
                db_cursor.execute(
                    'UPDATE raw_images_details SET file_status = ? WHERE file_id = ?',
                    ('Converted', raw_image_details_row['file_id'])
                )
            db_connection.commit()
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Convert', 'step': '8', 'message': str(error)}

    # Return Success:S9
    return {'status': 'SUCCESS', 'file_name': 'Image-Convert', 'step': '9', 'message': 'All The Images Converted To JPG Successfully'}