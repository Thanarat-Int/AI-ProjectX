import sqlite3
import json
from datetime import datetime

DB_NAME = "data/resume_screener.db"

def init_db():
    """Initializes the SQLite database and migrates schema if needed."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Create Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            filename TEXT,
            match_score INTEGER,
            skills TEXT,
            summary TEXT,
            file_path TEXT
        )
    ''')
    
    # 2. Migration: Check if file_path column exists (for older DB versions)
    c.execute("PRAGMA table_info(history)")
    columns = [info[1] for info in c.fetchall()]
    if "file_path" not in columns:
        print("Migrating Database: Adding file_path column...")
        c.execute("ALTER TABLE history ADD COLUMN file_path TEXT")
        
    conn.commit()
    conn.close()

def save_analysis(filename, analysis_data, file_path=None):
    """Saves the analysis result to the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # safely get data
        score = analysis_data.get('match_score', 0)
        skills = ", ".join(analysis_data.get('key_skills', []))
        summary = analysis_data.get('candidate_summary', '')
        
        c.execute('''
            INSERT INTO history (filename, match_score, skills, summary, file_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, score, skills, summary, file_path))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

def get_history():
    """Retrieves analysis history."""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT id, timestamp, filename, match_score, skills FROM history ORDER BY id DESC')
        data = c.fetchall()
        conn.close()
        return data
    except Exception as e:
        return []

def clear_history():
    """Deletes all records from the history table."""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM history")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")
        return False
    return True
