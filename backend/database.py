import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'proof_of_skill.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            wallet_address TEXT PRIMARY KEY,
            username TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Create Projects table
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            ipfs_hash TEXT NOT NULL,
            user_id TEXT NOT NULL,
            skill_category TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users (wallet_address)
        )
    ''')
    
    # Create Reviews table
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            reviewer_id TEXT NOT NULL,
            score INTEGER NOT NULL,
            feedback TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (reviewer_id) REFERENCES users (wallet_address),
            UNIQUE(project_id, reviewer_id)
        )
    ''')
    
    # Create Reputation table
    c.execute('''
        CREATE TABLE IF NOT EXISTS reputation (
            user_id TEXT PRIMARY KEY,
            score INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (wallet_address)
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
