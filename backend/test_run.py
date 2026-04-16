import urllib.request
import json
import time
import sys

API_URL = "http://127.0.0.1:5000"

def post(url, data):
    req = urllib.request.Request(f"{API_URL}{url}", method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data=json.dumps(data).encode("utf-8")) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}
    except urllib.error.URLError as e:
        print(f"Failed to connect to backend: {e.reason}")
        sys.exit(1)

def get(url):
    try:
        with urllib.request.urlopen(f"{API_URL}{url}") as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}

print("=== Starting Full API Flow Test ===\\n")

# 1. Create Wallets
alice = "0xAAA0000000000000000000000000000000000000"
bob = "0xBBB1111111111111111111111111111111111111"
charlie = "0xCCC2222222222222222222222222222222222222"
dave = "0xDDD3333333333333333333333333333333333333"

print("1. Connecting Wallets (Simulating MetaMask connections)...")
post("/verify-wallet", {"wallet_address": alice})
post("/verify-wallet", {"wallet_address": bob})
post("/verify-wallet", {"wallet_address": charlie})
post("/verify-wallet", {"wallet_address": dave})
print("   Wallets connected successfully.\\n")

# 2. Submit Project
print("2. Alice submits a new Proof of Skill project...")
res = post("/submit-project", {
    "title": "Decentralized Exchange Smart Contract",
    "description": "A comprehensive DEX written in Solidity.",
    "skill_category": "Solidity Development",
    "user_id": alice
})
project_id = res.get("project_id")
print(f"   Project submitted! ID: {project_id}, IPFS Hash: {res.get('ipfs_hash')}\\n")

# 3. Peer Reviews
print("3. Bob, Charlie, and Dave review Alice's project (Consensus requires 3)...")
post("/review", {"project_id": project_id, "reviewer_id": bob, "score": 4, "feedback": "Great contract security."})
print("   Bob gave a score of 4.")

post("/review", {"project_id": project_id, "reviewer_id": charlie, "score": 5, "feedback": "Excellent test coverage."})
print("   Charlie gave a score of 5.")

res3 = post("/review", {"project_id": project_id, "reviewer_id": dave, "score": 4, "feedback": "Good gas optimization."})
print("   Dave gave a score of 4.")
print(f"   Consensus Status: {res3.get('consensus_reached')} | Approved: {res3.get('approved')}\\n")

# 4. Check Alice's Reputation
print("4. Recruiter Dashboard Check for Alice...")
alice_data = get(f"/user/{alice}")
print(f"   Alice's Reputation Score: {alice_data.get('reputation')}")
approved_projects = [p for p in alice_data.get("projects", []) if p["status"] == "approved"]
print(f"   Alice's Approved Skills: {len(approved_projects)}")
if approved_projects:
    print(f"   Skill Verified: {approved_projects[0]['skill_category']} -> {approved_projects[0]['title']}")

print("\\n=== Test Routine Finished ===")
