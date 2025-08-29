import re
from urllib.parse import urlparse, parse_qs
from typing import Optional, Tuple
from app.config import settings
import os
from io import BytesIO
import requests
from datetime import datetime
import pandas as pd


def extract_gdrive_ids(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract (kind, file_id) from a Google Sheets or Google Drive URL.
    kind ∈ {"sheet", "file"} else None.
    """

    try:
        if not url:
            return None, None

        u = urlparse(url)
        host = (u.netloc or "").lower()
        path = u.path or ""
        qs = parse_qs(u.query)

        # Pattern for /d/<file_id>
        m = re.search(r"/d/([a-zA-Z0-9-_]+)", path)

        # Google Sheets
        if "docs.google.com" in host and "/spreadsheets/" in path and m:
            return "sheet", m.group(1)

        # Google Drive file
        if "drive.google.com" in host:
            if m:
                return "file", m.group(1)
            if "id" in qs and qs["id"]:
                return "file", qs["id"][0]

        return None, None

    except Exception as e:
        print(f"error found: {e}")


# download GDrive_Reminder file
def download_reminder_file():
    url_type, file_id = extract_gdrive_ids(settings.Reminder_URL)

    export_url: str = ""

    if url_type == "sheet":
        export_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
    if url_type == "file":
        export_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    # Download the file content
    try:
        response = requests.get(export_url)  # Assign to response
        response.raise_for_status()  # Call the method on response

        # Read excel from memory to get the first sheet name
        file_content = BytesIO(response.content)
        xl = pd.ExcelFile(file_content)
        sheet_name = xl.sheet_names[0]  # Use the first sheet's name as base

        # Reset the pointer for saving
        file_content.seek(0)

        # Create dynamic filename
        current_date = datetime.now().strftime("%Y-%m-%d")
        safe_sheet_name = sheet_name.replace(" ", "_").replace(".", "")  # Make file-safe
        filename = f"{safe_sheet_name}_{current_date}.xlsx"

        # Save with dynamic filename
        folder = settings.Reminder_input_dir
        if not os.path.exists(folder):
            os.makedirs(folder)
        file_path = os.path.join(folder, filename)

        with open(file_path, "wb") as f:
            f.write(file_content.read())

        return True

    except Exception as e:
        return False

