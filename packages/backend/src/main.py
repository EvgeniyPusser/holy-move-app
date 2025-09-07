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
        # Геокодирование ZIP-кодов через OpenRouteService
        ors_key = os.getenv("API_ORS")
        geo_url_from = f"https://api.openrouteservice.org/geocode/search?api_key={ors_key}&text={fromZip}&boundary.country=US"
        geo_url_to = f"https://api.openrouteservice.org/geocode/search?api_key={ors_key}&text={toZip}&boundary.country=US"

        async with session.get(geo_url_from) as geo_response:
            geo_data = await geo_response.json()
            start = geo_data['features'][0]['geometry']['coordinates']  # [lon, lat]

        async with session.get(geo_url_to) as geo_response:
            geo_data = await geo_response.json()
            end = geo_data['features'][0]['geometry']['coordinates']  # [lon, lat]

        # Запрос маршрута через OpenRouteService Directions API
        route_url = "https://api.openrouteservice.org/v2/directions/driving-car"
        headers = {"Authorization": ors_key, "Content-Type": "application/json"}
        payload = {
            "coordinates": [start, end]
        }

        async with session.post(route_url, json=payload, headers=headers) as route_response:
            if route_response.status != 200:
                # Fallback: если сервис недоступен, возвращаем только точки
                return {
                    "start": {"lat": start[1], "lon": start[0]},
                    "end": {"lat": end[1], "lon": end[0]},
                    "polyline": []
                }
            route_data = await route_response.json()
            geometry = route_data['routes'][0]['geometry']
            # polyline может быть в формате encoded, декодировать на фронте через leaflet-polyline
            return {
                "start": {"lat": start[1], "lon": start[0]},
                "end": {"lat": end[1], "lon": end[0]},
                "polyline": geometry
            }
