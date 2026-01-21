from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from hd.compute import compute_hd_gates
from geopy.geocoders import Nominatim
import pytz
from datetime import datetime
from hd.compute import compute_hd_gates

app = FastAPI()

class BirthData(BaseModel):
    year: int
    month: int
    day: int
    hour: float
    city: str
    country: str

@app.get("/", response_class=HTMLResponse)
def index():
    with open("templates/index.html") as f:
        return f.read()

@app.post("/compute-hd")
def compute_hd(data: BirthData):
    # 1. Convert city + country → lat/lon
    geolocator = Nominatim(user_agent="hd_study")
    location = geolocator.geocode(f"{data.city}, {data.country}")

    if location is None:
        return {"error": "City not found"}

    lat, lon = location.latitude, location.longitude

    # 2. Call HD computation
    gates = compute_hd_gates(
        data.year,
        data.month,
        data.day,
        data.hour,
        lat,
        lon
    )

    # 3. Return result to browser
    return gates