import os
import random
import shutil

def create_random_files_in_folder(base_folder_path, group_name, min_files, max_files, size_range):
    # Create the specific group folder path
    folder_path = os.path.join(base_folder_path, group_name)
    
    # Delete the folder if it exists
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Deleted existing folder: {folder_path}")
    
    # Create the folder
    os.makedirs(folder_path, exist_ok=True)
    print(f"Created new folder: {folder_path}")
    
    # Determine the number of files to create
    num_files = random.randint(min_files, max_files)
    print(f"Generating {num_files} files in '{group_name}' with random sizes between {size_range[0]} MB and {size_range[1]} MB.")
    
    for i in range(num_files):
        # Generate random file size within the specified range
        file_size_mb = random.randint(size_range[0], size_range[1])
        file_size_bytes = file_size_mb * 1024 * 1024  # Convert MB to bytes
        
        file_path = os.path.join(folder_path, f"file_{i}.dat")
        
        # Use `dd` to create a file with the specified size
        dd_cmd = f"dd if=/dev/zero of={file_path} bs=1M count={file_size_mb}"
        os.system(dd_cmd)
        
        print(f"Created file: {file_path} with size {file_size_mb} MB")
    
    print(f"File generation complete for {group_name}.")

# Define the path for the base folder to be created
current_dir = os.getcwd()
base_folder_name = "random_files_folder"
base_folder_path = os.path.join(current_dir, base_folder_name)

# Define size ranges for each group
small_size_range = (5, 10)
medium_size_range = (11, 15)
large_size_range = (16, 20)

# Define the number of files range for each group
min_files = 6
max_files = 12

# Create folders and generate random files for each group
create_random_files_in_folder(base_folder_path, 'small', min_files, max_files, small_size_range)
create_random_files_in_folder(base_folder_path, 'medium', min_files, max_files, medium_size_range)
create_random_files_in_folder(base_folder_path, 'large', min_files, max_files, large_size_range)
