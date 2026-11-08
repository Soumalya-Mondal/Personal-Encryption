# Define "image_decode" Function
def image_decode(images_folder_path: str) -> dict[str, str]:
    # Importing Python Modules:S1
    try:
        from pathlib import Path
        import shutil
        import base64
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '1', 'message': str(error)}

    # Define Folder Path:S2
    try:
        parent_folder_path = Path.cwd()
        tmp_folder_path = Path(parent_folder_path) / 'tmp'
        encoded_images_folder_path = Path(tmp_folder_path) / 'EncodedImages'
        original_images_folder_path = Path(tmp_folder_path) / 'OriginalImages'
        images_folder_path_object = Path(images_folder_path)
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
        for decoded_number, encoded_text_file_path in enumerate(encoded_text_file_path_list, start = 1):
            image_bytes = base64.b64decode(encoded_text_file_path.read_bytes(), validate = True)
            original_image_file_path = original_images_folder_path / f'{encoded_text_file_path.stem}.jpg'
            original_image_file_path.write_bytes(image_bytes)
            print(f'{decoded_number:05d}-> "{encoded_text_file_path.name}" Has Been Decoded From Base64')
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '6', 'message': str(error)}

    # Copy Original Images To "images" Folder And Delete "tmp" Folder:S7
    try:
        for original_image_file_path in sorted(original_images_folder_path.iterdir()):
            if original_image_file_path.is_file():
                shutil.copy(str(original_image_file_path), str(images_folder_path_object))
        shutil.rmtree(tmp_folder_path)
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Image-Decode', 'step': '7', 'message': str(error)}

    # Return Success:S8
    return {'status': 'SUCCESS', 'file_name': 'Image-Decode', 'step': '8', 'message': 'All The Images Decoded And Copied To "images" Folder Successfully'}
