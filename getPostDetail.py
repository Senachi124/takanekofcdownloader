from tqdm import tqdm
import json
import requests
import os

def main():
    input_file = "all_notifications.json"
    output_file = "api_responses.json"
    error_file = "problematic.json"
    api_url = "https://api.takanekofc.com/auth/notifications/{}"


    token_file = "token.txt"
    if not os.path.exists(token_file):
        print(f"Token file '{token_file}' not found. Please create it and put your token inside.")
        return
    with open(token_file, "r", encoding="utf-8") as tf:
        token = tf.read().strip()
    if not token:
        print("Token file is empty. Exiting.")
        return

    with open(input_file, "r", encoding="utf-8") as f: 
        data = json.load(f)


    responses_count = 0
    errors_count = 0
    with open(output_file.replace('.json', '.jsonl'), "w", encoding="utf-8") as resp_f, \
         open(error_file.replace('.json', '.jsonl'), "w", encoding="utf-8") as err_f:
        for idx, entry in enumerate(tqdm(data, desc="Processing notifications")):
            notification_id = entry.get("notificationReservationId")
            if not notification_id:
                error_obj = {"index": idx, "error": "No notificationReservationId", "source": entry}
                err_f.write(json.dumps(error_obj, ensure_ascii=False) + "\n")
                errors_count += 1
                continue
            url = api_url.format(notification_id)
            headers = {"Authorization": token}
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    try:
                        resp_json = resp.json()
                        for field in ("createDate", "releaseDate", "sendingOfficialUserId"):
                            if field not in resp_json:
                                error_obj = {"index": idx, "error": f"Missing field {field}", "source": entry, "api_response": resp_json}
                                err_f.write(json.dumps(error_obj, ensure_ascii=False) + "\n")
                                errors_count += 1
                                break
                        else:
                            resp_f.write(json.dumps(resp_json, ensure_ascii=False) + "\n")
                            responses_count += 1
                    except Exception as e:
                        error_obj = {"index": idx, "error": f"JSON decode error: {e}", "source": entry, "api_response_text": resp.text}
                        err_f.write(json.dumps(error_obj, ensure_ascii=False) + "\n")
                        errors_count += 1
                else:
                    error_obj = {"index": idx, "error": f"HTTP {resp.status_code}", "source": entry, "api_response_text": resp.text}
                    err_f.write(json.dumps(error_obj, ensure_ascii=False) + "\n")
                    errors_count += 1
            except Exception as e:
                error_obj = {"index": idx, "error": f"Request error: {e}", "source": entry}
                err_f.write(json.dumps(error_obj, ensure_ascii=False) + "\n")
                errors_count += 1

    print(f"Done. {responses_count} responses saved to {output_file.replace('.json', '.jsonl')}. {errors_count} errors saved to {error_file.replace('.json', '.jsonl')}.")

if __name__ == "__main__":
    main()
