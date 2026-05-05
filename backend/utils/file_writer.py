import os
import zipfile
import json
from pathlib import Path
import re
import os

BASE_DIR = Path(os.path.expanduser("~/Desktop")) / "generated_projects"

def get_project_dir(project_slug: str) -> Path:
    safe_slug = sanitize_slug(project_slug)
    return BASE_DIR / safe_slug

def write_files(project_slug: str, files: list[dict]) -> dict:
    """
    files: [{"path": "backend/models/user.py", "content": "..."}]
    """
    project_dir = get_project_dir(project_slug)
    written = []
    errors = []

    for file in files:
        try:
            file_path = project_dir / file["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file["content"], encoding="utf-8")
            written.append(file["path"])
        except Exception as e:
            errors.append({"path": file["path"], "error": str(e)})

    return {
        "project_dir": str(project_dir),
        "written": written,
        "errors": errors
    }


def read_file(project_name: str, file_path: str) -> str:
    project_dir = get_project_dir(project_name)
    full_path = project_dir / file_path
    if full_path.exists():
        return full_path.read_text(encoding="utf-8")
    return ""


def list_files(project_name: str) -> list[str]:
    project_dir = get_project_dir(project_name)
    if not project_dir.exists():
        return []
    files = []
    for f in project_dir.rglob("*"):
        if f.is_file():
            files.append(str(f.relative_to(project_dir)))
    return files


def zip_project(project_name: str) -> str:
    project_dir = get_project_dir(project_name)
    zip_path = BASE_DIR / f"{project_name}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in project_dir.rglob("*"):
            if file.is_file():
                zipf.write(file, file.relative_to(project_dir))

    return str(zip_path)


def delete_project(project_name: str):
    import shutil
    project_dir = get_project_dir(project_name)
    if project_dir.exists():
        shutil.rmtree(project_dir)

def sanitize_slug(name: str) -> str:
    name = name.lower()
    name = re.sub(r'[^a-z0-9\-]', '-', name)
    name = re.sub(r'-+', '-', name)
    name = name.strip('-')
    return name
