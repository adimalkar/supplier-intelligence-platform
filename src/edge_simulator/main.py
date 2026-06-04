"""Edge Simulator Main Entry Point."""
import argparse
import asyncio
import logging
import sys
import time
import numpy as np

from src.common.config import settings
from src.edge_simulator.config import get_supplier_profile
from src.edge_simulator.generators.telemetry import TelemetryGenerator
from src.edge_simulator.generators.image import InspectionImageGenerator
from src.edge_simulator.transport.grpc_client import TelemetryGrpcClient
from src.edge_simulator.proto import telemetry_pb2

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO), 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def simulate_equipment(
    generator: TelemetryGenerator,
    image_generator: InspectionImageGenerator,
    grpc_client: TelemetryGrpcClient,
    speed: float,
    duration: float,
    anomaly_mode: bool
):
    """Simulate a single piece of equipment."""
    start_time = time.time()
    
    # Calculate sleep interval based on cycle time and speed
    cycle_time = generator.product_line.base_cycle_time_sec / speed
    
    while True:
        if duration > 0 and time.time() - start_time >= duration:
            break
            
        # Generate telemetry
        data = generator.generate()
        
        # Create protobuf event
        event = telemetry_pb2.TelemetryEvent(
            supplier_code=data["supplier_code"],
            equipment_code=data["equipment_code"],
            product_line_code=data["product_line_code"],
            timestamp_ms=data["timestamp_ms"],
            cycle_time_seconds=data["cycle_time_seconds"],
            units_produced=data["units_produced"],
            units_passed=data["units_passed"],
            temperature_c=data["temperature_c"],
            pressure_psi=data["pressure_psi"],
            vibration_mm_s=data["vibration_mm_s"],
            power_consumption_kw=data["power_consumption_kw"],
            process_params=data["process_params"]
        )
        
        await grpc_client.enqueue_telemetry(event)
        
        # Decide if we generate an image (e.g. for inspection equipment or every N cycles)
        is_anomaly = data["process_params"]["anomaly_flag"] == "true"
        if is_anomaly or np.random.random() < 0.1:
            defect = None
            if is_anomaly:
                defect = np.random.choice(["scratch", "misalignment", "discoloration"])
            
            img_data = image_generator.generate(defect_type=defect)
            
            img_event = telemetry_pb2.InspectionImage(
                supplier_code=img_data["supplier_code"],
                equipment_code=img_data["equipment_code"],
                timestamp_ms=img_data["timestamp_ms"],
                image_data=img_data["image_data"],
                image_format=img_data["image_format"],
                inspection_type=img_data["inspection_type"]
            )
            
            await grpc_client.enqueue_image(img_event)
            
        # Sleep until next cycle
        await asyncio.sleep(cycle_time)

async def main_async():
    parser = argparse.ArgumentParser(description="Supplier Edge Simulator")
    parser.add_argument("--suppliers", type=str, required=True, help="Comma-separated list of supplier codes")
    parser.add_argument("--speed", type=float, default=1.0, help="Simulation speed multiplier")
    parser.add_argument("--duration", type=float, default=0.0, help="Duration to run in seconds (0 = infinite)")
    parser.add_argument("--anomaly-mode", action="store_true", help="Force anomaly generation")
    
    args = parser.parse_args()
    
    supplier_codes = [s.strip() for s in args.suppliers.split(",")]
    logger.info(f"Starting Edge Simulator for suppliers: {supplier_codes}")
    logger.info(f"Speed: {args.speed}x, Duration: {args.duration}s, Anomaly Mode: {args.anomaly_mode}")
    
    grpc_client = TelemetryGrpcClient(settings.simulator.GRPC_TARGET)
    await grpc_client.start()
    
    tasks = []
    
    for code in supplier_codes:
        try:
            profile = get_supplier_profile(code)
            for product_line in profile.product_lines:
                for equipment in product_line.equipment:
                    generator = TelemetryGenerator(profile, product_line, equipment, args.speed, args.anomaly_mode)
                    image_generator = InspectionImageGenerator(profile, product_line, equipment)
                    
                    task = asyncio.create_task(
                        simulate_equipment(generator, image_generator, grpc_client, args.speed, args.duration, args.anomaly_mode)
                    )
                    tasks.append(task)
        except ValueError as e:
            logger.error(f"Error loading supplier {code}: {e}")
            
    if not tasks:
        logger.error("No valid equipment found to simulate. Exiting.")
        await grpc_client.stop()
        return
        
    # Wait for all tasks to complete or run indefinitely
    try:
        if args.duration > 0:
            # Add a small buffer to ensure the duration is fully respected by tasks
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=args.duration + 5.0)
        else:
            await asyncio.gather(*tasks)
    except asyncio.TimeoutError:
        logger.info("Simulation completed.")
    except asyncio.CancelledError:
        logger.info("Simulation cancelled.")
    finally:
        await grpc_client.stop()
        logger.info("Simulation finished.")

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")

if __name__ == "__main__":
    main()
