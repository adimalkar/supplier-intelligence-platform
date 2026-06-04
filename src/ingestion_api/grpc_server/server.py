import grpc
from concurrent import futures
import logging
from src.ingestion_api.config import settings
from src.ingestion_api.proto import telemetry_pb2_grpc
from src.ingestion_api.grpc_server.servicer import TelemetryServicer

logger = logging.getLogger(__name__)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    telemetry_pb2_grpc.add_TelemetryServiceServicer_to_server(TelemetryServicer(), server)
    port = settings.GRPC_PORT
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f"gRPC server started, listening on {port}")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
