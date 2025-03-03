from fastapi import FastAPI, Query
from typing import List
import os
import json
import requests

TOKEN = open(os.path.expanduser(os.environ('MAPILLARY_CLIENT_TOKEN_FILE'))).read().strip()
url = "https://graph.mapillary.com/images"

app = FastAPI()

@app.get("/api/mapillary")
def get_images(bbox: List[float] = Query(..., description="Bounding box coordinates in the format [minLon, minLat, maxLon, maxLat]")):

    params = {
        "bbox": ",".join(map(str, bbox)),
        "fields": "id,geometry,compass_angle,thumb_1024_url",
        "access_token": TOKEN,
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    sorted_data = sorted(data['data'], key=lambda x: x['compass_angle'])
    return sorted_data