import os
from zero_g.storage import StorageClient

# --- تنظیمات ---
# این مقادیر از طریق GitHub Secrets به اسکریپت داده می‌شوند
RPC_URL = os.getenv("RPC_URL", "https://rpc-testnet.0g.ai") 
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# نام فایل تستی که آپلود می‌شود
TEST_FILE_NAME = "placeholder_for_baseuri.txt"
# ----------------

def upload_and_get_uri():
    """
    یک فایل تستی را در 0G Storage آپلود کرده و URI آن را در خروجی چاپ می‌کند.
    """
    if not PRIVATE_KEY:
        print("خطا: کلید خصوصی (PRIVATE_KEY) به عنوان سکرت در گیت‌هاب تنظیم نشده است.")
        return

    try:
        # ساخت یک فایل تستی خالی
        with open(TEST_FILE_NAME, "w") as f:
            f.write("This is a temporary file created by GitHub Actions to get the base URI.")

        # اتصال به کلاینت 0G Storage
        print("در حال اتصال به 0G Storage...")
        storage_client = StorageClient(RPC_URL, PRIVATE_KEY)

        # آپلود فایل به عنوان پوشه
        print(f"در حال آپلود فایل '{TEST_FILE_NAME}' برای ساخت پوشه...")
        upload_result = storage_client.upload(TEST_FILE_NAME, as_folder=True)

        uri = upload_result.uri
        
        print("\n" + "="*70)
        print("✅ آپلود با موفقیت انجام شد!")
        print(f"🎉 آدرس BaseURI شما این است (این خط را کپی کنید):")
        print(f"\n{uri}\n")
        print("="*70)
        print("\nاین آدرس را کپی کرده و در تابع setBaseURI قرارداد هوشمند خود وارد کنید.")
        print("فراموش نکنید که یک '/' به انتهای آن اضافه کنید اگر به صورت خودکار وجود نداشت.")

    except Exception as e:
        print(f"❌ یک خطا در حین اجرای اسکریپت رخ داد: {e}")
    finally:
        # پاک کردن فایل تستی
        if os.path.exists(TEST_FILE_NAME):
            os.remove(TEST_FILE_NAME)

if __name__ == "__main__":
    upload_and_get_uri()
