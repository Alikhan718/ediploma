import os
import shutil
import stat


def removeFolder(folder_path):
    print()

    try:
        # List all files in the folder
        files = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), folder_path))
        print(files)
        # Iterate over the files and delete each one
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)

            os.remove(file_path)
            print(f"File '{folder_path}' has been successfully deleted.")

        print(f"All files in the folder '{folder_path}' have been deleted.")
    except OSError as e:
        print(f"Error: {e}")

removeFolder('storage/archives')
removeFolder('storage/jsons/1')
removeFolder('storage/images/1')