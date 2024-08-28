import grpc
import filetransfer_pb2
import filetransfer_pb2_grpc
import os
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import sys

NUM_CHANNELS = 6
CHANNEL_NAMES = [f"Channel {i+1}" for i in range(NUM_CHANNELS)]

class ChannelStatus:
    def __init__(self):
        self.current_file = "Waiting..."
        self.files_sent = 0
        self.total_size = 0
        self.start_time = time.time()
        self.total_elapsed_time = 0  # Total time including reading and transmission
        self.transmission_time = 0   # Pure transmission time only
        self.errors = []

    def update(self, filename, size, total_duration, transmission_duration):
        self.current_file = filename
        self.files_sent += 1
        self.total_size += size
        self.total_elapsed_time += total_duration  # Include total duration (reading + transmission)
        self.transmission_time += transmission_duration  # Include only transmission duration

    def add_error(self, error):
        self.errors.append(error)

    def get_stats(self):
        total_bandwidth = self.total_size / self.total_elapsed_time if self.total_elapsed_time > 0 else 0
        transmission_bandwidth = self.total_size / self.transmission_time if self.transmission_time > 0 else 0
        return (self.files_sent, self.total_size, self.total_elapsed_time, self.transmission_time, total_bandwidth, transmission_bandwidth)

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
            # Start timing total duration (reading + transmission)
            total_start_time = time.time()

            # Read the file from disk
            with open(filename, 'rb') as f:
                content = f.read()

            file_size = len(content)
            
            # Start timing the transmission duration only
            transmission_start_time = time.time()

            # gRPC call to send the file
            response = stub.SendFile(filetransfer_pb2.FileRequest(filename=os.path.basename(filename), content=content))
            
            # End timing the transmission duration
            transmission_duration = time.time() - transmission_start_time

            # End timing total duration
            total_duration = time.time() - total_start_time

            with lock:
                channel_statuses[channel_name].update(os.path.basename(filename), file_size, total_duration, transmission_duration)
                print_status(channel_statuses, lock)

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

def run():
    folder_path = os.path.join(os.getcwd(), "random_files_folder")
    files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
    num_files = len(files)
    
    if num_files == 0:
        print("No files found in the directory.")
        return

    num_files_per_channel = num_files // NUM_CHANNELS
    extra_files = num_files % NUM_CHANNELS

    channels = [grpc.insecure_channel('192.168.0.106:50051', options=[('grpc.max_send_message_length', 100 * 1024 * 1024)]) for _ in range(NUM_CHANNELS)]

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
        files_sent, total_size, total_elapsed_time, transmission_time, total_bandwidth, transmission_bandwidth = status.get_stats()
        print(f"\n{name}:")
        print(f"  Files sent: {files_sent}")
        print(f"  Total size: {total_size / (1024*1024):.2f} MB")
        print(f"  Total elapsed time (reading + transmission): {total_elapsed_time:.2f} seconds")
        print(f"  Transmission time (network only): {transmission_time:.2f} seconds")
        print(f"  Total bandwidth (including reading): {total_bandwidth / (1024*1024):.2f} MB/s")
        print(f"  Transmission bandwidth (network only): {transmission_bandwidth / (1024*1024):.2f} MB/s")
        if status.errors:
            print("  Errors:")
            for error in status.errors:
                print(f"    - {error}")

    for channel in channels:
        channel.close()

if __name__ == '__main__':
    run()
