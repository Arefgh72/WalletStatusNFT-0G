package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/0glabs/0g-storage-client/node"
	"github.com/ethereum/go-ethereum/crypto"
)

func main() {
	// خواندن کلید خصوصی از سکرت‌های گیت‌هاب
	privateKeyHex := os.Getenv("PRIVATE_KEY")
	if privateKeyHex == "" {
		log.Fatal("FATAL: PRIVATE_KEY environment variable not set.")
	}
	if strings.HasPrefix(privateKeyHex, "0x") {
		privateKeyHex = privateKeyHex[2:]
	}

	privateKey, err := crypto.HexToECDSA(privateKeyHex)
	if err != nil {
		log.Fatalf("FATAL: Failed to parse private key: %v", err)
	}

	// ایجاد کلاینت برای 0G Storage با استفاده از API سازگار
	client, err := node.NewClient("https://rpc-storage-testnet.0g.ai", privateKey)
	if err != nil {
		log.Fatalf("FATAL: Failed to create 0G storage client: %v", err)
	}

	fmt.Println("Client created successfully. Uploading test file...")

	// ایجاد و آپلود یک فایل تستی
	fileContent := []byte("This is the final test file to get the base URI.")
	fileName := "final_test_file.txt"

	result, err := client.Upload(context.Background(), fileContent, fileName)
	if err != nil {
		log.Fatalf("FATAL: Failed to upload file: %v", err)
	}

	// چاپ آدرس نهایی
	fmt.Println("\n=======================================================================")
	fmt.Println("✅ Success! Your Base URI is:")
	fmt.Printf("\n%s\n\n", result.URL)
	fmt.Println("=======================================================================")
	fmt.Println("➡️ Next Step: Copy this URL, add a '/' at the end, and use it in the setBaseURI function.")
}
