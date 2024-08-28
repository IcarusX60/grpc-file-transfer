# file_client.py
import grpc
import filetransfer_pb2
import filetransfer_pb2_grpc
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from file_client_utils import ChannelStatus, print_status, send_files_to_channel

NUM_CHANNELS = 6
CHANNEL_NAMES = [f"Channel {i+1}" for i in range(NUM_CHANNELS)]

def run():
    folder_path = os.path.join(os.getcwd(), "random_files_folder")
    files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
    num_files = len(files)
    
    if num_files == 0:
        print("No files found in the directory.")
        return

    num_files_per_channel = num_files // NUM_CHANNELS
    extra_files = num_files % NUM_CHANNELS

    channels = [grpc.insecure_channel('10.105.197.101:50051', options=[('grpc.max_send_message_length', 100 * 1024 * 1024)]) for _ in range(NUM_CHANNELS)]

    file_chunks = []
    start = 0
    for i in range(NUM_CHANNELS):
        end = start + num_files_per_channel + (1 if i < extra_files else 0)
        file_chunks.append(files[start:end])
        start = end

    channel_statuses = {name: ChannelStatus() for name in CHANNEL_NAMES}
    lock = Lock()

    with ThreadPoolExecutor(max_workers=NUM_CHANNELS) as executor:
        futures = [executor.submit(send_files_to_channel, CHANNEL_NAMES[i], channels[i], file_chunks[i], channel_statuses, lock) for i in range(NUM_CHANNELS)]
        for future in futures:
            future.result()

    print("\nTransfer Complete. Final Statistics:")
    for name, status in channel_statuses.items():
        files_sent, total_size, elapsed_time, bandwidth = status.get_stats()
        print(f"\n{name}:")
        print(f"  Files sent: {files_sent}")
        print(f"  Total size: {total_size / (1024*1024):.2f} MB")
        print(f"  Time taken: {elapsed_time:.2f} seconds")
        print(f"  Bandwidth: {bandwidth / (1024*1024):.2f} MB/s")
        if status.errors:
            print("  Errors:")
            for error in status.errors:
                print(f"    - {error}")

    for channel in channels:
        channel.close()

if __name__ == '__main__':
    run()
