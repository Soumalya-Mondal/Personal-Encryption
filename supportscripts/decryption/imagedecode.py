# Define "image_decode" Function
def image_decode(database_file_path: str) -> dict[str, str]:
    # Importing Python Modules:S1
    try:
        from pathlib import Path
        import shutil
        import base64
        import sqlite3
        import hashlib
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '1', 'message': str(error)}

    # Define Folder Path:S2
    try:
        parent_folder_path = Path.cwd()
        database_file_path_object = Path(database_file_path)
        tmp_folder_path = Path(parent_folder_path) / 'tmp'
        encoded_images_folder_path = Path(tmp_folder_path) / 'EncodedImages'
        original_images_folder_path = Path(tmp_folder_path) / 'OriginalImages'
        images_folder_path_object = Path(parent_folder_path) / 'images'
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '2', 'message': str(error)}

    # Recreate "OriginalImages" Folder:S3
    try:
        if original_images_folder_path.exists() and original_images_folder_path.is_dir():
            shutil.rmtree(original_images_folder_path)
        original_images_folder_path.mkdir(parents = True, exist_ok = True)
        images_folder_path_object.mkdir(parents = True, exist_ok = True)
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '3', 'message': str(error)}

    # Creating Path Object And Check If "EncodedImages" Folder Is Present:S4
    try:
        if not (encoded_images_folder_path.exists() and encoded_images_folder_path.is_dir()):
            return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '4', 'message': f'"{encoded_images_folder_path.name}" Folder Not Present'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '4', 'message': str(error)}

    # Create Encoded Text File Path List:S5
    try:
        encoded_text_file_path_list = sorted(
            file_path for file_path in encoded_images_folder_path.iterdir()
            if file_path.is_file() and file_path.suffix.lower() == '.txt'
        )
        if not encoded_text_file_path_list:
            raise ValueError(f'No Encoded Text Files Found In "{encoded_images_folder_path.name}" Folder')
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '5', 'message': str(error)}

    # Convert Base64 Text Files To Original Images:S6
    try:
        print('')
        for encoded_text_file_path in encoded_text_file_path_list:
            image_bytes = base64.b64decode(encoded_text_file_path.read_bytes(), validate = True)
            original_image_file_path = original_images_folder_path / f'{encoded_text_file_path.stem}.jpg'
            original_image_file_path.write_bytes(image_bytes)
            print(f'"{encoded_text_file_path.name}" Has Been Decoded From Base64')
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '6', 'message': str(error)}

    # Create Original Image File Details Dictionary From "OriginalImages" Folder:S7
    try:
        original_image_file_details_dict = {
            file_path.name: hashlib.md5(file_path.read_bytes()).hexdigest()
            for file_path in original_images_folder_path.iterdir()
            if file_path.is_file() and file_path.suffix.lower() == '.jpg'
        }
        if not original_image_file_details_dict:
            return {'status': 'INFO', 'file_name': 'Image-Decode', 'step': '7', 'message': 'No Original Image Files Found In "OriginalImages" Folder'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '7', 'message': str(error)}

    # Compare Original Image Hashes With "converted_images_details" Table:S8
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_connection.row_factory = sqlite3.Row
            db_cursor = db_connection.cursor()
            for original_image_file_name, original_image_file_hash in original_image_file_details_dict.items():
                converted_image_details_row = db_cursor.execute(
                    'SELECT file_hash FROM converted_images_details WHERE file_name = ?',
                    (original_image_file_name,)
                ).fetchone()
                if not converted_image_details_row:
                    return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '8', 'message': f'No Converted Image Details Found For "{original_image_file_name}"'}
                converted_file_hash = converted_image_details_row['file_hash']
                if original_image_file_hash != converted_file_hash:
                    return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '8', 'message': f'Hash Mismatch For "{original_image_file_name}"'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '8', 'message': str(error)}

    # Copy Renamed Original Images To "images" Folder And Delete "tmp" Folder:S9
    try:
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_connection.row_factory = sqlite3.Row
            db_cursor = db_connection.cursor()
            for original_image_file_name in original_image_file_details_dict.keys():
                converted_image_details_row = db_cursor.execute('''
                    SELECT rid.file_name
                    FROM converted_images_details cid
                    INNER JOIN raw_images_details rid ON cid.raw_file_id = rid.file_id
                    WHERE cid.file_name = ?
                ''', (original_image_file_name,)).fetchone()
                if not converted_image_details_row:
                    return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '9', 'message': f'No Raw Image Details Found For "{original_image_file_name}"'}
                raw_file_name = converted_image_details_row['file_name']
                raw_file_stem = Path(raw_file_name).stem
                shutil.copy(
                    str(original_images_folder_path / original_image_file_name),
                    str(images_folder_path_object / f'{raw_file_stem}.jpg')
                )
        shutil.rmtree(tmp_folder_path)
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '9', 'message': str(error)}

    # Return Success:S10
    return {'status': 'SUCCESS', 'file_name': 'Image-Decode', 'step': '10', 'message': 'All The Images Decoded And Copied To "images" Folder Successfully'}
