import asyncio
import pytest
import grpc
from src.edge_simulator.transport.grpc_client import TelemetryGrpcClient
from src.edge_simulator.proto import telemetry_pb2
from src.edge_simulator.proto import telemetry_pb2_grpc

class MockTelemetryService(telemetry_pb2_grpc.TelemetryServiceServicer):
    def __init__(self):
        self.telemetry_events = []
        self.image_events = []

    async def StreamTelemetry(self, request_iterator, context):
        async for event in request_iterator:
            self.telemetry_events.append(event)
        return telemetry_pb2.TelemetryAck(success=True, message="OK")

    async def StreamInspectionImage(self, request_iterator, context):
        async for event in request_iterator:
            self.image_events.append(event)
        return telemetry_pb2.InspectionAck(success=True, message="OK")

@pytest.mark.asyncio
async def test_grpc_client_streams_successfully():
    server = grpc.aio.server()
    mock_service = MockTelemetryService()
    telemetry_pb2_grpc.add_TelemetryServiceServicer_to_server(mock_service, server)
    port = server.add_insecure_port('[::]:0')
    await server.start()
    
    client = TelemetryGrpcClient(f'localhost:{port}')
    await client.start()
    
    event = telemetry_pb2.TelemetryEvent(supplier_code="TEST")
    await client.enqueue_telemetry(event)
    
    image = telemetry_pb2.InspectionImage(supplier_code="TEST_IMG")
    await client.enqueue_image(image)
    
    await asyncio.sleep(1.0)
    await client.stop()
    await server.stop(grace=None)
    
    assert len(mock_service.telemetry_events) == 1
    assert mock_service.telemetry_events[0].supplier_code == "TEST"
    assert len(mock_service.image_events) == 1
    assert mock_service.image_events[0].supplier_code == "TEST_IMG"
