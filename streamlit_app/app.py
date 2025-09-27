import streamlit as st
from web3 import Web3
import json

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="🍗 KFC Loyalty Portal", layout="wide")

# ---------------------------
# Config
# ---------------------------
RPC_URL = st.secrets["RPC_URL"]
SHOP_ADDRESS = st.secrets["SHOP_ADDRESS"]
SHOP_PRIVATE_KEY = st.secrets["SHOP_PRIVATE_KEY"]
BUYER_ADDRESS = st.secrets["BUYER_ADDRESS"]

# Load ABIs
with open("build/contracts/KFCShop.json") as f:
    shop_abi = json.load(f)["abi"]
with open("build/contracts/RewardToken.json") as f:
    token_abi = json.load(f)["abi"]
with open("build/contracts/RewardNFT.json") as f:
    nft_abi = json.load(f)["abi"]

# Web3 setup
w3 = Web3(Web3.HTTPProvider(RPC_URL))
shop = w3.eth.contract(address=Web3.to_checksum_address(SHOP_ADDRESS), abi=shop_abi)
reward_token = w3.eth.contract(address=shop.functions.rewardToken().call(), abi=token_abi)
reward_nft = w3.eth.contract(address=shop.functions.rewardNFT().call(), abi=nft_abi)

# ---------------------------
# Session State
# ---------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# Utility Functions
# ---------------------------
def add_message(msg):
    st.session_state.messages.insert(0, msg)
    if len(st.session_state.messages) > 10:
        st.session_state.messages.pop()

def show_notifications():
    with st.session_state.notif_placeholder.container():
        if st.session_state.messages:
            for msg in st.session_state.messages:
                st.info(msg)
        else:
            st.info("No notifications yet.")

def refresh_balances(buyer):
    try:
        token_balance = reward_token.functions.balanceOf(buyer).call() / 1e18
        nft_count = reward_nft.functions.balanceOf(buyer).call()
    except:
        token_balance, nft_count = 0, 0
    return token_balance, nft_count

def owner_address():
    return w3.eth.account.from_key(SHOP_PRIVATE_KEY).address

def send_tx(tx):
    signed_tx = w3.eth.account.sign_transaction(tx, SHOP_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash, receipt

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("🔔 Notifications")
if "notif_placeholder" not in st.session_state:
    st.session_state.notif_placeholder = st.sidebar.empty()

buyer_address = st.sidebar.text_input("Buyer Wallet Address", value=BUYER_ADDRESS)
st.sidebar.markdown("---")
st.sidebar.write("### 🔄 Actions")
if st.sidebar.button("Refresh Balances"):
    st.session_state.messages = []
    add_message("💡 Balances refreshed.")

show_notifications()

# ---------------------------
# Main App
# ---------------------------
st.title("🍗 KFC Loyalty Portal")
st.markdown("Earn KFC Tokens and NFTs with every purchase!")

# ---------------------------
# Tabs
# ---------------------------
tabs = st.tabs(["💼 Wallet Dashboard", "🛒 Shop / Cart"])

# ---------------------------
# Tab 1: Wallet Dashboard
# ---------------------------
with tabs[0]:
    st.header("💼 Wallet Dashboard")
    token_balance, nft_count = refresh_balances(buyer_address)
    col1, col2 = st.columns(2)
    col1.metric("💰 KFC Tokens", f"{token_balance:.2f} KFC")
    col2.metric("🎟️ NFTs Owned", nft_count)

# ---------------------------
# Tab 2: Shop / Cart
# ---------------------------
with tabs[1]:
    st.header("🛒 KFC Menu")
    products = [
        {"id": 1, "name": "Veg Nuggets", "price": 120, "image": "assets/chilly.jpg"},
        {"id": 2, "name": "Fry & Chips Meal", "price": 300, "image": "assets/dry_fry_chips.jpg"},
        {"id": 3, "name": "Crispy Fries", "price": 150, "image": "assets/crispy.jpg"},
        {"id": 4, "name": "Strips", "price": 100, "image": "assets/wings.jpg"},
    ]

    cols = st.columns(2)
    for idx, p in enumerate(products):
        with cols[idx % 2]:
            st.image(p["image"], width=200)
            st.markdown(f"**{p['name']}** — {p['price']} units")
            if st.button(f"Add {p['name']}", key=f"add{p['id']}"):
                st.session_state.cart.append(p)
                st.session_state.messages = []  # clear old notifications
                add_message(f"🛒 Added {p['name']} to cart.")
                show_notifications()

    st.subheader("🛍️ Your Cart")
    if st.session_state.cart:
        total_units = sum(item["price"] for item in st.session_state.cart)
        for item in st.session_state.cart:
            st.write(f"- {item['name']} ({item['price']} units)")
        st.write(f"**Total: {total_units} units**")

        if st.button("Checkout"):
            try:
                st.session_state.messages = []  # clear old notifications
                tx = shop.functions.buyFor(buyer_address, total_units).build_transaction({
                    "chainId": w3.eth.chain_id,
                    "from": owner_address(),
                    "nonce": w3.eth.get_transaction_count(owner_address(), "pending"),
                    "gas": 500000,
                    "gasPrice": w3.to_wei("50", "gwei")
                })
                tx_hash, receipt = send_tx(tx)
                add_message(f"✅ Purchase successful! Tx: {tx_hash.hex()}")

                # Clear cart after successful checkout
                st.session_state.cart = []

                # Refresh balances
                token_balance, nft_count = refresh_balances(buyer_address)
                show_notifications()
            except Exception as e:
                add_message(f"❌ Transaction failed: {e}")
                show_notifications()
    else:
        st.info("Your cart is empty.")
