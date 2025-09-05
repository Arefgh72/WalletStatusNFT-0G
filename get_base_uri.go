package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/0glabs/0g-storage-client/node"
	"github.com/ethereum/go-ethereum/crypto"
)

func main() {
	// مرحله ۱: خواندن کلید خصوصی از سکرت‌های گیت‌هاب
	// The script reads the private key from GitHub Secrets.
	privateKeyHex := os.Getenv("PRIVATE_KEY")
	if privateKeyHex == "" {
		log.Fatal("FATAL: PRIVATE_KEY environment variable not set. Please set it in GitHub repository secrets.")
	}

	// مرحله ۲: آماده‌سازی کلید خصوصی برای امضای تراکنش‌ها
	// The private key is prepared for signing transactions. We remove the "0x" prefix.
	privateKey, err := crypto.HexToECDSA(privateKeyHex[2:])
	if err != nil {
		log.Fatalf("FATAL: Failed to parse private key: %v", err)
	}

	// مرحله ۳: ایجاد یک کلاینت جدید برای اتصال به شبکه تست‌نت 0G Storage
	// A new client is created to connect to the 0G Storage testnet.
	// The URL "https://rpc-storage-testnet.0g.ai" is the official testnet endpoint.
	fmt.Println("Connecting to 0G Storage testnet...")
	client, err := node.NewClient("https://rpc-storage-testnet.0g.ai", privateKey)
	if err != nil {
		log.Fatalf("FATAL: Failed to create 0G storage client: %v", err)
	}

	// مرحله ۴: ایجاد یک فایل تستی و خالی برای آپلود
	// A dummy test file is created for the upload process.
	fileContent := []byte("This is a test file to get the base URI.")
	fileName := "test_file_for_base_uri.txt"

	fmt.Printf("Uploading a test file ('%s') to 0G Storage...\n", fileName)

	// مرحله ۵: آپلود فایل به شبکه 0G Storage
	// The file is uploaded to the 0G Storage network.
	result, err := client.Upload(context.Background(), fileContent, fileName)
	if err != nil {
		log.Fatalf("FATAL: Failed to upload file: %v", err)
	}

	// مرحله ۶: چاپ آدرس نهایی در خروجی. این همان baseURI شماست!
	// The final URL is printed. This is your baseURI.
	fmt.Println("\n=======================================================================")
	fmt.Println("✅ Success! Your Base URI is:")
	fmt.Printf("\n%s\n\n", result.URL)
	fmt.Println("=======================================================================")
	fmt.Println("➡️ Next Step: Copy this URL, add a '/' at the end, and use it in the setBaseURI function of your smart contract.")
}
