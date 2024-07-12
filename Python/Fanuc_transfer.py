import os
import shutil
from pathlib import Path

def get_user_input(prompt):
    return input(prompt).strip()

def file_exists(filepath):
    return os.path.exists(filepath)

def copy_file(src, dst):
    try:
        shutil.copy2(src, dst)
        print(f"Copied {src} to {dst}")
    except Exception as e:
        print(f"Failed to copy {src} to {dst}: {e}")

def copy_files(source_folder, dest_folder, files_to_copy, file_type):
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
    user_home = Path.home()
    documents_path = user_home / "Documents" / "Fanuc_transfer"
    
    #DIO, Registry, Poziční registry, ToolFrame a UserFrame
    static_files = ["DIOCFGSV.IO", "NUMREG.VR", "POSREG.VR", "SYSFRAME.SV", "FRAME.VR"]
    
    while True:
        last_folder_name = get_user_input("Enter the last folder name for source: ")
        source_folder = documents_path / last_folder_name
        
        if not os.path.isdir(source_folder):
            retry_or_quit = get_user_input(f"Source folder does not exist: {source_folder}. Type 'r' to enter folder name again or 'q' to exit: ").lower()
            if retry_or_quit == 'q':
                get_user_input("Press Enter to exit...")
                return
            elif retry_or_quit == 'r':
                continue
            else:
                print("Invalid input. Please type 'retry' or 'quit'.")
                continue
        else:
            break
    
    # Check if all static files are present in the source folder
    missing_files = [file for file in static_files if not file_exists(os.path.join(source_folder, file))]
    if missing_files:
        print(f"The following static files are missing in the source folder: {', '.join(missing_files)}")
        continue_anyway = get_user_input("Do you want to continue anyway? (y/n): ").lower()
        if continue_anyway != 'y':
            get_user_input("Press Enter to exit...")
            return

    dest_folder_name = get_user_input("Enter the last folder name for destination: ")
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

    # Copy static files
    copy_files(source_folder, dest_folder, static_files, "Static")

    # Handle .tp files
    tp_files = [f for f in os.listdir(source_folder) if f.endswith('.tp')]
    
    if not tp_files:
        print("No .tp files found in the source folder.")
    else:
        copy_all_tp_files = get_user_input("Do you want to copy all .tp files? (y/n): ").lower()
        
        if copy_all_tp_files == 'y':
            copy_files(source_folder, dest_folder, tp_files, ".tp")
        else:
            for tp_file in tp_files:
                copy_tp_file = get_user_input(f"Do you want to copy {tp_file}? (y/n): ").lower()
                if copy_tp_file == 'y':
                    copy_files(source_folder, dest_folder, [tp_file], ".tp")

    # Final message indicating successful completion
    print("File copying process completed successfully.")
    get_user_input("Press Enter to exit...")

if __name__ == "__main__":
    main()
