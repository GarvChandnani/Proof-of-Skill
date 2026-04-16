import hashlib
import os
import json

STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'mock_ipfs_storage')

def init_storage():
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)

def upload_to_mock_ipfs(data_dict):
    """
    Simulates uploading data to IPFS by hashing the serialized JSON content.
    Returns the mock IPFS hash (CID).
    """
    init_storage()
    content = json.dumps(data_dict, sort_keys=True).encode('utf-8')
    # Use SHA-256 to generate a mock CID
    cid = "Qm" + hashlib.sha256(content).hexdigest()[:44]
    
    file_path = os.path.join(STORAGE_DIR, f"{cid}.json")
    with open(file_path, 'wb') as f:
        f.write(content)
        
    return cid

def get_from_mock_ipfs(cid):
    """
    Retrieves data using the mock IPFS hash (CID).
    """
    file_path = os.path.join(STORAGE_DIR, f"{cid}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None
