import grpc
import filetransfer_pb2
import filetransfer_pb2_grpc

def send_file(stub, filename):
    with open(filename, 'rb') as f:
        content = f.read()
    response = stub.SendFile(filetransfer_pb2.FileRequest(filename=filename, content=content))
    print("Server response: " + response.message)

def receive_file(stub, filename):
    response = stub.ReceiveFile(filetransfer_pb2.FileRequest(filename=filename))
    if response.content:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print("File received and saved as: " + filename)
    else:
        print(response.message)

def run():
    with grpc.insecure_channel('192.168.0.103:50051',
                               options=[('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100 MB limit
                                        ('grpc.max_receive_message_length', 100 * 1024 * 1024)]) as channel:
        stub = filetransfer_pb2_grpc.FileTransferStub(channel)
        action = input("Do you want to (S)end or (R)eceive a file? ").strip().upper()
        filename = input("Enter the filename: ")

        if action == 'S':
            send_file(stub, filename)
        elif action == 'R':
            receive_file(stub, filename)
        else:
            print("Invalid action")

if __name__ == '__main__':
    run()
