import streamlit as st
from web3 import Web3
import json

st.set_page_config(page_title="🍗 KFC Shop", layout="wide")

# ---------------------------
# Config
# ---------------------------
RPC_URL = st.secrets["RPC_URL"]
SHOP_ADDRESS = st.secrets["SHOP_ADDRESS"]
SHOP_PRIVATE_KEY = st.secrets["SHOP_PRIVATE_KEY"]
BUYER_ADDRESS = st.secrets["BUYER_ADDRESS"]

with open("build/contracts/KFCShop.json") as f:
    shop_abi = json.load(f)["abi"]

w3 = Web3(Web3.HTTPProvider(RPC_URL))
shop = w3.eth.contract(address=Web3.to_checksum_address(SHOP_ADDRESS), abi=shop_abi)

# ---------------------------
# Buyer Input
# ---------------------------
buyer_address = st.sidebar.text_input(
    "Buyer Wallet Address",
    value=BUYER_ADDRESS
)

# ---------------------------
# Products
# ---------------------------
products = [
    {"id": 1, "name": "Veg Nuggets", "price": 120, "image": "assets/chilly.jpg"},
    {"id": 2, "name": "Fry & Chips Meal", "price": 300, "image": "assets/dry_fry_chips.jpg"},
    {"id": 3, "name": "Crispy Fries", "price": 150, "image": "assets/crispy.jpg"},
    {"id": 4, "name": "Strips", "price": 100, "image": "assets/wings.jpg"},
]

if "cart" not in st.session_state:
    st.session_state.cart = []

st.title("🍗 KFC DApp Shop (Owner-Signed Checkout)")

cols = st.columns(2)
for idx, p in enumerate(products):
    with cols[idx % 2]:
        st.image(p["image"], width=200)
        st.write(f"**{p['name']}** — {p['price']} units")
        if st.button(f"Add {p['name']}", key=f"add{p['id']}"):
            st.session_state.cart.append(p)

# ---------------------------
# Cart & Checkout
# ---------------------------
st.header("🛒 Cart")
total_units = sum(item["price"] for item in st.session_state.cart)

if st.session_state.cart:
    for item in st.session_state.cart:
        st.write(f"- {item['name']} ({item['price']} units)")
    st.write(f"**Total: {total_units} units**")

    if st.button("✅ Checkout (Owner-Signed)"):
        if not buyer_address or not w3.is_address(buyer_address):
            st.error("Please enter a valid Ethereum address!")
        else:
            try:
                # Owner account (EOA) — must match private key
                OWNER_ADDRESS = w3.eth.account.from_key(SHOP_PRIVATE_KEY).address
                
                st.write("On-chain owner:", shop.functions.owner().call())
                st.write("Signer address from SHOP_PRIVATE_KEY:", OWNER_ADDRESS)
                st.write("Contract address in use:", shop.address)

                # Build transaction to call buyFor(buyer, amount)
                tx = shop.functions.buyFor(buyer_address, total_units).build_transaction({
                    "chainId": w3.eth.chain_id,
                    "from": OWNER_ADDRESS,
                    "nonce": w3.eth.get_transaction_count(OWNER_ADDRESS, "pending"),
                    "gas": 500000,
                    "gasPrice": w3.to_wei("50", "gwei")
                })

                # Sign with shop's private key
                signed_tx = w3.eth.account.sign_transaction(tx, private_key=SHOP_PRIVATE_KEY)

                # Send transaction
                tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                print(f"Transaction sent.Hash: {tx_hash.hex()}")

                # wait for mining
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"Transaction mined. Status: {receipt.status}")

                st.success(f"✅ Purchase successful!")
                st.write(f"Transaction Hash: {tx_hash.hex()}")
                st.write(f"Tokens and NFTs minted to: {buyer_address}")

                st.json(dict(
                    txHash=tx_hash.hex(),
                    block=receipt.blockNumber,
                    gasUsed=receipt.gasUsed,
                    status=receipt.status
                ))

                

                # Clear cart
                st.session_state.cart = []
            except Exception as e:
                st.error(f"Transaction failed: {e}")
else:
    st.info("Your cart is empty.")
