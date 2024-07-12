import os
import shutil

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
    base_path = "C:/Users/PetrJanů/Documents/Fanuc_transfer/"
    static_files = ["static1.txt", "static2.txt", "static3.txt", "static4.txt", "static5.txt"]
    
    last_folder_name = get_user_input("Enter the last folder name for source: ")
    source_folder = os.path.join(base_path, last_folder_name)
    
    if not os.path.isdir(source_folder):
        print(f"Source folder does not exist: {source_folder}")
        return

    dest_folder_name = get_user_input("Enter the last folder name for destination: ")
    dest_folder = os.path.join(base_path, dest_folder_name)
    
    if not os.path.isdir(dest_folder):
        print(f"Destination folder does not exist: {dest_folder}")
        return

    # Copy static files
    copy_files(source_folder, dest_folder, static_files, "Static")

    # Handle .tp files
    tp_files = [f for f in os.listdir(source_folder) if f.endswith('.tp')]
    
    if not tp_files:
        print("No .tp files found in the source folder.")
        return

    copy_all_tp_files = get_user_input("Do you want to copy all .tp files? (y/n): ").lower()
    
    if copy_all_tp_files == 'y':
        copy_files(source_folder, dest_folder, tp_files, ".tp")
    else:
        for tp_file in tp_files:
            copy_tp_file = get_user_input(f"Do you want to copy {tp_file}? (y/n): ").lower()
            if copy_tp_file == 'y':
                copy_files(source_folder, dest_folder, [tp_file], ".tp")

if __name__ == "__main__":
    main()
