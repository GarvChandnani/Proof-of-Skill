# Proof of Skill - Blockchain Work Verification

This is a complete decentralized application for submitting, reviewing, and verifying skills on the blockchain using Soulbound NFTs (Non-transferable).

## Features
* Wallet Connection (MetaMask)
* Submit Proof of Work
* Review Submissions (Consensus mechanism: Min 2 reviews)
* Receive Soulbound NFT upon approval
* Recruiter verification dashboard

## Tech Stack
* **Frontend:** Vanilla HTML, CSS, JS + Ethers.js v6
* **Backend:** Python + Flask + SQLite
* **Blockchain:** Solidity + Hardhat

## Instructions to Run Locally

### 1. Smart Contracts
1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the local Hardhat node:
   ```bash
   npx hardhat node
   ```
3. Open a new terminal and deploy contracts to the local network:
   ```bash
   npx hardhat run scripts/deploy.js --network localhost
   ```

### 2. Backend API
1. Open a new terminal and navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask server:
   ```bash
   python app.py
   ```

### 3. Frontend
Use a web server like Live Server (VSCode extension) or Python's HTTP server to run the frontend:
```bash
cd frontend
python -m http.server 8000
```
Open your browser and navigate to `http://localhost:8000`.

### Workflow
1. Use MetaMask to connect (make sure it's on the Localhost 8545 network).
2. Register a project on the **Submit Work** page.
3. Switch MetaMask to 2 different accounts and use the **Review** page to submit scores.
4. Go to **Dashboard** or **Recruiter** page to verify the minted credential once approved.
