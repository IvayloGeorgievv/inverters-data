import os


def delete_files_in_folder(folder_path):
    try:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        print(f"Deleted all files in {folder_path}")
    except Exception as e:
        print(f"Error cleaning folder {folder_path}: {e}")