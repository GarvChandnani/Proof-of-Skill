const API_URL = 'http://127.0.0.1:5000';
let userWalletAddress = null;
let userRole = null;

const connectWalletBtn = document.getElementById('connectWalletBtn');
const walletStatus = document.getElementById('walletStatus');

// Initialize
async function init() {
    if (typeof window.ethereum !== 'undefined') {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
            await handleAccountsChanged(accounts);
        }

        window.ethereum.on('accountsChanged', handleAccountsChanged);
        
        if(connectWalletBtn) {
            connectWalletBtn.addEventListener('click', connectWallet);
        }
    } else {
        if(walletStatus) walletStatus.innerText = 'MetaMask not installed';
    }
}

async function connectWallet() {
    try {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        await handleAccountsChanged(accounts);
    } catch (error) {
        console.error("User denied account access");
    }
}

async function handleAccountsChanged(accounts) {
    if (accounts.length === 0) {
        console.log('Please connect to MetaMask.');
        if(walletStatus) walletStatus.innerText = 'Not Connected';
        userWalletAddress = null;
    } else {
        userWalletAddress = accounts[0];
        if(walletStatus) {
            walletStatus.innerText = `Connected: ${userWalletAddress.substring(0, 6)}...${userWalletAddress.substring(38)}`;
        }
        if(connectWalletBtn) connectWalletBtn.style.display = 'none';
        
        // Verify with backend
        await verifyWallet(userWalletAddress);
        
        // Dispatch custom event for pages to react
        document.dispatchEvent(new CustomEvent('walletConnected', { detail: { address: userWalletAddress, role: userRole } }));
    }
}

async function verifyWallet(address) {
    try {
        const response = await fetch(`${API_URL}/verify-wallet`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wallet_address: address })
        });
        const data = await response.json();
        userRole = data.role;
        // Keep role updated globally or in localStorage if needed
        localStorage.setItem('userRole', userRole);
    } catch (err) {
        console.error("Error verifying wallet:", err);
    }
}

// Ensure init is called
window.addEventListener('load', init);
