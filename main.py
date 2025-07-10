from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
from static.posting_logic.mastadon_post import post_to_mastodon
from static.posting_logic.discord_post import post_to_discord
from static.posting_logic.devto_post import post_to_devto
from static.posting_logic.bluesky_post import post_to_bluesky  # Now enabled
from models import (
    Project, Task, Event, engine, Base,
    ProjectCreate, ProjectRead,
    TaskCreate, TaskRead,
    EventCreate, EventRead
)
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from fastapi import Form
from starlette.status import HTTP_303_SEE_OTHER
from datetime import date

app = FastAPI()

# Mount static files (for style.css, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Create tables on startup
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/daily", response_class=HTMLResponse)
def daily_page(request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    projects_data = []
    for project in projects:
        tasks = db.query(Task).filter(Task.project_id == project.id).all()
        tasks_data = []
        for task in tasks:
            tasks_data.append({
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "due_date": task.due_date.isoformat() if task.due_date is not None else "",
                "completed": task.completed
            })
        projects_data.append({
            "id": project.id,
            "name": project.name,
            "tasks": tasks_data
        })
    selected_project_id = projects_data[0]["id"] if projects_data else None
    return templates.TemplateResponse("daily.html", {
        "request": request,
        "projects": projects_data,
        "selected_project_id": selected_project_id
    })

@app.get("/create-event", response_class=HTMLResponse)
def create_event_form(request: Request):
    return templates.TemplateResponse("create_event.html", {"request": request})

@app.post("/create-event")
def create_event_submit(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    start_time: str = Form(...),
    db: Session = Depends(get_db)
):
    from datetime import datetime
    event = Event(
        name=name,
        description=description,
        start_time=datetime.fromisoformat(start_time),
        completed=False
    )
    db.add(event)
    db.commit()
    return RedirectResponse(url="/daily", status_code=HTTP_303_SEE_OTHER)

@app.get("/edit-event/{event_id}", response_class=HTMLResponse)
def edit_event_form(request: Request, event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return RedirectResponse(url="/daily", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("edit_event.html", {"request": request, "event": event})

@app.post("/edit-event/{event_id}")
def edit_event_submit(
    request: Request,
    event_id: int,
    name: str = Form(...),
    description: str = Form(None),
    start_time: str = Form(...),
    completed: str = Form(None),
    db: Session = Depends(get_db)
):
    from datetime import datetime
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return RedirectResponse(url="/daily", status_code=HTTP_303_SEE_OTHER)
    setattr(event, 'name', name)
    setattr(event, 'description', description)
    setattr(event, 'start_time', datetime.fromisoformat(start_time))
    setattr(event, 'completed', completed == "on")
    db.commit()
    return RedirectResponse(url="/daily", status_code=HTTP_303_SEE_OTHER)

@app.get("/create-project", response_class=HTMLResponse)
def create_project_form(request: Request):
    return templates.TemplateResponse("create_project.html", {"request": request})

@app.post("/create-project")
async def create_project_submit(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    print("[DEBUG] /create-project POST hit. Form data:", dict(form))
    name = form.get("name")
    description = form.get("description")
    # Parse tasks
    tasks = []
    idx = 0
    while True:
        t_name = form.get(f"tasks-{idx}-name")
        if not t_name:
            break
        t_desc = form.get(f"tasks-{idx}-description")
        t_due = form.get(f"tasks-{idx}-due_date")
        t_completed = form.get(f"tasks-{idx}-completed")
        tasks.append({
            "name": t_name,
            "description": t_desc,
            "due_date": t_due if t_due else None,
            "completed": bool(t_completed)
        })
        idx += 1
    # Create project
    project = Project(name=name, description=description)
    db.add(project)
    db.commit()
    db.refresh(project)
    # Create tasks
    for t in tasks:
        due_date_obj = None
        if t["due_date"]:
            try:
                due_date_obj = date.fromisoformat(t["due_date"])
            except Exception:
                due_date_obj = None
        task = Task(
            project_id=project.id,
            name=t["name"],
            description=t["description"],
            due_date=due_date_obj,
            completed=t["completed"]
        )
        db.add(task)
    db.commit()
    return RedirectResponse(url="/daily", status_code=HTTP_303_SEE_OTHER)

@app.get("/edit-project", response_class=HTMLResponse)
def edit_project_page(request: Request):
    return templates.TemplateResponse("edit_project.html", {"request": request})

@app.get("/edit-project/{project_id}", response_class=HTMLResponse)
def edit_project_form(request: Request, project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return RedirectResponse(url="/daily", status_code=HTTP_303_SEE_OTHER)
    tasks = db.query(Task).filter(Task.project_id == project_id).order_by(Task.order).all()
    return templates.TemplateResponse("edit_project.html", {"request": request, "project": project, "tasks": tasks})

@app.post("/edit-project/{project_id}")
async def edit_project_submit(request: Request, project_id: int, db: Session = Depends(get_db)):
    form = await request.form()
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return RedirectResponse(url="/daily", status_code=HTTP_303_SEE_OTHER)
    # Update project fields
    project.name = form.get("name")
    project.description = form.get("description")
    # Handle tasks
    # Collect submitted task ids
    submitted_task_ids = set()
    idx = 0
    from datetime import date
    while True:
        t_id = form.get(f"tasks-{idx}-id")
        t_name = form.get(f"tasks-{idx}-name")
        if not t_name:
            break
        t_desc = form.get(f"tasks-{idx}-description")
        t_due = form.get(f"tasks-{idx}-due_date")
        t_completed = form.get(f"tasks-{idx}-completed")
        t_order = int(form.get(f"tasks-{idx}-order", idx))
        if t_id and t_id.isdigit():
            # Update existing task
            task = db.query(Task).filter(Task.id == int(t_id), Task.project_id == project_id).first()
            if task:
                task.name = t_name
                task.description = t_desc
                task.due_date = date.fromisoformat(t_due) if t_due else None
                task.completed = bool(t_completed)
                task.order = t_order
                submitted_task_ids.add(task.id)
        else:
            # New task
            new_task = Task(
                project_id=project_id,
                name=t_name,
                description=t_desc,
                due_date=date.fromisoformat(t_due) if t_due else None,
                completed=bool(t_completed),
                order=t_order
            )
            db.add(new_task)
        idx += 1
    # Delete removed tasks
    all_tasks = db.query(Task).filter(Task.project_id == project_id).all()
    for task in all_tasks:
        if task.id not in submitted_task_ids:
            db.delete(task)
    db.commit()
    return RedirectResponse(url="/daily", status_code=HTTP_303_SEE_OTHER)

@app.post("/delete-project/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        db.query(Task).filter(Task.project_id == project_id).delete()
        db.delete(project)
        db.commit()
    return RedirectResponse(url="/daily", status_code=HTTP_303_SEE_OTHER)

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
    # Dev.to
    if data.get("devto", {}).get("enabled"):
        try:
            post_to_devto(
                api_key=data["devto"]["api_key"],
                kofi_url=data["message"].get("originalPost", ""),
                comment=data["message"].get("postText", ""),
                image_path=data["message"].get("imagePath")
            )
            results["devto"] = "sent"
        except Exception as e:
            results["devto"] = f"error: {e}"
    # Bluesky - app password bvoy-gudy-fd7x-4eww
    if data.get("bluesky", {}).get("enabled"):
        try:
            post_to_bluesky(
                handle=data["bluesky"]["handle"],
                password=data["bluesky"]["password"],
                message=data["message"]["postText"],
                image_path=data["message"].get("imagePath")
            )
            results["bluesky"] = "sent"
        except Exception as e:
            results["bluesky"] = f"error: {e}"
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

# ------------------- Projects -------------------
@app.post("/projects", response_model=ProjectRead)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()

@app.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/projects/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project.dict().items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return

# ------------------- Tasks -------------------
@app.post("/tasks", response_model=TaskRead)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks", response_model=list[TaskRead])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.dict().items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return

@app.patch("/tasks/{task_id}/toggle-completed")
def toggle_task_completed(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    current_completed = getattr(task, 'completed')
    setattr(task, 'completed', not current_completed)
    db.commit()
    return {"completed": getattr(task, 'completed')}

@app.get("/projects/{project_id}/tasks", response_model=list[TaskRead])
def list_tasks_by_project(project_id: int, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.project_id == project_id).all()

# ------------------- Events -------------------
@app.post("/events", response_model=EventRead)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events", response_model=list[EventRead])
def list_events(db: Session = Depends(get_db)):
    return db.query(Event).all()

@app.get("/events/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.put("/events/{event_id}", response_model=EventRead)
def update_event(event_id: int, event: EventCreate, db: Session = Depends(get_db)):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in event.dict().items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(db_event)
    db.commit()
    return 