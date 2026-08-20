from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from engine import HydromindEngine
import uvicorn

app = FastAPI(title="Hydromind Backend API")

# Allow Frontend (React / Web / Mobile) to access API without CORS blocking
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Initialize AI Engine once when server starts
ai_engine = HydromindEngine(model_path="hydromind_model.pkl")

# In-memory store for the latest reading
latest_reading = {
    "pollution_score": 0,
    "status": "Waiting for sensor data..."
}

@app.get("/")
def home():
    return {"message": "Hydromind Server is Running!"}

@app.post("/api/analyze")
async def analyze_water(
    turbidity_v: float = Form(...),
    conductivity_v: float = Form(...),
    image: UploadFile = File(...)
):
    """
    Endpoint called by Hardware / ESP32.
    Receives voltages + image file, processes AI inference, and updates state.
    """
    global latest_reading
    try:
        image_bytes = await image.read()
        
        # Run AI Inference Engine
        score = ai_engine.predict_pollution_score(
            image_bytes=image_bytes,
            turbidity_v=turbidity_v,
            conductivity_v=conductivity_v
        )
        
        # Update global state
        latest_reading = {
            "pollution_score": score,
            "turbidity_v": turbidity_v,
            "conductivity_v": conductivity_v
        }
        
        return {"success": True, "pollution_score": score}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/score")
def get_score():
    """
    Endpoint called by Frontend Guy.
    Returns the latest calculated Pollution Score.
    """
    return latest_reading

if __name__ == "__main__":
    print("\nStarting Hydromind Local Backend Server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)