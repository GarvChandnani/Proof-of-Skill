import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'proof_of_skill.db')

def sync():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT id FROM projects WHERE status = 'pending'")
    pending_projects = c.fetchall()
    
    print(f"Checking {len(pending_projects)} pending projects...")
    
    for p in pending_projects:
        pid = p['id']
        c.execute("SELECT score FROM reviews WHERE project_id = ?", (pid,))
        reviews = c.fetchall()
        
        num_reviews = len(reviews)
        if num_reviews >= 2:
            avg_score = sum([r['score'] for r in reviews]) / num_reviews
            status = 'approved' if avg_score >= 3.5 else 'rejected'
            
            c.execute("UPDATE projects SET status = ? WHERE id = ?", (status, pid))
            print(f"Project ID {pid}: Consensus reached ({num_reviews} reviews). New status: {status}")
        else:
            print(f"Project ID {pid}: Still waiting for reviews ({num_reviews}/2).")
            
    conn.commit()
    conn.close()
    print("Sync complete.")

if __name__ == '__main__':
    sync()
