import sqlite3
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import hashlib

app = FastAPI(title="CampusFind API")

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.environ.get("DATABASE_PATH", "campusfind.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT,
            desc TEXT,
            emoji TEXT,
            reporter TEXT,
            email TEXT,
            color TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

class UserSignup(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class Item(BaseModel):
    id: Optional[int] = None
    type: str
    name: str
    category: str
    location: str
    date: str
    time: Optional[str] = None
    desc: Optional[str] = None
    emoji: str
    reporter: str
    email: str
    color: str

@app.get("/items", response_model=List[Item])
def get_items():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@app.post("/items", response_model=Item)
def create_item(item: Item):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO items (type, name, category, location, date, time, desc, emoji, reporter, email, color)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item.type, item.name, item.category, item.location, item.date, item.time, 
        item.desc, item.emoji, item.reporter, item.email, item.color
    ))
    conn.commit()
    item.id = cursor.lastrowid
    conn.close()
    return item

@app.post("/signup", response_model=UserResponse)
def signup(user: UserSignup):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
        
    password_hash = hash_password(user.password)
    try:
        cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", 
                       (user.name, user.email, password_hash))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return UserResponse(id=user_id, name=user.name, email=user.email)
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Database error")

@app.post("/login", response_model=UserResponse)
def login(user: UserLogin):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    password_hash = hash_password(user.password)
    cursor.execute("SELECT id, name, email FROM users WHERE email = ? AND password_hash = ?", 
                   (user.email, password_hash))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return UserResponse(id=row[0], name=row[1], email=row[2])
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")

# Serve Frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(ROOT_DIR, "Frontend.html"))

@app.get("/Frontend.html")
def serve_frontend():
    return FileResponse(os.path.join(ROOT_DIR, "Frontend.html"))

@app.get("/auth.html")
def serve_auth():
    return FileResponse(os.path.join(ROOT_DIR, "auth.html"))
