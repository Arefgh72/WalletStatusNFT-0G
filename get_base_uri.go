package main

import (
	"context"
	"fmt"
	"os"
	"strings"

	// --- ایمپورت اصلی و اصلاح شده ---
	"github.com/0glabs/0g-storage-client/client"
	"github.com/ethereum/go-ethereum/common/hexutil"
	"github.com/ethereum/go-ethereum/crypto"
)

func main() {
	// ۱. خواندن کلید خصوصی از سکرت‌های گیت‌هاب
	privateKeyHex := os.Getenv("PRIVATE_KEY")
	if privateKeyHex == "" {
		fmt.Println("Error: PRIVATE_KEY environment variable not set.")
		os.Exit(1)
	}
	// حذف پیشوند 0x اگر وجود داشته باشد
	if strings.HasPrefix(privateKeyHex, "0x") {
		privateKeyHex = privateKeyHex[2:]
	}

	privateKey, err := crypto.HexToECDSA(privateKeyHex)
	if err != nil {
		fmt.Printf("Error converting private key: %v\n", err)
		os.Exit(1)
	}

	// ۲. آدرس شبکه تست‌نت 0G
	// این آدرس رسمی از مستندات آنهاست
	rpcURL := "https://rpc-testnet.0g.ai"

	fmt.Println("Connecting to 0G Storage node at:", rpcURL)

	// --- فراخوانی تابع اصلاح شده و صحیح ---
	// ۳. ایجاد یک کلاینت جدید با استفاده از تابع صحیح از پکیج client
	zgClient, err := client.NewClient(rpcURL, privateKey)
	if err != nil {
		fmt.Printf("Error creating 0G client: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Client created successfully.")

	// ۴. آپلود یک فایل تستی برای گرفتن آدرس
	testContent := []byte("This is a test file to get a base URI.")
	fileName := "test.txt"

	fmt.Println("Uploading test file...")
	// در نسخه جدید، Upload نیاز به context و fileName دارد
	merkleRoot, err := zgClient.Upload(context.Background(), strings.NewReader(string(testContent)), fileName)
	if err != nil {
		fmt.Printf("Error uploading file: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("File uploaded successfully!")

	// ۵. چاپ کردن URI نهایی
	// URI همان Merkle Root است که به صورت هگزادسیمال نمایش داده می‌شود
	baseURI := hexutil.Encode(merkleRoot)
	fmt.Println("\n==============================================")
	fmt.Println("✅ Success! Your Base URI is:")
	fmt.Println(baseURI)
	fmt.Println("==============================================")
	fmt.Println("\nNOTE: Remember to add a '/' at the end when setting it in your smart contract.")
	fmt.Println("Example: ", baseURI+"/")
}

