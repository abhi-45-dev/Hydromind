from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="Hydromind API",
    description="Backend API for the Hydromind water quality monitoring system",
    version="1.0.0",
)


class SensorData(BaseModel):
    temperature: Optional[float] = None
    turbidity_voltage: Optional[float] = None
    camera_url: Optional[str] = None
    ml_score: Optional[float] = None
    device_online: bool = False


latest_data = SensorData()


@app.get("/")
def root():
    return {
        "status": "online",
        "system": "Hydromind",
        "message": "Water quality monitoring API is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/sensor-data")
def get_sensor_data():
    return latest_data


@app.post("/api/sensor-data")
def receive_sensor_data(data: SensorData):
    global latest_data

    latest_data = data

    return {
        "status": "received",
        "data": latest_data,
    }