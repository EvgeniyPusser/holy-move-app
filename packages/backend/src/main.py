from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiohttp
import os
from dotenv import load_dotenv
import redis.asyncio as redis
import json

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

class MovingRequest(BaseModel):
    fromZip: str
    toZip: str
    rooms: int
    moveDate: str

class MovingResponse(BaseModel):
    price: float
    truckType: str
    helpersCount: int

@app.post("/api/calculate-moving", response_model=MovingResponse)
async def calculate_moving(request: MovingRequest):
    cache_key = f"calc_{request.fromZip}_{request.toZip}_{request.rooms}_{request.moveDate}"
    cached = await redis_client.get(cache_key)
    if cached:
        return MovingResponse(**json.loads(cached))

    async with aiohttp.ClientSession() as session:
        ai_url = os.getenv("AI_API_URL")
        ai_key = os.getenv("AI_KEY")
        payload = {
            "from_zip": request.fromZip,
            "to_zip": request.toZip,
            "rooms": request.rooms,
            "move_date": request.moveDate,
        }
        headers = {"Authorization": f"Bearer {ai_key}"}
        async with session.post(ai_url, json=payload, headers=headers) as response:
            result = await response.json()
            await redis_client.setex(cache_key, 3600, json.dumps(result))
            return MovingResponse(
                price=result["price"],
                truckType=result["truck_type"],
                helpersCount=result["helpers_count"],
            )

@app.get("/api/get-route")
async def get_route(fromZip: str, toZip: str):
    async with aiohttp.ClientSession() as session:
        geo_url = f"https://nominatim.openstreetmap.org/search?format=json&postalcode={fromZip}&country=USA"
        async with session.get(geo_url) as geo_response:
            geo_data = await geo_response.json()
            start = {"lat": float(geo_data[0]["lat"]), "lon": float(geo_data[0]["lon"])}

        geo_url = f"https://nominatim.openstreetmap.org/search?format=json&postalcode={toZip}&country=USA"
        async with session.get(geo_url) as geo_response:
            geo_data = await geo_response.json()
            end = {"lat": float(geo_data[0]["lat"]), "lon": float(geo_data[0]["lon"])}

        route_url = f"http://router.project-osrm.org/route/v1/driving/{start['lon']},{start['lat']};{end['lon']},{end['lat']}?geometries=geojson"
        async with session.get(route_url) as route_response:
            route_data = await route_response.json()
            polyline = route_data["routes"][0]["geometry"]["coordinates"]
            return {"start": start, "end": end, "polyline": [[lat, lon] for lon, lat in polyline]}
