# Tasko — Todo App

A clean, dark-themed todo application with a **Python / Flask** backend and an SQLite database.

---

## Project structure

```
tasko/
├── app.py           # Flask application & REST API
├── index.html       # Single-page frontend (served by Flask)
├── requirements.txt # Python dependencies
├── tasks.db         # SQLite database (auto-created on first run)
├── .gitignore
└── README.md
```

---

## Quick start

### 1 — Clone / download the project

```bash
cd tasko
```

### 2 — Create and activate a virtual environment

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Run the server

```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

> The SQLite database (`tasks.db`) is created automatically on the first run.

---

## REST API reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tasks` | List all tasks (newest first) |
| `POST` | `/api/tasks` | Create a task `{ "text": "..." }` |
| `PUT` | `/api/tasks/<id>` | Update text and/or done flag |
| `DELETE` | `/api/tasks/<id>` | Delete a single task |
| `DELETE` | `/api/tasks?done=true` | Delete all completed tasks |

### Task object

```json
{
  "id":        "a3f9...",
  "text":      "Buy groceries",
  "done":      false,
  "createdAt": "2025-05-15T10:30:00Z"
}
```

---

## Production deployment (optional)

Use **gunicorn** instead of the built-in Flask server:

```bash
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

---

## Features

- ✅ Persistent storage via SQLite — tasks survive server restarts
- ✅ Full CRUD — create, read, update (text + done), delete
- ✅ Bulk-clear completed tasks
- ✅ Live search & filter (All / Pending / Completed)
- ✅ Inline editing with keyboard shortcuts (Enter to save, Esc to cancel)
- ✅ Smooth animations for add, complete, and delete
- ✅ CORS headers — works when frontend is on a different dev port
- ✅ WSGI-compatible — `init_db()` runs at import time, not just in `__main__`
"# todo_simpleapp" 
