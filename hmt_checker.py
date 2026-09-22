import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ============================================================
# HMT WATCH STOCK TRACKER
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

WATCHES = {
    "HMT Tareeq - Turquoise Blue": {
        "url": "https://www.hmtwatches.in/product_overview?id=eyJpdiI6IkluQ0hpU1ZST2w0cjkyK283bFRPV1E9PSIsInZhbHVlIjoicXV4Q3J4cUlSVkNteGc2NWhjVUJvZz09IiwibWFjIjoiY2E2MTlkZDg2OWMwYWQ2MWQ1ZTI0MzdlZTI1NmRmNzVlNGJiMjQ0YmZlZjgxZDYzOWM4YWMyMzZmNjQyOTQ1YSIsInRhZyI6IiJ9"
    },

    "HMT Tareeq - Sunray Blue": {
        "url": "https://www.hmtwatches.in/product_overview?id=eyJpdiI6Iis3cWJOd0NRK1JhSFgzcTFVdGlmZ3c9PSIsInZhbHVlIjoiMzlsSmVJSWdMTDRTdXhFbk1qRGFidz09IiwibWFjIjoiMDRhOGQyYThhNDc5OTcxNzM2NTk0MWIyMWNiOGI2MTBkY2FlNjBhNjUxOTYzNWI3YmIyYWYzZjE5MjE0MTdiYiIsInRhZyI6IiJ9"
    },

    "HMT Kohinoor - Silver": {
        "url": "https://www.hmtwatches.in/product_overview?id=eyJpdiI6Inkvdk8ydDIwOUZSbStMd2hrdUFYNmc9PSIsInZhbHVlIjoibFBIOW9WVUI1WFFJTXNZZkFFNDVSUT09IiwibWFjIjoiMGQ2MjNjNjk3NzZjMmY5OGQ1OThiZjgyMWJmMDQ4NmViYmYyZTljZmQ3ZWYyYmQ1OTk1NDMyZjUzYzVlNGUzNCIsInRhZyI6IiJ9"
    },

    "HMT Kohinoor - Maroon": {
        "url": "https://www.hmtwatches.in/product_overview?id=eyJpdiI6ImxER3dQWWVSVDhReU1kUmFXOHRHbHc9PSIsInZhbHVlIjoiT0VvVHo3YStVcVBxNDJEQ0Q5bklkdz09IiwibWFjIjoiNjFiMDBiYjk3YjFhOWU3YzIwN2IzMjExYWViZjNlMzE0NzNmOGI2YTdlYjg1YzFhMjBmNTRjODU5MWY2YTM3ZCIsInRhZyI6IiJ9"
    },

    "HMT Kohinoor - Dark Blue Matte": {
        "url": "https://www.hmtwatches.in/product_overview?id=eyJpdiI6IkZqTEZhVXRJdnZ3b0RhbGZsOW1PdGc9PSIsInZhbHVlIjoiWDAxVHlVTm9WN0tIWVFmbHhhbWZidz09IiwibWFjIjoiNDBmZTQzMzllMjQ0ZWJhNTM4ODg3ODBjYjgzYTJkY2VmYWY4ZGY2YTIyZGJiMTFlYTQ4ZGE2NDRmYWE5YWZiNCIsInRhZyI6IiJ9"
    }
}


# ------------------------------------------------------------
# TELEGRAM
# ------------------------------------------------------------

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials are missing.")
        return

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    }

    response = requests.post(url, data=payload, timeout=20)

    if response.ok:
        print("Telegram notification sent.")
    else:
        print("Telegram error:", response.text)


# ------------------------------------------------------------
# STOCK CHECK
# ------------------------------------------------------------

def check_stock(name, url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/140.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        page_text = soup.get_text(
            " ",
            strip=True
        ).lower()

        # HMT currently displays "Out Of Stock"
        # when the product is unavailable.
        out_of_stock = (
            "out of stock" in page_text
            or "out-of-stock" in page_text
        )

        if out_of_stock:
            status = "OUT_OF_STOCK"
        else:
            status = "AVAILABLE"

        print(f"{name}: {status}")

        return status

    except Exception as error:
        print(f"{name}: ERROR - {error}")
        return "ERROR"


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print("=" * 60)
    print("HMT Stock Tracker")
    print(f"Checked at: {current_time}")
    print("=" * 60)

    available_watches = []

    for name, details in WATCHES.items():

        status = check_stock(
            name,
            details["url"]
        )

        if status == "AVAILABLE":
            available_watches.append(
                (name, details["url"])
            )

    # --------------------------------------------------------
    # SEND ALERT
    # --------------------------------------------------------

    if available_watches:

        message = "🚨 HMT WATCH BACK IN STOCK! 🚨\n\n"

        for name, url in available_watches:
            message += (
                f"⌚ {name}\n"
                f"🟢 AVAILABLE\n"
                f"👉 {url}\n\n"
            )

        message += (
            "⚡ Check it immediately — "
            "stock may sell out quickly!"
        )

        send_telegram(message)

    else:
        print("No monitored watches are currently available.")


if __name__ == "__main__":
    main()