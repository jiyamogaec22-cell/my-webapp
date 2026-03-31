# ============================================
# MAIN.PY — FastAPI with SQLite database
# ============================================
from database import create_tables, get_connection, hash_password, check_password
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import uvicorn
from database import create_tables, get_connection

# ── Create app ────────────────────────────────────
app = FastAPI()

# ── CORS ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Create tables when app starts ─────────────────
create_tables()

# ── Data models ───────────────────────────────────
class LoginData(BaseModel):
    username: str
    password: str

class SignupData(BaseModel):
    name:     str
    email:    str
    password: str

class TaskData(BaseModel):
    text: str

class ContactData(BaseModel):
    name:    str
    email:   str
    message: str

# ════════════════════════════════════════════════
# LOGIN ROUTES (same as before)
# ════════════════════════════════════════════════
# ── SIGNUP — now saves to database with hashed password ──
@app.post("/signup")
def signup(data: SignupData):

    # Check password length
    if len(data.password) < 6:
        return {"success": False, "message": "Password must be 6+ characters!"}

    conn = get_connection()

    # Check if username already exists
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?", (data.name,)
    ).fetchone()

    if existing:
        conn.close()
        return {"success": False, "message": "Username already taken!"}

    # Hash the password before saving!
    hashed = hash_password(data.password)

    # Save to database
    conn.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (data.name, hashed)
    )
    conn.commit()
    conn.close()

    return {"success": True, "message": "Account created for " + data.name + "!"}


# ── LOGIN — checks password against hash in database ──
@app.post("/login")
def login(data: LoginData):
    conn = get_connection()

    # Find user in database
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (data.username,)
    ).fetchone()
    conn.close()

    if user is None:
        return {"success": False, "message": "Username not found!"}

    # Compare typed password with stored hash
    if check_password(data.password, user["password"]):
        return {"success": True,  "message": "Welcome back, " + data.username + "!"}
    else:
        return {"success": False, "message": "Wrong password!"}
# ════════════════════════════════════════════════
# TASK ROUTES — now using SQLite!
# ════════════════════════════════════════════════

# CREATE a task
@app.post("/tasks")
def create_task(data: TaskData):
    conn = get_connection()
    conn.execute(
        "INSERT INTO tasks (text, done) VALUES (?, ?)",
        (data.text, 0)
    )
    conn.commit()
    conn.close()
    return {"success": True}

# READ all tasks
@app.get("/tasks")
def get_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    tasks = [{"id": r["id"], "text": r["text"], "done": bool(r["done"])} for r in rows]
    return {"tasks": tasks}

# UPDATE a task (flip done)
@app.put("/tasks/{task_id}")
def update_task(task_id: int):
    conn = get_connection()
    row  = conn.execute("SELECT done FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        conn.close()
        return {"success": False, "message": "Task not found"}
    new_done = 0 if row["done"] else 1   # flip 0→1 or 1→0
    conn.execute("UPDATE tasks SET done = ? WHERE id = ?", (new_done, task_id))
    conn.commit()
    conn.close()
    return {"success": True}

# DELETE a task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# ════════════════════════════════════════════════
# CONTACT ROUTES — now using SQLite!
# ════════════════════════════════════════════════

# Save a message
@app.post("/contact")
def save_message(data: ContactData):
    conn = get_connection()
    conn.execute(
        "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
        (data.name, data.email, data.message)
    )
    conn.commit()
    conn.close()
    return {"success": True}

# View all messages
@app.get("/contact")
def get_messages():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM messages").fetchall()
    conn.close()
    messages = [{"id": r["id"], "name": r["name"], "email": r["email"], "message": r["message"]} for r in rows]
    return {"messages": messages}

# ── Run server ────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)