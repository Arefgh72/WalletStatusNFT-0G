import os
import json
import subprocess
import time
from dotenv import load_dotenv
from web3 import Web3
from PIL import Image, ImageDraw, ImageFont

# --- Load Environment Variables ---
# This line loads variables from a .env file for local testing.
# In GitHub Actions, these will be set as environment secrets.
load_dotenv()

# --- Configuration ---
# These are read from GitHub Secrets in the workflow.
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
# Official RPC endpoints from 0G documentation.
RPC_URL = "https://evmrpc-testnet.0g.ai/"
INDEXER_URL = "https://indexer-storage-testnet-turbo.0g.ai"
# Path to the CLI binary built in the GitHub workflow.
CLI_EXECUTABLE = "./zg_storage"

# --- Smart Contract ABI (Application Binary Interface) ---
# This is the ABI you provided for your deployed contract.
CONTRACT_ABI = """
[{"type": "constructor", "inputs": [], "stateMutability": "nonpayable"}, {"name": "Approval", "type": "event", "inputs": [{"name": "owner", "type": "address", "indexed": true, "internalType": "address"}, {"name": "approved", "type": "address", "indexed": true, "internalType": "address"}, {"name": "tokenId", "type": "uint256", "indexed": true, "internalType": "uint256"}], "anonymous": false}, {"name": "ApprovalForAll", "type": "event", "inputs": [{"name": "owner", "type": "address", "indexed": true, "internalType": "address"}, {"name": "operator", "type": "address", "indexed": true, "internalType": "address"}, {"name": "approved", "type": "bool", "indexed": false, "internalType": "bool"}], "anonymous": false}, {"name": "BatchTokenRootHashesUpdated", "type": "event", "inputs": [{"name": "tokenIds", "type": "uint256[]", "indexed": false, "internalType": "uint256[]"}], "anonymous": false}, {"name": "OwnershipTransferred", "type": "event", "inputs": [{"name": "previousOwner", "type": "address", "indexed": true, "internalType": "address"}, {"name": "newOwner", "type": "address", "indexed": true, "internalType": "address"}], "anonymous": false}, {"name": "StatusNFTMinted", "type": "event", "inputs": [{"name": "owner", "type": "address", "indexed": true, "internalType": "address"}, {"name": "tokenId", "type": "uint256", "indexed": true, "internalType": "uint256"}], "anonymous": false}, {"name": "TokenRootHashUpdated", "type": "event", "inputs": [{"name": "tokenId", "type": "uint256", "indexed": true, "internalType": "uint256"}, {"name": "newRootHash", "type": "string", "indexed": false, "internalType": "string"}], "anonymous": false}, {"name": "Transfer", "type": "event", "inputs": [{"name": "from", "type": "address", "indexed": true, "internalType": "address"}, {"name": "to", "type": "address", "indexed": true, "internalType": "address"}, {"name": "tokenId", "type": "uint256", "indexed": true, "internalType": "uint256"}], "anonymous": false}, {"name": "approve", "type": "function", "inputs": [{"name": "to", "type": "address", "internalType": "address"}, {"name": "tokenId", "type": "uint256", "internalType": "uint256"}], "outputs": [], "stateMutability": "nonpayable"}, {"name": "balanceOf", "type": "function", "inputs": [{"name": "owner", "type": "address", "internalType": "address"}], "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}], "stateMutability": "view"}, {"name": "batchSetTokenRootHashes", "type": "function", "inputs": [{"name": "tokenIds", "type": "uint256[]", "internalType": "uint256[]"}, {"name": "rootHashes", "type": "string[]", "internalType": "string[]"}], "outputs": [], "stateMutability": "nonpayable"}, {"name": "getApproved", "type": "function", "inputs": [{"name": "tokenId", "type": "uint256", "internalType": "uint256"}], "outputs": [{"name": "", "type": "address", "internalType": "address"}], "stateMutability": "view"}, {"name": "hasMinted", "type": "function", "inputs": [{"name": "wallet", "type": "address", "internalType": "address"}], "outputs": [{"name": "", "type": "bool", "internalType": "bool"}], "stateMutability": "view"}, {"name": "isApprovedForAll", "type": "function", "inputs": [{"name": "owner", "type": "address", "internalType": "address"}, {"name": "operator", "type": "address", "internalType": "address"}], "outputs": [{"name": "", "type": "bool", "internalType": "bool"}], "stateMutability": "view"}, {"name": "mintStatusNFT", "type": "function", "inputs": [], "outputs": [], "stateMutability": "nonpayable"}, {"name": "name", "type": "function", "inputs": [], "outputs": [{"name": "", "type": "string", "internalType": "string"}], "stateMutability": "view"}, {"name": "owner", "type": "function", "inputs": [], "outputs": [{"name": "", "type": "address", "internalType": "address"}], "stateMutability": "view"}, {"name": "ownerOf", "type": "function", "inputs": [{"name": "tokenId", "type": "uint256", "internalType": "uint256"}], "outputs": [{"name": "", "type": "address", "internalType": "address"}], "stateMutability": "view"}, {"name": "renounceOwnership", "type": "function", "inputs": [], "outputs": [], "stateMutability": "nonpayable"}, {"name": "safeTransferFrom", "type": "function", "inputs": [{"name": "from", "type": "address", "internalType": "address"}, {"name": "to", "type": "address", "internalType": "address"}, {"name": "tokenId", "type": "uint256", "internalType": "uint256"}], "outputs": [], "stateMutability": "nonpayable"}, {"name": "safeTransferFrom", "type": "function", "inputs": [{"name": "from", "type": "address", "internalType": "address"}, {"name": "to", "type": "address", "internalType": "address"}, {"name": "tokenId", "type": "uint256", "internalType": "uint256"}, {"name": "data", "type": "bytes", "internalType": "bytes"}], "outputs": [], "stateMutability": "nonpayable"}, {"name": "setApprovalForAll", "type": "function", "inputs": [{"name": "operator", "type": "address", "internalType": "address"}, {"name": "approved", "type": "bool", "internalType": "bool"}], "outputs": [], "stateMutability": "nonpayable"}, {"name": "setTokenRootHash", "type": "function", "inputs": [{"name": "tokenId", "type": "uint256", "internalType": "uint256"}, {"name": "rootHash", "type": "string", "internalType": "string"}], "outputs": [], "stateMutability": "nonpayable"}, {"name": "supportsInterface", "type": "function", "inputs": [{"name": "interfaceId", "type": "bytes4", "internalType": "bytes4"}], "outputs": [{"name": "", "type": "bool", "internalType": "bool"}], "stateMutability": "view"}, {"name": "symbol", "type": "function", "inputs": [], "outputs": [{"name": "", "type": "string", "internalType": "string"}], "stateMutability": "view"}, {"name": "tokenURI", "type": "function", "inputs": [{"name": "tokenId", "type": "uint256", "internalType": "uint256"}], "outputs": [{"name": "", "type": "string", "internalType": "string"}], "stateMutability": "view"}, {"name": "totalSupply", "type": "function", "inputs": [], "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}], "stateMutability": "view"}, {"name": "transferFrom", "type": "function", "inputs": [{"name": "from", "type": "address", "internalType": "address"}, {"name": "to", "type": "address", "internalType": "address"}, {"name": "tokenId", "type": "uint256", "internalType": "uint256"}], "outputs": [], "stateMutability": "nonpayable"}, {"name": "transferOwnership", "type": "function", "inputs": [{"name": "newOwner", "type": "address", "internalType": "address"}], "outputs": [], "stateMutability": "nonpayable"}]
"""

# --- Helper Functions ---

def get_wallet_stats(w3, address):
    """Fetches transaction count for a given wallet address."""
    try:
        # Get the number of transactions sent from the address.
        checksum_address = w3.to_checksum_address(address)
        tx_count = w3.eth.get_transaction_count(checksum_address)
        # Note: Calculating wallet age accurately requires a blockchain explorer API or an indexer.
        # We'll keep it simple and only use the transaction count for this example.
        return {"tx_count": tx_count, "age_days": "N/A"}
    except Exception as e:
        print(f"Warning: Could not fetch stats for {address}. Error: {e}")
        return {"tx_count": 0, "age_days": "N/A"}

def generate_image(token_id, stats, owner_address):
    """Generates a dynamic PNG image for the NFT with the wallet's stats."""
    # Create a new image with a dark blue background
    img = Image.new('RGB', (800, 800), color=(16, 25, 48))
    d = ImageDraw.Draw(img)

    # Try to load a specific font, fall back to default if not found.
    # Note: On GitHub Actions, specific fonts like 'arial.ttf' might not be available.
    # The default font will be used as a fallback.
    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        main_font = ImageFont.truetype("arial.ttf", 40)
        small_font = ImageFont.truetype("arial.ttf", 25)
    except IOError:
        print("Warning: Arial font not found. Using default font.")
        title_font = ImageFont.load_default()
        main_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Draw content on the image
    d.text((50, 50), "0G Wallet Status", font=title_font, fill=(255, 255, 255))
    d.line([(50, 130), (750, 130)], fill=(70, 80, 120), width=3)

    d.text((50, 180), f"Token ID: #{token_id}", font=main_font, fill=(210, 210, 255))
    
    # Display a shortened version of the owner's address
    short_address = f"{owner_address[:6]}...{owner_address[-4:]}"
    d.text((50, 250), f"Owner: {short_address}", font=main_font, fill=(210, 210, 255))

    d.text((50, 350), "On-Chain Activity:", font=main_font, fill=(150, 160, 200))
    d.text((70, 420), f"Transaction Count: {stats['tx_count']}", font=main_font, fill=(210, 210, 255))
    
    timestamp = f"Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}"
    d.text((50, 720), timestamp, font=small_font, fill=(120, 130, 170))

    # Save the generated image to a file
    image_path = f"./metadata/images/{token_id}.png"
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    img.save(image_path)
    return image_path

def generate_metadata_json(token_id, image_root_hash, stats, owner_address):
    """Generates the metadata JSON file for the NFT."""
    metadata = {
        "name": f"Wallet Status NFT #{token_id}",
        "description": "A dynamic NFT that reflects the on-chain activity of a wallet on the 0G network.",
        "image": f"https://indexer-storage-testnet-turbo.0g.ai/file?root={image_root_hash}",
        "owner": owner_address,
        "attributes": [
            {
                "trait_type": "Transaction Count", 
                "value": stats['tx_count']
            },
            # You can add more attributes here later, e.g., Wallet Age
        ]
    }
    json_path = f"./metadata/json/{token_id}.json"
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    return json_path

def upload_to_0g_storage(file_path):
    """Uploads a file to 0G Storage using the official CLI and returns the root hash."""
    # This command is built according to the official 0G CLI documentation
    command = [
        CLI_EXECUTABLE,
        "upload",
        "--url", RPC_URL,
        "--indexer", INDEXER_URL,
        "--key", PRIVATE_KEY,
        "--file", file_path
    ]
    print(f"Executing command: {' '.join(command)}")
    
    try:
        # Run the command with a timeout and capture output
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=400)
        output = result.stdout
        print("CLI Output:", output)
        
        # Extract root hash from the CLI output, searching for the specific line
        for line in output.splitlines():
            if "Root hash" in line or "file uploaded, root =" in line:
                root_hash = line.split()[-1]
                print(f"Successfully extracted root hash: {root_hash}")
                return root_hash
        
        print("Error: Could not find root hash in CLI output.")
        return None
        
    except subprocess.CalledProcessError as e:
        # This handles cases where the CLI returns a non-zero exit code (an error)
        print(f"Error: 0G CLI failed to upload {file_path}.")
        print("Stderr:", e.stderr)
        return None
    except subprocess.TimeoutExpired:
        print(f"Error: 0G CLI timed out while uploading {file_path}.")
        return None

# --- Main Logic ---

def main():
    if not PRIVATE_KEY or not CONTRACT_ADDRESS:
        print("FATAL: PRIVATE_KEY and CONTRACT_ADDRESS environment variables must be set.")
        return

    # Connect to the blockchain
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("FATAL: Could not connect to the RPC URL.")
        return
    
    account = w3.eth.account.from_key(PRIVATE_KEY)
    contract = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDRESS), abi=CONTRACT_ABI)
    print(f"Successfully connected. Script wallet address: {account.address}")

    # Get the total number of NFTs minted so far using the standard totalSupply function
    try:
        total_supply = contract.functions.totalSupply().call()
    except Exception as e:
        print(f"FATAL: Could not determine total supply of NFTs using totalSupply(). Error: {e}")
        return

    print(f"Total NFTs minted: {total_supply}")

    if total_supply == 0:
        print("No NFTs found to update. Exiting.")
        return

    token_ids_to_update = []
    root_hashes_to_update = []

    # Loop through each token ID from 1 to total_supply
    for token_id in range(1, total_supply + 1):
        print(f"\n--- Processing Token ID: {token_id} ---")
        try:
            # Get the owner of the current NFT
            owner_address = contract.functions.ownerOf(token_id).call()
            print(f"Owner found: {owner_address}")
            
            # Get the wallet stats for the owner
            stats = get_wallet_stats(w3, owner_address)
            
            # 1. Generate the dynamic image
            image_path = generate_image(token_id, stats, owner_address)
            print(f"Image generated at: {image_path}")
            
            # 2. Upload the image to 0G Storage
            image_root_hash = upload_to_0g_storage(image_path)
            if not image_root_hash:
                print(f"Skipping Token ID {token_id} due to image upload failure.")
                continue

            # 3. Generate the metadata JSON file
            json_path = generate_metadata_json(token_id, image_root_hash, stats, owner_address)
            print(f"Metadata JSON generated at: {json_path}")

            # 4. Upload the metadata JSON to 0G Storage
            json_root_hash = upload_to_0g_storage(json_path)
            if not json_root_hash:
                print(f"Skipping Token ID {token_id} due to metadata upload failure.")
                continue
            
            # Add the successful updates to our lists for the batch transaction
            token_ids_to_update.append(token_id)
            root_hashes_to_update.append(json_root_hash)
            print(f"Successfully prepared Token ID {token_id} for on-chain update.")

        except Exception as e:
            print(f"An unexpected error occurred while processing Token ID {token_id}: {e}")

    # 5. If there are any successful updates, send the batch transaction
    if not token_ids_to_update:
        print("\nNo NFTs were successfully processed for on-chain update. Exiting.")
        return

    print(f"\n--- Preparing to batch update {len(token_ids_to_update)} NFTs on-chain ---")
    
    try:
        # Build the transaction for the batch update function
        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.eth.gas_price
        
        tx_data = contract.functions.batchSetTokenRootHashes(
            token_ids_to_update,
            root_hashes_to_update
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gasPrice': gas_price,
            # 'gas': 3000000 # Optional: You can set a manual gas limit if needed
        })
        
        # Estimate gas to make sure the transaction is likely to succeed
        estimated_gas = w3.eth.estimate_gas(tx_data)
        tx_data['gas'] = int(estimated_gas * 1.2) # Add 20% buffer
        print(f"Estimated Gas: {estimated_gas}, Gas Limit Set: {tx_data['gas']}")

        signed_tx = w3.eth.account.sign_transaction(tx_data, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"Batch update transaction sent! Hash: {tx_hash.hex()}")
        print("Waiting for transaction confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        print("Transaction confirmed successfully!")
        print("Receipt:", receipt)

    except Exception as e:
        print(f"Error sending batch update transaction: {e}")

if __name__ == "__main__":
    main()

