"""gRPC Client."""
import asyncio
import logging
import grpc
import time
from typing import AsyncGenerator

from src.edge_simulator.proto import telemetry_pb2
from src.edge_simulator.proto import telemetry_pb2_grpc

logger = logging.getLogger(__name__)

class TelemetryGrpcClient:
    """Async gRPC client for streaming telemetry and images."""

    def __init__(self, target: str):
        self.target = target
        self._telemetry_queue: asyncio.Queue = asyncio.Queue(maxsize=10000)
        self._image_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._running = False
        self._telemetry_count = 0
        self._image_count = 0
        self._start_time = 0.0

    async def enqueue_telemetry(self, event: telemetry_pb2.TelemetryEvent):
        """Enqueue telemetry event for streaming."""
        try:
            await self._telemetry_queue.put(event)
        except asyncio.QueueFull:
            logger.warning("Telemetry queue full, dropping event.")

    async def enqueue_image(self, image: telemetry_pb2.InspectionImage):
        """Enqueue image for streaming."""
        try:
            await self._image_queue.put(image)
        except asyncio.QueueFull:
            logger.warning("Image queue full, dropping image.")

    async def _telemetry_generator(self) -> AsyncGenerator[telemetry_pb2.TelemetryEvent, None]:
        """Generator that yields events from the queue."""
        while self._running:
            try:
                # Use a small timeout so we can exit gracefully
                event = await asyncio.wait_for(self._telemetry_queue.get(), timeout=1.0)
                self._telemetry_count += 1
                yield event
                self._telemetry_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    async def _image_generator(self) -> AsyncGenerator[telemetry_pb2.InspectionImage, None]:
        """Generator that yields images from the queue."""
        while self._running:
            try:
                # Use a small timeout so we can exit gracefully
                image = await asyncio.wait_for(self._image_queue.get(), timeout=1.0)
                self._image_count += 1
                yield image
                self._image_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    async def _stream_telemetry_loop(self):
        """Continuous loop for streaming telemetry."""
        backoff = 1.0
        while self._running:
            try:
                async with grpc.aio.insecure_channel(self.target) as channel:
                    stub = telemetry_pb2_grpc.TelemetryServiceStub(channel)
                    logger.info("Connected to gRPC server (Telemetry stream).")
                    backoff = 1.0  # reset backoff on successful connect
                    
                    # This will block as long as generator produces items and connection is alive
                    response = await stub.StreamTelemetry(self._telemetry_generator())
                    logger.info(f"StreamTelemetry ended: {response.message if response else ''}")
            except grpc.aio.AioRpcError as e:
                if self._running:
                    logger.error(f"gRPC error (Telemetry): {e.details()} (code: {e.code()})")
            except Exception as e:
                if self._running:
                    logger.error(f"Unexpected error (Telemetry): {e}")
            
            if self._running:
                logger.info(f"Reconnecting telemetry stream in {backoff} seconds...")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30.0)

    async def _stream_image_loop(self):
        """Continuous loop for streaming images."""
        backoff = 1.0
        while self._running:
            try:
                async with grpc.aio.insecure_channel(self.target) as channel:
                    stub = telemetry_pb2_grpc.TelemetryServiceStub(channel)
                    logger.info("Connected to gRPC server (Image stream).")
                    backoff = 1.0
                    
                    response = await stub.StreamInspectionImage(self._image_generator())
                    logger.info(f"StreamInspectionImage ended: {response.message if response else ''}")
            except grpc.aio.AioRpcError as e:
                if self._running:
                    logger.error(f"gRPC error (Image): {e.details()} (code: {e.code()})")
            except Exception as e:
                if self._running:
                    logger.error(f"Unexpected error (Image): {e}")
            
            if self._running:
                logger.info(f"Reconnecting image stream in {backoff} seconds...")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30.0)

    async def _log_throughput(self):
        """Log throughput metrics."""
        while self._running:
            await asyncio.sleep(10.0)
            elapsed = time.time() - self._start_time
            t_rate = self._telemetry_count / elapsed if elapsed > 0 else 0
            i_rate = self._image_count / elapsed if elapsed > 0 else 0
            logger.info(f"Throughput: {t_rate:.2f} telemetry/sec, {i_rate:.2f} images/sec")

    async def start(self):
        """Start streaming loops."""
        self._running = True
        self._start_time = time.time()
        self._telemetry_count = 0
        self._image_count = 0
        
        self._t_task = asyncio.create_task(self._stream_telemetry_loop())
        self._i_task = asyncio.create_task(self._stream_image_loop())
        self._log_task = asyncio.create_task(self._log_throughput())

    async def stop(self):
        """Stop streaming loops."""
        self._running = False
        if hasattr(self, '_t_task'):
            self._t_task.cancel()
        if hasattr(self, '_i_task'):
            self._i_task.cancel()
        if hasattr(self, '_log_task'):
            self._log_task.cancel()
        try:
            await asyncio.gather(self._t_task, self._i_task, self._log_task, return_exceptions=True)
        except Exception:
            pass
