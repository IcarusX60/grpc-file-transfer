# file_client_multiple.py
import grpc
import filetransfer_pb2
import filetransfer_pb2_grpc
import os
import time
import csv
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from file_client_utils import ChannelStatus, print_status, send_files_to_channel, log_to_csv

NUM_CHANNELS = 3
CHANNEL_NAMES = [f"Channel {i+1}" for i in range(NUM_CHANNELS)]
NUM_ITERATIONS = 2  # Define the number of times to send the same data

def run():
    folder_path = os.path.join(os.getcwd(), "random_files_folder")
    file_groups = ["small", "medium", "large"]

    log_data = []

    for iteration in range(1, NUM_ITERATIONS + 1):
        for group in file_groups:
            group_folder_path = os.path.join(folder_path, group)
            files = [os.path.join(group_folder_path, file) for file in os.listdir(group_folder_path) if os.path.isfile(os.path.join(group_folder_path, file))]
            num_files = len(files)
            
            if num_files == 0:
                print(f"No files found in the {group} directory.")
                continue

            for num_channels in range(1, NUM_CHANNELS + 1):
                channels = [grpc.insecure_channel('192.168.0.106:50051', options=[('grpc.max_send_message_length', 100 * 1024 * 1024)]) for _ in range(num_channels)]

                file_chunks = []
                num_files_per_channel = num_files // num_channels
                extra_files = num_files % num_channels
                start = 0
                for i in range(num_channels):
                    end = start + num_files_per_channel + (1 if i < extra_files else 0)
                    file_chunks.append(files[start:end])
                    start = end

                channel_statuses = {CHANNEL_NAMES[i]: ChannelStatus() for i in range(num_channels)}
                lock = Lock()

                with ThreadPoolExecutor(max_workers=num_channels) as executor:
                    futures = [executor.submit(send_files_to_channel, CHANNEL_NAMES[i], channels[i], file_chunks[i], channel_statuses, lock) for i in range(num_channels)]
                    for future in futures:
                        future.result()

                # Log the results for this iteration and number of channels
                for i in range(num_channels):
                    name = CHANNEL_NAMES[i]
                    status = channel_statuses[name]
                    files_sent, total_size, elapsed_time, bandwidth = status.get_stats()
                    log_data.append({
                        "Iteration": iteration,
                        "File Group": group,
                        "Num Channels": num_channels,
                        "Channel": name,
                        "Files Sent": files_sent,
                        "Total Size (MB)": total_size / (1024 * 1024),
                        "Time Taken (s)": elapsed_time,
                        "Bandwidth (MB/s)": bandwidth / (1024 * 1024)
                    })

                for channel in channels:
                    channel.close()

    log_to_csv(log_data)
    print("\nTransfer Complete. Log saved to throughput_log.csv.")

if __name__ == '__main__':
    run()
