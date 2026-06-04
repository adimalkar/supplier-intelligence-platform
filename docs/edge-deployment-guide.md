# Edge Deployment Guide

The Edge Simulator represents code that will eventually run on factory hardware.

## Running Locally

To start the simulator:
```bash
make simulator
```

## Running on Real Hardware
1. Ensure Python 3.10+ is installed on the edge device.
2. Compile the gRPC stubs for the specific target architecture if needed.
3. Set the `INGESTION_GRPC_URL` environment variable to point to the central server.
4. Run the simulator pointing to the real sensor endpoints instead of random generation.
