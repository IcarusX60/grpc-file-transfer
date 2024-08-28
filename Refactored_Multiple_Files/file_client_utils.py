# file_client_utils.py
import csv
import grpc
import filetransfer_pb2
import filetransfer_pb2_grpc
import os
import time
from threading import Lock
import sys

class ChannelStatus:
    def __init__(self):
        self.current_file = "Waiting..."
        self.files_sent = 0
        self.total_size = 0
        self.start_time = time.time()
        self.errors = []

    def update(self, filename, size):
        self.current_file = filename
        self.files_sent += 1
        self.total_size += size

    def add_error(self, error):
        self.errors.append(error)

    def get_stats(self):
        elapsed_time = time.time() - self.start_time
        bandwidth = self.total_size / elapsed_time if elapsed_time > 0 else 0
        return (self.files_sent, self.total_size, elapsed_time, bandwidth)

def print_status(channel_statuses, lock):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Channel Status:")
    for name, status in channel_statuses.items():
        print(f"{name}: {status.current_file}")
    print("\nErrors:")
    for name, status in channel_statuses.items():
        for error in status.errors:
            print(f"{name}: {error}")
    sys.stdout.flush()

def send_files_to_channel(channel_name, channel, files, channel_statuses, lock):
    stub = filetransfer_pb2_grpc.FileTransferStub(channel)
    for filename in files:
        if not os.path.exists(filename):
            error = f"Error: File {filename} does not exist."
            with lock:
                channel_statuses[channel_name].add_error(error)
                print_status(channel_statuses, lock)
            continue
        
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            file_size = len(content)
            with lock:
                channel_statuses[channel_name].update(os.path.basename(filename), file_size)
                print_status(channel_statuses, lock)
            response = stub.SendFile(filetransfer_pb2.FileRequest(filename=os.path.basename(filename), content=content))
        except grpc.RpcError as e:
            error = f"RPC error while sending {filename}: {e}"
            with lock:
                channel_statuses[channel_name].add_error(error)
                print_status(channel_statuses, lock)
        except Exception as e:
            error = f"Unexpected error while sending {filename}: {e}"
            with lock:
                channel_statuses[channel_name].add_error(error)
                print_status(channel_statuses, lock)

def log_to_csv(log_data, filename="throughput_log.csv"):
    # Save log data to a CSV file
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["Iteration", "File Group", "Num Channels", "Channel", "Files Sent", "Total Size (MB)", "Time Taken (s)", "Bandwidth (MB/s)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in log_data:
            writer.writerow(data)
