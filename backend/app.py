from flask import Flask, request, jsonify
from flask_cors import CORS
from database import init_db, get_db_connection
from mock_ipfs import upload_to_mock_ipfs
import os

app = Flask(__name__)
CORS(app)

# Initialize database on startup
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'proof_of_skill.db')):
    init_db()

@app.route('/verify-wallet', methods=['POST'])
def verify_wallet():
    data = request.json
    wallet_address = data.get('wallet_address')
    
    if not wallet_address:
        return jsonify({"error": "Missing wallet_address"}), 400
        
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE wallet_address = ?", (wallet_address,))
    user = c.fetchone()
    
    if not user:
        c.execute("INSERT INTO users (wallet_address, username) VALUES (?, ?)", (wallet_address, f"User_{wallet_address[:6]}"))
        conn.commit()
        user_role = 'user'
    else:
        user_role = user['role']
        
    conn.close()
    return jsonify({"success": True, "role": user_role, "wallet_address": wallet_address})

@app.route('/submit-project', methods=['POST'])
def submit_project():
    data = request.json
    title = data.get('title')
    description = data.get('description')
    skill_category = data.get('skill_category')
    user_id = data.get('user_id')
    
    if not all([title, description, skill_category, user_id]):
        return jsonify({"error": "Missing required fields"}), 400
        
    # Upload to mock IPFS
    ipfs_data = {
        "title": title,
        "description": description,
        "skill_category": skill_category,
        "user_id": user_id
    }
    ipfs_hash = upload_to_mock_ipfs(ipfs_data)
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO projects (title, description, ipfs_hash, user_id, skill_category) VALUES (?, ?, ?, ?, ?)",
        (title, description, ipfs_hash, user_id, skill_category)
    )
    conn.commit()
    project_id = c.lastrowid
    conn.close()
    
    return jsonify({"success": True, "project_id": project_id, "ipfs_hash": ipfs_hash})

@app.route('/projects', methods=['GET'])
def get_projects():
    status = request.args.get('status')
    user_id = request.args.get('user_id')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    query = "SELECT * FROM projects WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
        
    c.execute(query, tuple(params))
    projects = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify({"projects": projects})

@app.route('/review', methods=['POST'])
def submit_review():
    data = request.json
    project_id = data.get('project_id')
    reviewer_id = data.get('reviewer_id')
    score = data.get('score')  # 1 to 5
    feedback = data.get('feedback')
    
    if not all([project_id, reviewer_id, score, feedback]):
        return jsonify({"error": "Missing required fields"}), 400
        
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if review already exists
    c.execute("SELECT id FROM reviews WHERE project_id=? AND reviewer_id=?", (project_id, reviewer_id))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "You have already reviewed this project"}), 400
        
    c.execute(
        "INSERT INTO reviews (project_id, reviewer_id, score, feedback) VALUES (?, ?, ?, ?)",
        (project_id, reviewer_id, score, feedback)
    )
    conn.commit()
    
    # Consensus Logic (Min 2 reviews)
    c.execute("SELECT score FROM reviews WHERE project_id = ?", (project_id,))
    reviews = c.fetchall()
    
    consensus_reached = False
    approved = False
    if len(reviews) >= 2:
        avg_score = sum([r['score'] for r in reviews]) / len(reviews)
        status = 'approved' if avg_score >= 3.5 else 'rejected'
        c.execute("UPDATE projects SET status = ? WHERE id = ?", (status, project_id))
        conn.commit()
        consensus_reached = True
        approved = status == 'approved'
        
    conn.close()
    
    return jsonify({
        "success": True, 
        "consensus_reached": consensus_reached,
        "approved": approved
    })

@app.route('/user/<address>', methods=['GET'])
def get_user(address):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE wallet_address = ?", (address,))
    user = c.fetchone()
    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404
        
    user_data = dict(user)
    
    c.execute("SELECT * FROM projects WHERE user_id = ?", (address,))
    projects = [dict(row) for row in c.fetchall()]
    
    c.execute("SELECT score FROM reputation WHERE user_id = ?", (address,))
    rep = c.fetchone()
    user_data['reputation'] = rep['score'] if rep else 0
    user_data['projects'] = projects
    
    conn.close()
    return jsonify(user_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
