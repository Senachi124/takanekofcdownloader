
import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
import html
from tqdm import tqdm

user_map = {
    "0Tg8s7vP15A90NeUM4rnC": "籾山ひめり",
    "Ga_ddM7JhAnlRnkYXsDHG": "春野莉々",
    "WjMBMFAFdQ6zmzm34dpj5": "葉月紗蘭",
    "NSTLZy-J08YuwqPkkVpb2": "城月菜央",
    "6lToHXxrSpkyDT9jmPUOE": "たかねこファンクラブ運営",
    "jv8afDOWLZqPpdJ6Mlymq": "星谷美来",
    "a4npPurePgMCD5wEmekQO": "東山恵里沙",
    "2Ssu8-WzAOXlFZkeD01VU": "松本ももな",
    "SKuzAY-gIlD25a5-yGmhZ": "日向端ひな",
    "3-3vzS6FMV9lCvNjGscEg": "橋本桃呼",
    "VaKS0gcqUZTDi_asf5Xn2": "涼海すう"
}

def format_ts(ms):
    return datetime.fromtimestamp(ms / 1000, tz=ZoneInfo("Asia/Tokyo")).strftime('%Y-%m-%d %H:%M:%S')

def html_to_markdown(html_content):
    soup = BeautifulSoup(html_content or "", "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    markdown = ""
    for p in soup.find_all("p"):
        text = p.get_text(strip=False)
        markdown += text.strip() + "\n\n"
    return html.unescape(markdown.strip())

def download_image(image_url, save_path):
    try:
        r = requests.get(image_url, timeout=10)
        r.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"Failed to download {image_url}: {e}")
        return False

def main():
    input_file = "api_responses.jsonl"
    root_dir = "exported"
    os.makedirs(root_dir, exist_ok=True)

    # Count lines for tqdm
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in tqdm(lines, desc="Exporting notifications"):
        try:
            data = json.loads(line)
        except Exception:
            continue

        sender_id = data.get("sendingOfficialUserId")
        if not sender_id:
            continue
        sender_name = user_map.get(sender_id, sender_id).replace(" ", "")
        sender_dir = os.path.join(root_dir, sender_name)
        os.makedirs(sender_dir, exist_ok=True)
        pictures_dir = os.path.join(sender_dir, "pictures")
        os.makedirs(pictures_dir, exist_ok=True)

        release_date = data.get("releaseDate", 0)
        # Format release date as YYYY-MM-DD_HHMMSS
        try:
            release_dt = datetime.fromtimestamp(release_date / 1000, tz=ZoneInfo("Asia/Tokyo"))
            release_str = release_dt.strftime("%Y-%m-%d_%H%M%S")
        except Exception:
            release_str = str(release_date)
        title = data.get("title", "untitled").replace("/", "_").replace("\\", "_")
        notification_id = data.get("notificationId", "unknown")
        post_dir = os.path.join(sender_dir, f"{release_str}_{title}")
        os.makedirs(post_dir, exist_ok=True)
        md_path = os.path.join(post_dir, "index.md")

        body_md = ""
        for key in sorted(data.keys()):
            if key.startswith("body") and data[key]:
                body_md += html_to_markdown(data[key]) + "\n\n"

        image_md = ""
        image_count = 1
        for key in sorted(data.keys()):
            if key.startswith("image") and data[key]:
                image_url = f"https://takanekofc.com/{data[key]}"
                ext = os.path.splitext(data[key])[1]
                img_filename = f"{release_str}_{image_count:02d}{ext}"
                img_path = os.path.join(post_dir, img_filename)

                if not os.path.exists(img_path):
                    download_image(image_url, img_path)

                pic_copy_path = os.path.join(pictures_dir, img_filename)
                if not os.path.exists(pic_copy_path):
                    try:
                        with open(img_path, "rb") as src, open(pic_copy_path, "wb") as dst:
                            dst.write(src.read())
                    except Exception as e:
                        print(f"Failed to copy {img_path} to {pic_copy_path}: {e}")
                image_md += f"![{key}]({img_filename})\n"
                image_count += 1

        md_content = f"""# {title}

**Sender**: {sender_name}  
**Sender ID**: {sender_id}  
**Notification ID**: {notification_id}  
**Created**: {format_ts(data.get('createDate', 0))}  
**Released**: {format_ts(data.get('releaseDate', 0))}  
**Read**: {format_ts(data.get('readDate', 0))}  

---

{body_md.strip()}

---

{image_md.strip()}
"""
        with open(md_path, "w", encoding="utf-8") as out_md:
            out_md.write(md_content)
        # tqdm will handle progress display

if __name__ == "__main__":
    main()
