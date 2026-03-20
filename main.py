from fastapi import FastAPI
from routers import video, search, channel, music

app = FastAPI(
    title="Plus API",
    description="Plus API - YouTube client API powered by yt-dlp",
    version="1.0.0"
)

app.include_router(video.router,   prefix="/video",   tags=["Video"])
app.include_router(search.router,  prefix="/search",  tags=["Search"])
app.include_router(channel.router, prefix="/channel", tags=["Channel"])
app.include_router(music.router,   prefix="/music",   tags=["Music"])

@app.get("/")
def root():
    return {"message": "Plus API is running 🎬"}
