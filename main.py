from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Mount static files (for style.css, images, and index.html)
app.mount("/static", StaticFiles(directory=os.path.dirname(os.path.abspath(__file__))), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return FileResponse(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")) 