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
    
    # Normalize skill_category: if list, store as JSON; if string, make it a list then JSON
    if isinstance(skill_category, list):
        skills_json = json.dumps(skill_category)
    else:
        skills_json = json.dumps([s.strip() for s in skill_category.split(',') if s.strip()])
    
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
        (title, description, ipfs_hash, user_id, skills_json)
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
    
    # Enhanced query to get author details and reputation
    query = """
        SELECT p.*, u.username as author_name, r.score as author_rep
        FROM projects p
        JOIN users u ON p.user_id = u.wallet_address
        LEFT JOIN reputation r ON p.user_id = r.user_id
        WHERE 1=1
    """
    params = []
    if status:
        query += " AND p.status = ?"
        params.append(status)
    if user_id:
        query += " AND p.user_id = ?"
        params.append(user_id)
        
    c.execute(query, tuple(params))
    projects = [dict(row) for row in c.fetchall()]
    
    import json
    for p in projects:
        try:
            p['skills'] = json.loads(p['skill_category'])
        except:
            p['skills'] = [p['skill_category']]
        
        # Default rep if NULL
        if p.get('author_rep') is None:
            p['author_rep'] = 0
            
    conn.close()
    
    return jsonify({"projects": projects})

@app.route('/review', methods=['POST'])
def submit_review():
    data = request.json
    project_id = data.get('project_id')
    reviewer_id = data.get('reviewer_id')
    score = data.get('score')  
    feedback = data.get('feedback')
    verified_skills = data.get('verified_skills', []) # List of skills the reviewer checked
    
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
        "INSERT INTO reviews (project_id, reviewer_id, score, feedback, verified_skills) VALUES (?, ?, ?, ?, ?)",
        (project_id, reviewer_id, score, feedback, json.dumps(verified_skills))
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
    
    # Process project skills and check consensus
    import json
    from collections import Counter
    
    for p in projects:
        try:
            p['skills'] = json.loads(p['skill_category'])
        except:
            p['skills'] = [p['skill_category']]
            
        if p['status'] == 'approved':
            # Calculate skills that have > 50% verification consensus
            c.execute("SELECT verified_skills FROM reviews WHERE project_id = ?", (p['id'],))
            rev_skills_data = c.fetchall()
            skill_counts = Counter()
            for row in rev_skills_data:
                try:
                    checked = json.loads(row['verified_skills'])
                    for s in checked: skill_counts[s] += 1
                except: pass
            
            p['verified_skills'] = [s for s, count in skill_counts.items() if count >= 2]
        else:
            p['verified_skills'] = []
    
    c.execute("SELECT score FROM reputation WHERE user_id = ?", (address,))
    rep = c.fetchone()
    user_data['reputation'] = rep['score'] if rep else 0
    user_data['projects'] = projects
    
    conn.close()
    return jsonify(user_data)

import json
if __name__ == '__main__':
    app.run(debug=True, port=5000)
