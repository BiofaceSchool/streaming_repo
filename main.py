from fastapi import FastAPI, APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi import UploadFile, File
from sqlalchemy.orm import Session
import cv2
import uuid
import numpy as np
import face_recognition
from vidgear.gears import CamGear
from io import BytesIO
from auth_repository import AuthRepository
from typing import Generator, List, Dict
import asyncio
from dependency_config import get_db
from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Definir una instancia global para almacenar el detector
yt_object_detector_instance = None


class FacialDataService:
    def __init__(self, db):
        self.auth_repo = AuthRepository(db)
        self.db = db

    def recognize(self, img):
        embeddings_unknown = face_recognition.face_encodings(img)
        if len(embeddings_unknown) == 0:
            return 'no_persons_found', False
        embeddings_unknown = embeddings_unknown[0]

        match = False
        user_found = None
        users = self.auth_repo.get_all()

        for user in users:
            embeddings_db = user.embeddings
            if not embeddings_db:
                continue
            match = face_recognition.compare_faces([embeddings_db], embeddings_unknown)[0]
            if match:
                user_found = user
                break

        if match:
            return user_found.name, True 
        else:
            return 'unknown_person', False

    async def verify_face(self, file: UploadFile = File(...)):
        contents = await file.read()
        image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
        
        loop = asyncio.get_event_loop()
        user_name, match_status = await loop.run_in_executor(None, self.recognize, image)
        
        return {'user': user_name, 'match_status': match_status}

class YTObjectDetector:
    video_url: str
    video_resolution: str = "720p"
    face_detector: FacialDataService
    last_detected_face: Dict[str, str] = {}

    def __init__(self, video_url: str, db):
        self.video_url = video_url
        self.face_detector = FacialDataService(db)

    async def run(self):
        frame_counter = 0
        async for frame in self._get_video_frames_generator():
            frame_counter += 1

            if frame_counter % 5 == 0:  # Reducir la frecuencia de detección facial
                await self.detect_face(frame)

            _, frame_encoded = cv2.imencode(".jpg", frame)
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + bytearray(frame_encoded) + b"\r\n"

    async def detect_face(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            for face_location in face_locations:
                top, right, bottom, left = face_location
                face_image = frame[top:bottom, left:right]

                _, encoded_image = cv2.imencode(".png", face_image)
                face_file = BytesIO(encoded_image.tobytes())
                
                upload_file = UploadFile(filename=f"{uuid.uuid4()}.png", file=face_file)
                result = await self.face_detector.verify_face(upload_file)

                if result['match_status']:
                    self.last_detected_face = {'user': result['user'], 'status': 'matched'}
                    print(f"Rostro coincidente: {result['user']}")
                else:
                    self.last_detected_face = {'user': 'unknown_person', 'status': 'unmatched'}
                    print("Rostro desconocido.")

    async def _get_video_frames_generator(self) -> Generator[np.ndarray, None, None]:
        options = {"STREAM_RESOLUTION": self.video_resolution}
        video = CamGear(source=self.video_url, stream_mode=True, logging=True, **options).start()

        while True:
            frame = video.read()
            if frame is None:
                break
            yield frame

        video.stop()

    def get_last_detected_face(self):
        return self.last_detected_face


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)


@app.get("/faces_detected")
async def faces_detected():
    if yt_object_detector_instance is None:
        return {"message": "Please initialize the detector first by providing the video URL."}
    return {"detected_face": yt_object_detector_instance.get_last_detected_face()}

@app.get("/video_url")
async def get_video_url():
    if yt_object_detector_instance is None:
        return {"message": "Please initialize the detector first by providing the video URL."}
    return {"video_url": yt_object_detector_instance.video_url}

@app.post("/update_video_url")
async def update_video_url(new_video_url: str, db: Session = Depends(get_db)):
    global yt_object_detector_instance
    yt_object_detector_instance = YTObjectDetector(video_url=new_video_url, db=db)

    if yt_object_detector_instance is None:
        return {"message": "Please initialize the detector first by providing the video URL."}
    
    return {"message": "Video URL updated successfully.", "new_video_url": new_video_url}

@app.get("/detection")
async def detection():
    if yt_object_detector_instance is None:
        return {"message": "Please initialize the detector first by providing the video URL."}
    return StreamingResponse(yt_object_detector_instance.run(), media_type="multipart/x-mixed-replace;boundary=frame")


@app.get("/", include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
