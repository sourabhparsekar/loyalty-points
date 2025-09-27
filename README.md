# Fastfood-Style DApp (Polygon Amoy) — README

## Goal (simple): 

Build a Fastfood-style web app (Streamlit) where users can add default products to cart, checkout to automatically receive 10% ERC‑20 reward tokens of the purchase amount and an ERC‑721 NFT when purchase amount > 500 (test network units). Deploy contracts on Polygon Amoy via Alchemy.

## Network details you will use (Amoy testnet):

RPC URL: https://rpc-amoy.polygon.technology/.

Chain ID: 80002. These are Polygon Amoy testnet settings. 

## Prerequisites 

### Python 
1. Go to the official Python site: https://www.python.org/downloads/windows/
2. Download the latest Python 3.10 or 3.11 (64-bit) installer.
3. Run installer → check the box ✅ “Add Python to PATH” → then click Install Now.
4. Verify installation:
`python --version`

_You should see something like Python 3.11.9._

### Sol
We’ll use solc (Solidity compiler) via npm.

1. Install Node.js (includes npm):
   - Download Windows installer: https://nodejs.org/
   - Install LTS version (e.g., 20.x).
2. Install solc globally:
`npm install -g solc`
3. Check:
`solcjs --version`

### Brownie (Smart Contract Framework)

Brownie is Python-based and works on Windows through WSL (Windows Subsystem for Linux) OR using Anaconda + pip. Since you’re non-technical, let’s stick with pip:

1. First install Git (needed):
https://git-scm.com/download/win

2. Open PowerShell and run:
`pip install eth-brownie`

3. Verify:
`brownie --version`

You should see something like: Brownie v1.19.x.

⚠️ If brownie command fails on Windows, the easiest alternative is use Anaconda:
```
pip install virtualenv
python -m venv venv
.\venv\Scripts\activate
pip install eth-brownie
```

#### Private Key from MetaMask
1. Click on the account selector at the top of your screen.
2. Click the three vertical dots next to the account you want to export and select 'Account details'.
3. Click 'Private key' and enter your MetaMask password to confirm.
4. Click and hold on 'Hold to reveal Private Key' to display your private key.
5. Click to copy the private key to your clipboard. Make sure to save it somewhere safe.
6. Click 'Done' to close the screen.

### Streamlit 

1. Createpython virtualenvironment
`python -m venv .venv`

2. Activate virtual environment in linux
`source .venc/bin/activate`

3. 
`pip install -r requirements.txt`

4. Run application:installproject dependencies
`streamlit run streamlit_app/app.py`
It should open in your browser.

✅ At this point, you’ll have:
- Python (for scripting + frontend),
- Solidity compiler (to build contracts),
- Brownie (to deploy contracts on Polygon Amoy via Alchemy),
- Streamlit (to make the transactions).

## Project Compilation

### Compile Contracts 

`brownie pm install OpenZeppelin/openzeppelin-contracts@4.9.0`

`brownie compile`

#### Solidity smart contracts: 
- RewardToken.sol (ERC20) 
- RewardNFT.sol (ERC721) 
- KFCShop.sol (shop logic).

### Deployment Script
A Python deployment script using Brownie (Python-friendly) and configuration to use Alchemy RPC.

`brownie run scripts/deploy.py --network amoy`

### Web App
A Streamlit app (app.py) using web3.py to show products, cart, checkout, and interact with WalletConnect / manual private-key signing for testing.

## Issues 

### Install Microsoft C++ Build Tools for brownie

1. Go to: Microsoft C++ Build Tools Download
2. Download and install Build Tools for Visual Studio 2022.
3. During installation, select ✅ Desktop development with C++ workload.
4. Make sure “MSVC v143 build tools”, “Windows 10 SDK”, and “C++ CMake tools” are checked.
5. Restart your computer after installation.

### Manually add network 
- Polygon Amoy
`brownie networks add Polygon polygon_amoy host=https://polygon-amoy.g.alchemy.com/v2/<ALCHEMY_KEY_HERE> chainid=80002 explorer=https://api-amoy.polygonscan.com/api`

- Local Ganache UI - https://archive.trufflesuite.com/ganache/
`brownie networks add Ethereum ganache_local host=http://127.0.0.1:7545 chainid=5777`

```
brownie networks add Polygon polygon_amoy \
  host=https://polygon-amoy.g.alchemy.com/v2/<ALCHEMY_KEY_HERE> \
  chainid=80002 \
  explorer=https://api-amoy.polygonscan.com/api
```
- list networks
`brownie networks list`
