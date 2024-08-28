import os
import random
import shutil

def create_random_files_in_folder(folder_path, min_files=100, max_files=200, min_size_mb=15, max_size_mb=25):
    # Delete the folder if it exists
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Deleted existing folder: {folder_path}")
    
    # Create the folder
    os.makedirs(folder_path, exist_ok=True)
    print(f"Created new folder: {folder_path}")
    
    # Determine the number of files to create
    num_files = random.randint(min_files, max_files)
    print(f"Generating {num_files} files with random sizes between {min_size_mb} MB and {max_size_mb} MB.")
    
    for i in range(num_files):
        # Generate random file size
        file_size_mb = random.randint(min_size_mb, max_size_mb)
        file_size_bytes = file_size_mb * 1024 * 1024  # Convert MB to bytes
        
        file_path = os.path.join(folder_path, f"file_{i}.dat")
        dd_cmd = f"dd if=/dev/zero of={file_path} bs=1M count={file_size_mb}"
        os.system(dd_cmd)
        
        print(f"Created file: {file_path} with size {file_size_mb} MB")
    
    print("File generation complete.")

# Define the path for the folder to be created
current_dir = os.getcwd()
folder_name = "random_files_folder"
folder_path = os.path.join(current_dir, folder_name)

# Create the folder and generate random files
create_random_files_in_folder(folder_path)
