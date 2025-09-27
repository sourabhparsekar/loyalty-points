# streamlit_app.py
import streamlit as st
from web3 import Web3
import json
import os
from uuid import uuid4
from datetime import datetime

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(page_title="🍗 KFC Loyalty Portal", layout="wide")

# ---------------------------
# Config (from st.secrets)
# ---------------------------
RPC_URL = st.secrets["RPC_URL"]
SHOP_ADDRESS = Web3.to_checksum_address(st.secrets["SHOP_ADDRESS"])
SHOP_PRIVATE_KEY = st.secrets["SHOP_PRIVATE_KEY"]

# ---------------------------
# Paths
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")

# ---------------------------
# Load ABIs
# ---------------------------
with open(os.path.join(BASE_DIR, "../build/contracts/KFCShop.json")) as f:
    shop_abi = json.load(f)["abi"]
with open(os.path.join(BASE_DIR, "../build/contracts/RewardToken.json")) as f:
    token_abi = json.load(f)["abi"]
with open(os.path.join(BASE_DIR, "../build/contracts/RewardNFT.json")) as f:
    nft_abi = json.load(f)["abi"]

# ---------------------------
# Web3 setup
# ---------------------------
w3 = Web3(Web3.HTTPProvider(RPC_URL))
shop = w3.eth.contract(address=SHOP_ADDRESS, abi=shop_abi)
reward_token = w3.eth.contract(address=shop.functions.rewardToken().call(), abi=token_abi)
reward_nft = w3.eth.contract(address=shop.functions.rewardNFT().call(), abi=nft_abi)

# ---------------------------
# Session state defaults
# ---------------------------
st.session_state.setdefault("cart", [])
st.session_state.setdefault("messages", [])
st.session_state.setdefault("redeem_requests", [])
st.session_state.setdefault("buyer_address", "")
st.session_state.setdefault("token_balance", 0)
st.session_state.setdefault("nft_count", 0)

# ---------------------------
# Helper: notifications
# ---------------------------
def add_message(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    st.session_state.messages.insert(0, f"[{ts}] {msg}")
    if len(st.session_state.messages) > 12:
        st.session_state.messages.pop()

def show_notifications():
    st.sidebar.markdown("### 🔔 Notifications")
    if st.session_state.messages:
        for m in st.session_state.messages:
            st.sidebar.info(m)
    else:
        st.sidebar.info("No notifications yet.")

# ---------------------------
# Web3 helpers
# ---------------------------
def owner_address():
    return w3.eth.account.from_key(SHOP_PRIVATE_KEY).address

def send_tx(tx):
    signed_tx = w3.eth.account.sign_transaction(tx, SHOP_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash, receipt

def refresh_balances(buyer):
    try:
        token_balance = reward_token.functions.balanceOf(buyer).call() / 1e18
        nft_count = reward_nft.functions.balanceOf(buyer).call()
    except Exception:
        token_balance, nft_count = 0, 0
    st.session_state.token_balance = token_balance
    st.session_state.nft_count = nft_count
    return token_balance, nft_count

# ---------------------------
# Buyer address input
# ---------------------------
st.sidebar.markdown("## 👤 Buyer Address")
buyer_address_input = st.sidebar.text_input(
    "Enter Ethereum wallet address", value=st.session_state.buyer_address
)

if buyer_address_input:
    try:
        st.session_state.buyer_address = Web3.to_checksum_address(buyer_address_input)
    except Exception:
        st.sidebar.error("Invalid Ethereum address")
        st.session_state.buyer_address = ""

# ---------------------------
# App header
# ---------------------------
st.title("🍗 KFC Loyalty Portal")
st.markdown("Shop, earn KFC tokens & NFTs — rewards are minted by the shop (owner-signed).")

# ---------------------------
# Tabs
# ---------------------------
tabs = st.tabs(["💼 Wallet", "🛒 Shop & Cart", "🎁 Redeem", "🏅 Badges"])

# ---------------------------
# TAB 1: Wallet
# ---------------------------
with tabs[0]:
    st.header("💼 Wallet Dashboard")
    buyer_addr = st.session_state.buyer_address
    if buyer_addr:
        if st.button("🔄 Refresh Balance"):
            refresh_balances(buyer_addr)
        token_balance = st.session_state.token_balance
        nft_count = st.session_state.nft_count

        c1, c2, c3 = st.columns([1,1,2])
        c1.metric("💰 KFC Tokens", f"{token_balance:.2f} KFC")
        c2.metric("🎟 NFTs Owned", nft_count)
        c3.write(f"Shop contract: `{SHOP_ADDRESS}`")
    else:
        st.info("Enter a valid buyer address in the sidebar to view balances.")

# ---------------------------
# TAB 2: Shop & Cart
# ---------------------------
with tabs[1]:
    st.header("🛒 KFC Menu")
    products = [
        {"id": 1, "name": "Veg Nuggets", "price": 120, "image": os.path.join(ASSETS_DIR, "chilly.jpg")},
        {"id": 2, "name": "Fry & Chips Meal", "price": 300, "image": os.path.join(ASSETS_DIR, "dry_fry_chips.jpg")},
        {"id": 3, "name": "Crispy Fries", "price": 150, "image": os.path.join(ASSETS_DIR, "crispy.jpg")},
        {"id": 4, "name": "Strips", "price": 100, "image": os.path.join(ASSETS_DIR, "wings.jpg")},
    ]

    cols = st.columns(4)
    for idx, p in enumerate(products):
        with cols[idx % 4]:
            st.image(p["image"], width=150)
            st.markdown(f"**{p['name']}**")
            st.caption(f"{p['price']} units")
            if st.button(f"Add {p['name']}", key=f"add{p['id']}"):
                st.session_state.cart.append(p)
                add_message(f"🛒 Added {p['name']} to cart.")
                show_notifications()

    st.subheader("🛍️ Your Cart")
    if st.session_state.cart:
        total = sum(item["price"] for item in st.session_state.cart)
        for idx, item in enumerate(st.session_state.cart):
            c = st.columns([3,2,1])
            c[0].write(item["name"])
            c[1].write(f"{item['price']} units")
            if c[2].button("Remove", key=f"remove{idx}"):
                st.session_state.cart.pop(idx)
                add_message(f"🗑️ Removed {item['name']} from cart.")
                show_notifications()
                st.experimental_rerun()

        st.markdown("---")
        st.subheader(f"💰 Total: {total} units")

        if st.button("✅ Checkout"):
            buyer_addr = st.session_state.buyer_address
            if buyer_addr:
                try:
                    tx = shop.functions.buyFor(
                        buyer_addr, total
                    ).build_transaction({
                        "chainId": w3.eth.chain_id,
                        "from": owner_address(),
                        "nonce": w3.eth.get_transaction_count(owner_address(), "pending"),
                        "gas": 500000,
                        "gasPrice": w3.to_wei("50", "gwei")
                    })
                    tx_hash, receipt = send_tx(tx)
                    add_message(f"✅ Checkout successful! Tx: {tx_hash.hex()}")
                    st.session_state.cart = []
                    refresh_balances(buyer_addr)
                    show_notifications()
                except Exception as e:
                    add_message(f"❌ Checkout failed: {e}")
                    show_notifications()
            else:
                st.warning("Enter a valid buyer address in the sidebar to checkout.")
    else:
        st.info("Your cart is empty.")

# ---------------------------
# Buyer private key input (hidden)
# ---------------------------
st.sidebar.markdown("## 🔑 Buyer Private Key (for redeem)")
buyer_private_key_input = st.sidebar.text_input(
    "Enter buyer private key", type="password", value=""
)
st.session_state.buyer_private_key = buyer_private_key_input if buyer_private_key_input else None

# ---------------------------
# TAB 3: Redeem Tokens
# ---------------------------
with tabs[2]:
    st.header("🎁 Redeem Tokens for Coupons")
    buyer_addr = st.session_state.buyer_address
    buyer_pk = st.session_state.buyer_private_key

    if buyer_addr:
        if st.button("🔄 Refresh Balance", key="refresh_redeem"):
            refresh_balances(buyer_addr)

        token_balance = st.session_state.token_balance
        st.write(f"Your KFC token balance: **{token_balance:.2f} KFC**")

        amount = st.number_input("Tokens to redeem", min_value=10.0, step=10.0, value=100.0)
        if st.button("Redeem Now (Signed by buyer)"):
            if token_balance < amount:
                st.error("Insufficient token balance")
            else:
                try:
                    if not buyer_pk:
                        st.warning("Please enter your private key in the sidebar to redeem tokens")
                    else:
                        # On-chain transfer from buyer to shop
                        tx = reward_token.functions.transfer(
                            SHOP_ADDRESS, int(amount * 1e18)
                        ).build_transaction({
                            "chainId": w3.eth.chain_id,
                            "from": buyer_addr,
                            "nonce": w3.eth.get_transaction_count(buyer_addr, "pending"),
                            "gas": 200000,
                            "gasPrice": w3.to_wei("50", "gwei")
                        })
    
                        # Sign using buyer private key
                        signed_tx = w3.eth.account.sign_transaction(tx, private_key=buyer_pk)
                        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
                        # Issue coupon
                        coupon = f"KFC-{uuid4().hex[:8].upper()}"
                        req = {
                            "id": uuid4().hex,
                            "buyer": buyer_addr,
                            "amount": float(amount),
                            "coupon": coupon,
                            "created_at": datetime.utcnow().isoformat() + "Z",
                            "verified": True
                        }
                        st.session_state.redeem_requests.insert(0, req)
                        add_message(f"✅ Redeem successful! Tx: {tx_hash.hex()} — Coupon: {coupon}")
                        refresh_balances(buyer_addr)
                        show_notifications()
                except Exception as e:
                    add_message(f"❌ Redeem failed: {e}")
                    show_notifications()
    else:
        st.info("Enter a valid buyer address in the sidebar to redeem tokens.")

# ---------------------------
# TAB 4: NFT Badges
# ---------------------------
with tabs[3]:
    st.header("🏅 Your NFT Badges")
    buyer_addr = st.session_state.buyer_address
    if buyer_addr:
        nft_count = st.session_state.nft_count
        st.write(f"You own **{nft_count}** NFT(s).")
        if nft_count > 0:
            try:
                next_id = reward_nft.functions.nextTokenId().call()
            except Exception:
                next_id = 200
            owned = []
            max_scan = min(next_id+1, 2000)
            for tid in range(1, max_scan):
                try:
                    owner = reward_nft.functions.ownerOf(tid).call()
                    if owner.lower() == buyer_addr.lower():
                        owned.append(tid)
                except Exception:
                    continue
            if owned:
                for tid in owned:
                    st.success(f"🎟 NFT #{tid}")
            else:
                st.info("No NFTs found in scanned range.")
    else:
        st.info("Enter a valid buyer address in the sidebar to view NFTs.")

# ---------------------------
# Final: notifications
# ---------------------------
show_notifications()
