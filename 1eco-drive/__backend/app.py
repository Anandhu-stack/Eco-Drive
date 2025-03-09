from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# ✅ Initialize FastAPI first
app = FastAPI()

# ✅ CORS Middleware (Allows frontend requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Restrict to frontend only
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Import Environment module safely
try:
    from Environment import environment  # Ensure Environment.py exists
except ImportError:
    logger.error("Failed to import Environment module. Make sure Environment.py exists.")
    raise ImportError("Module 'Environment' not found. Check the file path.")

@app.get("/")
async def root():
    return {"message": "API is running!"}

@app.get("/route")
async def get_route(origin: str, destination: str):
    try:
        env = environment(origin, destination)
        step_reward, charge_num, SOC, time = env.origine_map_reward()

        # ✅ Dummy route (Replace with actual data)
        route = [
            {"lat": 40.468254, "lng": -86.980963},
            {"lat": 40.465123, "lng": -86.975432},
            {"lat": 40.462345, "lng": -86.970123},
            {"lat": 40.458765, "lng": -86.965432},
            {"lat": 40.455432, "lng": -86.960123},
            {"lat": 40.452345, "lng": -86.955432},
            {"lat": 40.449876, "lng": -86.952345},
            {"lat": 40.445283, "lng": -86.948429}
        ]

        return {
            "reward": step_reward,
            "charge_num": charge_num,
            "SOC": SOC,
            "time": time,
            "route": route
        }

    except Exception as e:
        logger.error(f"Error processing route: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


"""
from fastapi import FastAPI
from Environment import environment# Ensure this import is correct
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ✅ Allow frontend requests
    allow_credentials=True,
    allow_methods=["*"],  # ✅ Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # ✅ Allow all headers
)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is running!"}

@app.get("/route")
async def get_route(origin: str, destination: str):
    env = environment(origin, destination)
    step_reward, charge_num, SOC, time = env.origine_map_reward()

    # Dummy route (Replace this with actual route data)
    route = [
        {"lat": 40.468254, "lng": -86.980963},
        {"lat": 40.465123, "lng": -86.975432},
        {"lat": 40.462345, "lng": -86.970123},
        {"lat": 40.458765, "lng": -86.965432},
        {"lat": 40.455432, "lng": -86.960123},
        {"lat": 40.452345, "lng": -86.955432},
        {"lat": 40.449876, "lng": -86.952345},
        {"lat": 40.445283, "lng": -86.948429}
    ]

    return {
        "reward": step_reward,
        "charge_num": charge_num,
        "SOC": SOC,
        "time": time,
        "route": route
    }
"""