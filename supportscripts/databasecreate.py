# Define "database_create" Function
def database_create(database_file_path: str) -> dict[str, str]:
    # Importing Python Modules:S1
    try:
        from pathlib import Path
        import sqlite3
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Database-Create', 'step': '1', 'message': str(error)}

    # Check Database File Already Exists:S2
    try:
        database_file_path_object = Path(database_file_path)
        if database_file_path_object.exists() and database_file_path_object.is_file():
            return {'status': 'INFO', 'file_name': 'Database-Create', 'step': '2', 'message': 'Database Already Exists'}
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Database-Create', 'step': '2', 'message': str(error)}

    # Create "raw_images_details" Table:S3
    try:
        raw_images_details_table_creation_query = '''
            CREATE TABLE IF NOT EXISTS raw_images_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                file_id TEXT NOT NULL UNIQUE CHECK(LENGTH(file_id) = 6),
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL DEFAULT 'jpg' CHECK(file_type IN ('heic', 'jpg', 'jpeg', 'png')),
                file_size_bytes BIGINT NOT NULL,
                file_hash TEXT NOT NULL,
                file_status TEXT NOT NULL DEFAULT 'Original' CHECK(file_status IN ('Original', 'Converted', 'Encoded', 'Encrypted'))
            )
        '''
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_cursor = db_connection.cursor()
            db_cursor.execute(raw_images_details_table_creation_query)
            db_connection.commit()
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Database-Create', 'step': '3', 'message': str(error)}

    # Create "converted_images_details" Table:S4
    try:
        converted_images_details_table_creation_query = '''
            CREATE TABLE IF NOT EXISTS converted_images_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                raw_file_id TEXT NOT NULL CHECK(LENGTH(raw_file_id) = 6),
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL DEFAULT 'jpg' CHECK(file_type = 'jpg'),
                file_size_bytes BIGINT NOT NULL,
                file_hash TEXT NOT NULL,
                FOREIGN KEY (raw_file_id) REFERENCES raw_images_details(file_id)
            )
        '''
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_cursor = db_connection.cursor()
            db_cursor.execute('PRAGMA foreign_keys = ON')
            db_cursor.execute(converted_images_details_table_creation_query)
            db_connection.commit()
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Database-Create', 'step': '4', 'message': str(error)}

    # Create "encoded_images_details" Table:S5
    try:
        encoded_images_details_table_creation_query = '''
            CREATE TABLE IF NOT EXISTS encoded_images_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                raw_file_id TEXT NOT NULL CHECK(LENGTH(raw_file_id) = 6),
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL DEFAULT 'txt' CHECK(file_type = 'txt'),
                file_size_bytes BIGINT NOT NULL,
                file_hash TEXT NOT NULL,
                FOREIGN KEY (raw_file_id) REFERENCES raw_images_details(file_id)
            )
        '''
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_cursor = db_connection.cursor()
            db_cursor.execute('PRAGMA foreign_keys = ON')
            db_cursor.execute(encoded_images_details_table_creation_query)
            db_connection.commit()
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Database-Create', 'step': '5', 'message': str(error)}

    # Create "encrypted_images_details" Table:S6
    try:
        encrypted_images_details_table_creation_query = '''
            CREATE TABLE IF NOT EXISTS encrypted_images_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                raw_file_id TEXT NOT NULL CHECK(LENGTH(raw_file_id) = 6),
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size_bytes BIGINT NOT NULL,
                file_hash TEXT NOT NULL,
                FOREIGN KEY (raw_file_id) REFERENCES raw_images_details(file_id)
            )
        '''
        with sqlite3.connect(str(database_file_path_object)) as db_connection:
            db_cursor = db_connection.cursor()
            db_cursor.execute('PRAGMA foreign_keys = ON')
            db_cursor.execute(encrypted_images_details_table_creation_query)
            db_connection.commit()
    except Exception as error:
        return {'status': 'ERROR', 'file_name': 'Database-Create', 'step': '6', 'message': str(error)}

    # Return Success:S7
    return {'status': 'SUCCESS', 'file_name': 'Database-Create', 'step': '7', 'message': 'Database Created Successfully'}