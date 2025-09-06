import os
import json
import requests
import time
from dotenv import load_dotenv
from web3 import Web3
from PIL import Image, ImageDraw, ImageFont

# --- Load Environment Variables ---
load_dotenv()

# --- Configuration for Monad ---
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
# --- THIS LINE IS NOW CORRECTED ---
# It now reads from a dedicated secret for the Monad contract.
MONAD_CONTRACT_ADDRESS = os.getenv("MONAD_CONTRACT_ADDRESS") 
# --- Monad Testnet RPC URL ---
RPC_URL = "https://testnet-rpc.monad.xyz" 

# --- Pinata Configuration ---
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")
PINATA_BASE_URL = "https://api.pinata.cloud/"

# --- Smart Contract ABI (Same as before) ---
# Make sure to paste the ABI of the contract you deployed on Monad here.
CONTRACT_ABI = """
[
  YOUR_NEW_CONTRACT_ABI_HERE
]
"""

# --- Helper Functions (No changes here) ---

def get_wallet_stats(w3, address):
    try:
        checksum_address = w3.to_checksum_address(address)
        tx_count = w3.eth.get_transaction_count(checksum_address)
        return {"tx_count": tx_count}
    except Exception as e:
        print(f"Warning: Could not fetch stats for {address}. Error: {e}")
        return {"tx_count": 0}

def generate_image(token_id, stats, owner_address):
    img = Image.new('RGB', (800, 800), color=(16, 25, 48))
    d = ImageDraw.Draw(img)
    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        main_font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        title_font = ImageFont.load_default()
        main_font = ImageFont.load_default()

    d.text((50, 50), "Monad Wallet Status", font=title_font, fill=(255, 255, 255))
    d.line([(50, 130), (750, 130)], fill=(70, 80, 120), width=3)
    d.text((50, 180), f"Token ID: #{token_id}", font=main_font, fill=(210, 210, 255))
    short_address = f"{owner_address[:6]}...{owner_address[-4:]}"
    d.text((50, 250), f"Owner: {short_address}", font=main_font, fill=(210, 210, 255))
    d.text((50, 350), f"Transaction Count: {stats['tx_count']}", font=main_font, fill=(210, 210, 255))
    
    image_path = f"./metadata_monad/images/{token_id}.png"
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    img.save(image_path)
    return image_path

def upload_to_pinata(file_path):
    url = f"{PINATA_BASE_URL}pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_API_SECRET,
    }
    with open(file_path, "rb") as f:
        try:
            response = requests.post(url, files={"file": f}, headers=headers)
            response.raise_for_status()
            cid = response.json()["IpfsHash"]
            print(f"Successfully uploaded {file_path} to IPFS. CID: {cid}")
            return cid
        except requests.exceptions.RequestException as e:
            print(f"Error uploading {file_path} to Pinata: {e}")
            return None

def generate_metadata_json(token_id, image_cid, stats, owner_address):
    metadata = {
        "name": f"Monad Wallet Status NFT #{token_id}",
        "description": "A dynamic NFT on the Monad network.",
        "image": f"ipfs://{image_cid}",
        "owner": owner_address,
        "attributes": [{"trait_type": "Transaction Count", "value": stats['tx_count']}]
    }
    json_path = f"./metadata_monad/json/{token_id}.json"
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    return json_path

# --- Main Logic ---

def main():
    if not all([PRIVATE_KEY, MONAD_CONTRACT_ADDRESS, PINATA_API_KEY, PINATA_API_SECRET]):
        print("FATAL: All required environment variables (PRIVATE_KEY, MONAD_CONTRACT_ADDRESS, PINATA_...) must be set.")
        return

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print(f"FATAL: Could not connect to Monad RPC at {RPC_URL}.")
        return
    
    account = w3.eth.account.from_key(PRIVATE_KEY)
    contract = w3.eth.contract(address=w3.to_checksum_address(MONAD_CONTRACT_ADDRESS), abi=CONTRACT_ABI)
    print(f"Connected to Monad. Script wallet: {account.address}")

    total_supply = contract.functions.totalSupply().call()
    print(f"Total NFTs minted: {total_supply}")

    if total_supply == 0:
        print("No NFTs to update.")
        return

    token_ids_to_update = []
    cids_to_update = []

    for token_id in range(1, total_supply + 1):
        print(f"\n--- Processing Token ID: {token_id} ---")
        try:
            owner_address = contract.functions.ownerOf(token_id).call()
            stats = get_wallet_stats(w3, owner_address)
            
            image_path = generate_image(token_id, stats, owner_address)
            image_cid = upload_to_pinata(image_path)
            if not image_cid: continue

            json_path = generate_metadata_json(token_id, image_cid, stats, owner_address)
            json_cid = upload_to_pinata(json_path)
            if not json_cid: continue
            
            token_ids_to_update.append(token_id)
            cids_to_update.append(json_cid)

        except Exception as e:
            print(f"An unexpected error occurred for Token ID {token_id}: {e}")

    if not token_ids_to_update:
        print("\nNo NFTs were successfully processed.")
        return

    print(f"\n--- Preparing to batch update {len(token_ids_to_update)} NFTs on Monad ---")
    
    try:
        nonce = w3.eth.get_transaction_count(account.address)
        tx_data = contract.functions.batchSetTokenRootHashes(
            token_ids_to_update,
            cids_to_update
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gasPrice': w3.eth.gas_price
        })

        estimated_gas = w3.eth.estimate_gas(tx_data)
        tx_data['gas'] = int(estimated_gas * 1.2)
        
        signed_tx = w3.eth.account.sign_transaction(tx_data, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"Batch update transaction sent! Hash: {tx_hash.hex()}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction confirmed!")

    except Exception as e:
        print(f"Error sending batch update transaction: {e}")

if __name__ == "__main__":
    main()

