from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
from static.posting_logic.mastadon_post import post_to_mastodon
from static.posting_logic.discord_post import post_to_discord
# from static.postong_logic.linkedin_post import post_to_linkedin  # Example for future
# from static.postong_logic.bluesky_post import post_to_bluesky  # Uncomment when available

app = FastAPI()

# Mount static files (for style.css, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/daily", response_class=HTMLResponse)
def daily_page(request: Request):
    return templates.TemplateResponse("daily.html", {"request": request})

@app.get("/create-event", response_class=HTMLResponse)
def create_event_page(request: Request):
    return templates.TemplateResponse("create_event.html", {"request": request})

@app.get("/create-project", response_class=HTMLResponse)
def create_project_page(request: Request):
    return templates.TemplateResponse("create_project.html", {"request": request})

@app.get("/edit-project", response_class=HTMLResponse)
def edit_project_page(request: Request):
    return templates.TemplateResponse("edit_project.html", {"request": request})

@app.get("/create-project-ai", response_class=HTMLResponse)
def create_project_ai_page(request: Request):
    return templates.TemplateResponse("create_project_ai.html", {"request": request})

@app.get("/posting", response_class=HTMLResponse)
def posting_page(request: Request):
    return templates.TemplateResponse("posting.html", {"request": request})

@app.post("/multi-site-post")
async def multi_site_post(request: Request):
    data = await request.json()
    results = {}
    # Discord
    if data.get("discord", {}).get("enabled"):
        try:
            post_to_discord(
                kofi_url=data["message"].get("originalPost", ""),
                comment=data["message"].get("postText", ""),
                webhooks=data["discord"]["webhooks"],
                image_path=data["message"].get("imagePath")
            )
            results["discord"] = "sent"
        except Exception as e:
            results["discord"] = f"error: {e}"
    # Mastodon
    if data.get("mastodon", {}).get("enabled"):
        try:
            post_to_mastodon(
                data["mastodon"]["url"],
                data["mastodon"]["token"],
                data["message"]["postText"],
                data["message"].get("imagePath")
            )
            results["mastodon"] = "sent"
        except Exception as e:
            results["mastodon"] = f"error: {e}"
    # Bluesky (uncomment when available)
    # if data.get("bluesky", {}).get("enabled"):
    #     try:
    #         post_to_bluesky(
    #             handle=data["bluesky"]["handle"],
    #             password=data["bluesky"]["password"],
    #             message=data["message"]["postText"],
    #             image_path=data["message"].get("imagePath")
    #         )
    #         results["bluesky"] = "sent"
    #     except Exception as e:
    #         results["bluesky"] = f"error: {e}"
    # Add more site logic here as you add .py scripts
    return JSONResponse(results)

@app.post("/save-posting-config")
async def save_posting_config(request: Request):
    data = await request.json()
    config_path = os.path.join("static", "posting_config.json")
    print(f"[SAVE CONFIG] Attempting to write to: {os.path.abspath(config_path)}")
    try:
        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)
        print("[SAVE CONFIG] Successfully wrote config.")
        return {"status": "success"}
    except Exception as e:
        print(f"[SAVE CONFIG] Error: {e}")
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=500)

@app.get("/load-posting-config")
async def load_posting_config():
    config_path = os.path.join("static", "posting_config.json")
    if not os.path.exists(config_path):
        return JSONResponse(content={}, status_code=404)
    with open(config_path, "r") as f:
        data = json.load(f)
    return data 