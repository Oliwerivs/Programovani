import os
import shutil
from pathlib import Path

def is_valid_input(user_input, allowed_characters):
    return all(char in allowed_characters for char in user_input)

def get_user_input(prompt,allowed_characters = "ynb0123456789"):
    while True:
        user_input = input(prompt).strip().lower()
        if allowed_characters:
            if is_valid_input(user_input, allowed_characters):
                return user_input
            else:
                print(f"Invalid input. Please use only the allowed characters: {''.join(allowed_characters)}")
        else:
            return user_input

def list_folders_in_directory(directory):
    return [f.name for f in directory.iterdir() if f.is_dir()]

def display_folders_with_index(folders):
    print("Available folders:")
    for index, folder in enumerate(folders, start=1):
        print(f"{index}. {folder}")
        
def create_output_folder(base_path, base_name="RG_TRANSFER"):
    output_path = base_path / base_name
    counter = 1
    
    while output_path.exists():
        overwrite = get_user_input(f"{output_path} already exists. Overwrite? (y/n): ").lower()
        if overwrite == 'y':
            # If the user wants to overwrite, break the loop and return the existing path
            break
        else:
            # If no overwrite, create a new folder with an incrementing number
            output_path = base_path / f"{base_name}_{counter}"
            counter += 1
    
    if not output_path.exists():
        try:
            output_path.mkdir(parents=True)
            print(f"Created output folder: {output_path}")
        except Exception as e:
            print(f"Failed to create output folder: {e}")
            get_user_input("Press Enter to exit...")
            exit()
    
    return output_path

def file_exists(filepath):
    return os.path.exists(filepath)

def copy_file(src, dst):
    try:
        shutil.copy2(src, dst)
        print(f"Copied {src} to {dst}")
    except Exception as e:
        print(f"Failed to copy {src} to {dst}: {e}")

def copy_files(source_folder, dest_folder, files_to_copy, subfolder_name=None):
    if subfolder_name:
        dest_folder = dest_folder / subfolder_name
        if not dest_folder.exists():
            dest_folder.mkdir(parents=True)
    
    for file_name in files_to_copy:
        src_file = os.path.join(source_folder, file_name)
        dest_file = os.path.join(dest_folder, file_name)

        if file_exists(dest_file):
            overwrite = get_user_input(f"{file_name} already exists. Overwrite? (y/n): ").lower()
            if overwrite != 'y':
                print(f"Skipped {file_name}")
                continue

        copy_file(src_file, dest_file)

def main():
    #user_home = Path.home()
    # Set script_location to the folder where the script is located
    script_location = Path(__file__).parent
    documents_path = script_location
    #documents_path = user_home / "Documents" / "Fanuc_transfer"
    
    #DIO, Registry, Poziční registry, ToolFrame a UserFrame
    static_files = ["DIOCFGSV.IO", "NUMREG.VR", "POSREG.VR", "SYSFRAME.SV", "FRAMEVAR.VR"]
    
    #while True:
    #    last_folder_name = get_user_input("Enter the last folder name for source: ")
     #   source_folder = documents_path / last_folder_name
      #  
       # if not os.path.isdir(source_folder):
       #     retry_or_quit = get_user_input(f"Source folder does not exist: {source_folder}. Type 'r' to enter folder name again or 'q' to exit: ").lower()
       #     if retry_or_quit == 'q':
       #         get_user_input("Press Enter to exit...")
       #         return
       #     elif retry_or_quit == 'r':
       #         continue
       #     else:
       #         print("Invalid input. Please type 'retry' or 'quit'.")
       #         continue
       # else:
        #    break
    
    folders = list_folders_in_directory(script_location)
    
    if not folders:
        print("No folders found in the script's directory.")
        get_user_input("Press Enter to exit...")
        return
    
    display_folders_with_index(folders)
    
    while True:
        try:
            selected_index = int(get_user_input("Select a folder number to use as the source folder: "))
            if 1 <= selected_index <= len(folders):
                source_folder = script_location / folders[selected_index - 1]
                break
            else:
                print("Invalid number. Please select a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Confirm selected folder
    print(f"Selected source folder: {source_folder}")
    
    # Check if all static files are present in the source folder
    missing_files = [file for file in static_files if not file_exists(os.path.join(source_folder, file))]
    if missing_files:
        print(f"The following static files are missing in the source folder: {', '.join(missing_files)}")
        continue_anyway = get_user_input("Do you want to continue anyway? (y/n): ").lower()
        if continue_anyway != 'y':
            get_user_input("Press Enter to exit...")
            return

    #dest_folder_name = get_user_input("Enter the last folder name for destination: ")
    dest_folder_name = create_output_folder(script_location)
    dest_folder = documents_path / dest_folder_name
    
    if not os.path.isdir(dest_folder):
        create_dest_folder = get_user_input(f"Destination folder does not exist: {dest_folder}. Do you want to create it? (y/n): ").lower()
        if create_dest_folder == 'y':
            try:
                os.makedirs(dest_folder)
                print(f"Created destination folder: {dest_folder}")
            except Exception as e:
                print(f"Failed to create destination folder: {e}")
                get_user_input("Press Enter to exit...")
                return
        else:
            print("Destination folder was not created. Exiting...")
            get_user_input("Press Enter to exit...")
            return


    # Create output folder
    
    
    # Copy static files
    copy_files(source_folder, dest_folder, static_files, "CONF")

    # Handle .tp files
    tp_files = [f for f in os.listdir(source_folder) if f.endswith('.TP')]
    
    if not tp_files:
        print("No .tp files found in the source folder.")
    else:
        copy_tp_files = get_user_input("Do you want to copy .tp files? (y/n): ").lower()
        if copy_tp_files == 'y':
            copy_all_tp_files = get_user_input("Do you want to copy all .tp files? (y/n): ").lower()
        
            if copy_all_tp_files == 'y':
                copy_files(source_folder, dest_folder, tp_files, ".tp")
        
        
            else:
                for tp_file in tp_files:
                    copy_tp_file = get_user_input(f"Do you want to copy {tp_file}?  Hit \"B\" to Break. (y/n/b): ").lower()
                    if copy_tp_file == 'y':
                        copy_files(source_folder, dest_folder, [tp_file], ".tp")
                    elif copy_tp_file == 'b':
                        break

    # Final message indicating successful completion
    print("File copying process completed successfully.")
    get_user_input("Press Enter to exit...")

if __name__ == "__main__":
    main()
