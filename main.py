import os
import base64
import mimetypes
from datetime import datetime
import re
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel, validator
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

#gets the mongo uri from the environment to access the database
def getDB():
    MONGO_URI = os.getenv("MONGO_URI")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["Assets"]
    return db

#validates the player model
class PlayerScore(BaseModel):
    player_name: str
    score: int

    #validates that the player name only contains letters, numbers and underscores
    @validator('player_name')
    def validate_player_name(cls, value):
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValueError('Player name must only contain alphanumeric characters and underscores')
        return value

    #validates the score range, ensuring that it is equal to or larger than zero without being too large
    @validator('score')
    def validate_score(cls, value):
        if value < 0 or value > 1000000:
            raise ValueError('Score must be a non-negative number within a reasonable range')
        return value

#Helper function to determine the MIME type
def get_mime_type(filename):
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"

#Helper function to Process the uploading of files
async def process_file(file: UploadFile):
    content = await file.read()
    if len(content) > 4 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
    encoded = base64.b64encode(content).decode("utf-8")
    return {
        "filename": file.filename,
        "file_type": get_mime_type(file.filename),
        "size": len(content),
        "upload_date": datetime.utcnow(),
        "content": encoded
    }

#uploads a sprite/image file to the database
@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...), db=Depends()):
    data = await process_file(file)
    result = await db["Sprites"].insert_one(data)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

#retrieves the uploaded sprite/image file by its given MongoDB ID
@app.get("/sprite/{id}")
async def get_sprite(id: str, db=Depends(getDB())):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    sprite = await db["Sprites"].find_one({"_id": ObjectId(id)})
    if not sprite:
        raise HTTPException(status_code=404, detail="Sprite not found")
    
    return Response(
        content=base64.b64decode(sprite["content"]),
        media_type=sprite["file_type"],
        headers={"Content-Disposition": f"inline; filename={sprite['filename']}"}
    )

#uploads an audio file to the database
@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...), db=Depends(getDB())):
    data = await process_file(file)
    result = await db["Audio"].insert_one(data)
    return {"message": "Audio uploaded", "id": str(result.inserted_id)}

#retrieves the uploaded audio file by its given MongoDB ID
@app.get("/audio/{id}")
async def get_audio(id: str, db=Depends(getDB())):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    audio = await db["Audio"].find_one({"_id": ObjectId(id)})
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    return Response(
        content=base64.b64decode(audio["content"]),
        media_type=audio["file_type"],
        headers={"Content-Disposition": f"inline; filename={audio['filename']}"}
    )

#uploads the player score to the database as a JSON object
@app.post("/player_score")
async def upload_score(score: PlayerScore, db=Depends(getDB())):
    if score.score < 0:
        raise HTTPException(status_code=400, detail="Score must be non-negative")
    doc = {
        "player_name": score.player_name,
        "score": score.score,
        "date_achieved": datetime.utcnow()
    }
    result = await db["Score"].insert_one(doc)
    return {"message": "Score uploaded", "id": str(result.inserted_id)}

#retrieves the player score by its given MongoDB ID
@app.get("/player_score/{id}")
async def get_score(id: str, db=Depends(getDB())):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    score = await db["Score"].find_one({"_id": ObjectId(id)})
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    return {
        "player_name": score["player_name"],
        "score": score["score"],
        "date_achieved": score["date_achieved"]
    }

#searches player scores based on the player name
@app.get("/search_scores")
async def search_scores(player_name: str = None, db=Depends(getDB())):
    if player_name:
        #validates the player name to avoid SQL injection attacks
        if not re.match(r'^[a-zA-Z0-9_ ]+$', player_name):
            raise HTTPException(status_code=400, detail="Invalid characters in player name")
        
        scores = await db["Score"].find({"player_name": player_name}).to_list(length=100)
    else:
        #returns all the scores if no name is provided
        scores = await db["Score"].find().to_list(length=100)

    return scores
