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
MONAD_CONTRACT_ADDRESS = os.getenv("MONAD_CONTRACT_ADDRESS")
RPC_URL = "https://devnet.monad.xyz/"

# --- Pinata Configuration ---
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")
PINATA_BASE_URL = "https://api.pinata.cloud/"

# --- Smart Contract ABI (Same as before) ---
CONTRACT_ABI = """
[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256[]","name":"tokenIds","type":"uint256[]"}],"name":"BatchTokenRootHashesUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"StatusNFTMinted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":false,"internalType":"string","name":"newRootHash","type":"string"}],"name":"TokenRootHashUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"tokenIds","type":"uint256[]"},{"internalType":"string[]","name":"rootHashes","type":"string[]"}],"name":"batchSetTokenRootHashes","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"wallet","type":"address"}],"name":"hasMinted","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"mintStatusNFT","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"string","name":"rootHash","type":"string"}],"name":"setTokenRootHash","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]
"""

# --- Helper Functions ---

def get_wallet_stats(w3, address):
    try:
        checksum_address = w3.to_checksum_address(address)
        tx_count = w3.eth.get_transaction_count(checksum_address)
        return {"tx_count": tx_count}
    except Exception as e:
        print(f"Warning: Could not fetch stats for {address}. Error: {e}")
        return {"tx_count": 0}

# --- THIS IS THE NEW, IMPROVED IMAGE GENERATION FUNCTION ---
def generate_image(token_id, stats, owner_address):
    """Generates a beautiful, high-quality dynamic image for the NFT."""
    width, height = 800, 800
    
    # Create a new image
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # 1. Create a beautiful gradient background
    start_color = (18, 18, 97) # Dark Blue
    end_color = (97, 18, 120)  # Dark Purple
    for y in range(height):
        # Calculate the interpolation factor
        ratio = y / height
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Load the professional font (ensure it's in your repo)
    try:
        # NOTE: You MUST add the Poppins-Bold.ttf font to this path in your repo
        font_path = ".github/fonts/Poppins-Bold.ttf"
        title_font = ImageFont.truetype(font_path, 70)
        label_font = ImageFont.truetype(font_path, 35)
        value_font = ImageFont.truetype(font_path, 90)
        footer_font = ImageFont.truetype(font_path, 20)
    except IOError:
        print("Warning: Poppins font not found. Using default font.")
        title_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        value_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # 3. Draw the content with improved layout and colors
    # Title
    draw.text((width / 2, 100), "MONAD STATUS", font=title_font, fill=(255, 255, 255), anchor="ms")
    # Separator Line
    draw.line([(100, 160), (width - 100, 160)], fill=(100, 100, 150), width=3)

    # Token ID
    draw.text((width / 2, 230), f"TOKEN ID #{token_id}", font=label_font, fill=(200, 200, 255), anchor="ms")

    # Transaction Count - Label
    draw.text((width / 2, 400), "TRANSACTION COUNT", font=label_font, fill=(150, 160, 200), anchor="ms")
    # Transaction Count - Value (Large and prominent)
    tx_count_str = str(stats['tx_count'])
    draw.text((width / 2, 500), tx_count_str, font=value_font, fill=(255, 255, 255), anchor="ms")
    
    # Footer
    timestamp = f"Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}"
    draw.text((width / 2, height - 50), timestamp, font=footer_font, fill=(120, 130, 170), anchor="ms")

    # Save the generated image
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

# --- Main Logic (No changes here) ---
def main():
    if not all([PRIVATE_KEY, MONAD_CONTRACT_ADDRESS, PINATA_API_KEY, PINATA_API_SECRET]):
        print("FATAL: All required environment variables must be set.")
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

