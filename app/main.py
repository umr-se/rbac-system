# main.py
from fastapi import FastAPI, Depends, Form, HTTPException, status
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from app.database import SessionLocal
import app.models as models, app.schemas as schemas, app.crud as crud
from app.database import engine, get_db
from app.auth import create_access_token, get_current_user, get_current_admin, oauth2_scheme
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
import time
from sqlalchemy.exc import OperationalError
import icalendar

max_retries = 5
retry_delay = 10
for attempt in range(max_retries):
    try:
        models.Base.metadata.create_all(bind=engine)
        break
    except OperationalError:
        if attempt < max_retries - 1:
            print(f"Database connection failed, retrying in {retry_delay}s...")
            time.sleep(retry_delay)
            continue
        raise

app = FastAPI(
    title="RBAC API",
    description="API for user management and calendar events",
    version="2.0"
)



# Add this right after creating the FastAPI app
instrumentator = Instrumentator().instrument(app)

# Add this right before the startup event
@app.on_event("startup")
async def startup():
    instrumentator.expose(app)

@app.get("/")
async def root():
    # return {"message": "Hello World"}
    return {"message": "RBAC API is running!"}
    

@app.on_event("startup")
def startup_admin_check():
    db = SessionLocal()
    try:
        admin_email = "admin@example.com"
        admin = crud.get_user(db, admin_email)
        if not admin:
            admin_data = schemas.UserCreate(
                name="Admin User",
                email=admin_email,
                password="pass123"
            )
            crud.create_user(db, admin_data, is_admin=True)
            db.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

# ---------------------- Authentication Endpoints ----------------------
@app.post("/users/", response_model=schemas.UserResponse, tags=["Users"])
def create_user(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user_data = schemas.UserCreate(name=name, email=email, password=password)
    return crud.create_user(db, user_data)

@app.post("/login", response_model=schemas.Token, tags=["Authentication"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user(db, form_data.username)
    if not user or not crud.pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email, "is_admin": user.is_admin},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ---------------------- User Management Endpoints ----------------------
@app.get("/users/", response_model=list[schemas.UserResponse], tags=["Users"])
def get_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.is_admin:
        return crud.get_users(db)
    return [current_user]

@app.delete("/users/", tags=["Users"])
def delete_users(
    user_id: int = Form(...), 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_admin)
):
    if crud.delete_user(db, user_id):
        return {"message": f"User with ID {user_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/", response_model=schemas.UserResponse, tags=["Users"])
def update_user(
    user_id: int, 
    name: str = Form(...), 
    email: str = Form(...),
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_admin)
):
    updated_user = crud.update_user(db, user_id, name, email)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.post("/admin/create", response_model=schemas.UserResponse, tags=["Admin"])
def create_admin(
    name: str = Form(...), 
    email: str = Form(...), 
    password: str = Form(...),
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_admin)
):
    user_data = schemas.UserCreate(name=name, email=email, password=password)
    return crud.create_user(db, user_data, is_admin=True)

# ---------------------- Calendar Event Endpoints ----------------------
@app.post("/event/", tags=["Events"])
def create_event(
    summary: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    location: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        new_event = models.CalendarEvent(
            summary=summary,
            start_time=datetime.strptime(start_time, "%Y-%m-%d %H:%M"),
            end_time=datetime.strptime(end_time, "%Y-%m-%d %H:%M"),
            location=location,
            owner_id=current_user.id  # Link event to current user
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return {"message": "Event created successfully!", "event_id": new_event.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating event: {str(e)}")

@app.get("/events/", tags=["Events"])
def list_events(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    events = db.query(models.CalendarEvent).offset(skip).limit(limit).all()
    return {"total_events": len(events), "events": events}

@app.get("/event/{event_id}", tags=["Events"])
def get_event(
    event_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    event = db.query(models.CalendarEvent).filter(models.CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.delete("/event/{event_id}", tags=["Events"])
def delete_event(
    event_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    event = db.query(models.CalendarEvent).filter(models.CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}

@app.get("/event/{event_id}/ics", tags=["Events"])
def export_event_as_ics(
    event_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    event = db.query(models.CalendarEvent).filter(models.CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    cal = icalendar.Calendar()
    ical_event = icalendar.Event()
    ical_event.add("summary", event.summary)
    ical_event.add("dtstart", event.start_time)
    ical_event.add("dtend", event.end_time)
    if event.location:
        ical_event.add("location", event.location)

    cal.add_component(ical_event)

    file_path = f"event_{event_id}.ics"
    with open(file_path, "wb") as f:
        f.write(cal.to_ical())

    return FileResponse(
        path=file_path,
        filename=f"event_{event_id}.ics",
        media_type="text/calendar"
    )

@app.get("/", tags=["Root"])
def home():
    return {"message": "RBAC API is running!"}