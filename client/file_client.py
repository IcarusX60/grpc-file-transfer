import grpc
import filetransfer_pb2
import filetransfer_pb2_grpc

def run():
    with grpc.insecure_channel('192.168.0.106:50051',options=[('grpc.max_send_message_length', 100 * 1024 * 1024)]) as channel:
        stub = filetransfer_pb2_grpc.FileTransferStub(channel)
        filename = "largefile.txt"  # Replace with your file's name
        with open(filename, 'rb') as f:
            content = f.read()
        response = stub.SendFile(filetransfer_pb2.FileRequest(filename=filename, content=content))
        print("Server response: " + response.message)

if __name__ == '__main__':
    run()
