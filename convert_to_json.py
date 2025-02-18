import json
import os
import subprocess
from pathlib import Path
from pypinyin import pinyin, Style
from dotenv import load_dotenv

def chinese_to_json(text):
    """將中文文字轉換為 JSON 格式的注音資料，並在多個字之間加入空格"""
    bopomofo_list = pinyin(text, style=Style.BOPOMOFO)
    bopomofo_str = ' '.join([b[0] for b in bopomofo_list])  # 多個字之間加空格

    return {
        "bopomofo": bopomofo_str,
        "phrase": text
    }

def save_to_json(new_entry, file_path):
    """將新的注音資料存入 chewing.json，並讓 chewing-editor 重新載入"""
    # 如果檔案已存在，則讀取原始資料
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"userphrase": []}  # 如果 JSON 格式錯誤，則初始化
    else:
        data = {"userphrase": []}

    # 檢查是否已存在相同 phrase，避免重複
    if new_entry not in data["userphrase"]:
        data["userphrase"].append(new_entry)

    # 將更新後的資料寫入 chewing.json
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已將資料存入 {file_path}")

def reload_chewing():
    """強制重新載入 chewing 詞庫"""
    try:
        subprocess.run(["chewing-editor"], check=True)
        print("已啟動 chewing-editor 以重新載入詞庫")
        return True
    except FileNotFoundError:
        print("錯誤：找不到 chewing-editor，請確認已安裝！")
        return False
    except subprocess.CalledProcessError:
        print("執行 chewing-editor 時發生錯誤")
        return False

def upload_to_drive(local_file, drive_file, drive_name):
    """上傳檔案到 drive"""
    try:
        cmd = ["rclone", "copy", local_file, f"jokersaysjoke44_linux:{drive_file}"]
        subprocess.run(cmd, check=True)
        print(f"已上傳到 drive")
        return True
    except FileNotFoundError:
        print("錯誤：找不到 rclone，請確認已安裝！")
        return False
    except subprocess.CalledProcessError:
        print("執行 rclone 時發生錯誤")
        return False


def main():
    while True:
        load_dotenv()
        CHEWING_EDITOR_JSON_PATH = Path(os.getenv("CHEWING_EDITOR_JSON_PATH"))
        DRIVE_FOLDER = os.getenv("DRIVE_FOLDER")
        DRIVE_NAME = os.getenv("DRIVE_NAME")

        os.system('cls' if os.name == 'nt' else 'clear')
        print("新酷音詞庫編輯器")
        chinese_text = input("請輸入中文文字: ")
        json_entry = chinese_to_json(chinese_text)
        save_to_json(json_entry, CHEWING_EDITOR_JSON_PATH)
        upload_to_drive(CHEWING_EDITOR_JSON_PATH, DRIVE_FOLDER, DRIVE_NAME)

        if reload_chewing():
            continue

if __name__ == "__main__":
    main()
