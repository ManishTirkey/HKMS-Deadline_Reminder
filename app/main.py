from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from threading import Thread, Event
import time
import os
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlalchemy.exc

# Assuming you have a 'templates' folder with 'index.html' inside
templates = Jinja2Templates(directory="templates")

# Import from the new structure
from app.services.database_service import create_tables
from app.api.routes import router
from app.models.database_models import HKMSServiceCategory, get_sessionlocal
from app.config import settings
from app.services.Reminder_service import download_reminder_file
from fastapi import HTTPException


def monitor_service_categories(stop_event: Event, interval: int = 60):
    try:
        folder = settings.Reminder_input_dir
        SessionLocal = get_sessionlocal()

        while not stop_event.is_set():
            success = download_reminder_file()
            if not success:
                # raise HTTPException(status_code=500, detail="Failed to download sheet")
                print("Failed to download code")

            # Find all .xlsx files in the folder
            files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.xlsx')]
            if not files:
                print("No XLSX files found in folder. Waiting for next check...")
                time.sleep(interval)
                continue

            # Get the most recently modified file
            latest_file = max(files, key=os.path.getmtime)
            print(f"Processing latest file: {latest_file}")

            df = pd.read_excel(latest_file, skiprows=0)

            if "Service Category" not in df.columns:
                print("Column 'Service Category' not found in the sheet")
                time.sleep(interval)
                continue

            service_col_index = df.columns.get_loc("Service Category")

            service_categories = df.iloc[:, service_col_index].dropna().unique().tolist()

            print(service_categories)
            db = SessionLocal()

            new_categories = []
            for category in service_categories:
                exists = db.query(HKMSServiceCategory).filter(HKMSServiceCategory.category_name == category).first()
                if not exists:
                    new_cat = HKMSServiceCategory(category_name=category)
                    db.add(new_cat)
                    new_categories.append(category)
            if new_categories:
                db.commit()
                print(f"Added new service categories from {latest_file}: {new_categories}")
            db.close()

        time.sleep(interval)

    except Exception as e:
        print(f"error found: {e}")


stop_event = Event()


# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Startup: Create tables and start monitoring
        success, message = create_tables()
        if success:
            print("database created successfully")
        else:
            raise Exception("Failed to create database")

        monitor_thread = Thread(target=monitor_service_categories, args=(stop_event, 60), daemon=True)
        monitor_thread.start()
        yield
        # Shutdown: Stop monitoring
        stop_event.set()
        monitor_thread.join()
    except Exception as e:
        print(f"error found: {e}")


app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Root route - accessible at /
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("reminder_welcome_page.html", {"request": request})


# Include API routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    print("Starting the app")


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutdown the app")
