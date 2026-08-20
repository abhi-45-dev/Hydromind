from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from engine import HydromindEngine
import uvicorn

app = FastAPI(title="Hydromind Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_engine = HydromindEngine(model_path="hydromind_model.pkl")

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
    temperature_c: float = Form(25.0),
    image: UploadFile = File(...)
):
    global latest_reading
    try:
        image_bytes = await image.read()
        
        score = ai_engine.predict_pollution_score(
            image_bytes=image_bytes,
            turbidity_v=turbidity_v,
            temperature_c=temperature_c
        )
        
        latest_reading = {
            "pollution_score": score,
            "turbidity_v": turbidity_v,
            "temperature_c": temperature_c
        }
        
        return {"success": True, "pollution_score": score}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/score")
def get_score():
    return latest_reading

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)