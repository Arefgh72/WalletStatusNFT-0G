package main

import (
	"context"
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/0glabs/0g-storage-client/common/blockchain"
	"github.com/0glabs/0g-storage-client/core"
	"github.com/0glabs/0g-storage-client/indexer"
	"github.com/0glabs/0g-storage-client/transfer"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
)

func main() {
	// 1. Read private key from GitHub Secrets
	privateKeyHex := os.Getenv("PRIVATE_KEY")
	if privateKeyHex == "" {
		fmt.Println("Error: PRIVATE_KEY environment variable not set.")
		os.Exit(1)
	}
	if strings.HasPrefix(privateKeyHex, "0x") {
		privateKeyHex = privateKeyHex[2:]
	}
	privateKey, err := crypto.HexToECDSA(privateKeyHex)
	if err != nil {
		fmt.Printf("Error converting private key: %v\n", err)
		os.Exit(1)
	}

	// 2. Define official RPC endpoints from documentation
	evmRpc := "https://rpc-testnet.0g.ai/"
	indexerRpc := "https://indexer-storage-testnet-turbo.0g.ai"
	fmt.Printf("Using EVM RPC: %s\n", evmRpc)
	fmt.Printf("Using Indexer RPC: %s\n", indexerRpc)

	// 3. Create Web3 client
	w3client, err := blockchain.NewWeb3(evmRpc, privateKey)
	if err != nil {
		fmt.Printf("Error creating Web3 client: %v\n", err)
		os.Exit(1)
	}
	defer w3client.Close()
	fmt.Println("Web3 client created successfully.")

	// 4. Create Indexer client
	indexerClient, err := indexer.NewClient(indexerRpc)
	if err != nil {
		fmt.Printf("Error creating Indexer client: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Indexer client created successfully.")

	// Create a context with a 1-minute timeout
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Minute)
	defer cancel()

	// 5. Select storage nodes
	nodes, err := indexerClient.SelectNodes(ctx, 1, 1, []common.Address{})
	if err != nil {
		fmt.Printf("Error selecting storage nodes: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Selected %d storage node(s).\n", len(nodes))

	// 6. Create uploader
	uploader, err := transfer.NewUploader(ctx, w3client, nodes)
	if err != nil {
		fmt.Printf("Error creating uploader: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Uploader created successfully.")

	// 7. Create a temporary test file to upload
	filePath := "test_file.txt"
	fileContent := []byte("This is a test file to get a base URI.")
	err = os.WriteFile(filePath, fileContent, 0644)
	if err != nil {
		fmt.Printf("Error creating temporary file: %v\n", err)
		os.Exit(1)
	}
	defer os.Remove(filePath) // Clean up the file afterwards

	// 8. Upload the file
	fmt.Printf("Uploading file: %s ...\n", filePath)
	_, err = uploader.UploadFile(ctx, filePath)
	if err != nil {
		fmt.Printf("Error uploading file: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("File uploaded successfully!")

	// 9. Calculate the file's Merkle Root Hash (which is its identifier)
	rootHash, err := core.MerkleRoot(filePath)
	if err != nil {
		fmt.Printf("Error calculating file hash: %v\n", err)
		os.Exit(1)
	}

	// 10. Print the final identifier
	baseURI := rootHash.String()
	fmt.Println("\n======================================================================")
	fmt.Println("✅ Success! Your File Identifier (Merkle Root Hash) is:")
	fmt.Println(baseURI)
	fmt.Println("======================================================================")
	fmt.Println("\nNOTE: This hash is the unique ID for your uploaded data.")
	fmt.Println("For your contract's baseURI, you will likely use a gateway URL followed by this hash.")
	fmt.Println("Example: 'https://gateway.0g/uploads/' (You need to find the correct gateway URL from 0G docs)")
}

