from concurrent import futures
import grpc
import filetransfer_pb2
import filetransfer_pb2_grpc

class FileTransferServicer(filetransfer_pb2_grpc.FileTransferServicer):
    def SendFile(self, request, context):
        with open(request.filename, 'wb') as f:
            f.write(request.content)
        return filetransfer_pb2.FileResponse(message=f"Received file {request.filename}")

    def ReceiveFile(self, request, context):
        try:
            with open(request.filename, 'rb') as f:
                content = f.read()
            return filetransfer_pb2.FileResponse(message=f"File {request.filename} sent successfully", content=content)
        except FileNotFoundError:
            return filetransfer_pb2.FileResponse(message=f"File {request.filename} not found")

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[('grpc.max_receive_message_length', 100 * 1024 * 1024)]  # 100 MB limit
    )
    filetransfer_pb2_grpc.add_FileTransferServicer_to_server(FileTransferServicer(), server)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
