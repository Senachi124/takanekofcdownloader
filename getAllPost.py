import requests
import json
import os

def read_token(token_file="token.txt"):
    if not os.path.exists(token_file):
        raise FileNotFoundError(f"Token file '{token_file}' not found.")
    with open(token_file, "r") as f:
        token = f.read().strip()
    if not token:
        raise ValueError("Token file is empty.")
    return token

def main():
    token = read_token()
    headers = {"Authorization": token}

    count_url = "https://api.takanekofc.com/auth/notifications/count?notificationType=message"
    count_resp = requests.get(count_url, headers=headers, timeout=10)
    count_resp.raise_for_status()
    count_data = count_resp.json()
    count = count_data.get("count")
    print(f"Total message count: {count}")

    notif_url = (
        "https://api.takanekofc.com/auth/notifications"
        "?notificationType=message"
        f"&offset=0&limit={count}&orderType=2&readType=all"
    )
    notif_resp = requests.get(notif_url, headers=headers, timeout=30)
    notif_resp.raise_for_status()
    notif_data = notif_resp.json()

    with open("all_notifications.json", "w") as f:
        json.dump(notif_data, f, ensure_ascii=False, indent=2)
    print("All notifications saved to all_notifications.json")

if __name__ == "__main__":
    main()