from seleniumbase import Driver
import pandas as pd
import time
import random
from datetime import datetime
import os

FILE_NAME = "steamdb_data.xlsx"
TARGET_COUNT = 10000   # số game muốn cào

def is_cloudflare(driver):
    titles = [
        "just a moment",
        "verify you are human",
        "attention required"
    ]
    return any(t in driver.title.lower() for t in titles)

def scrape_steamdb():
    data = []
    scraped_links = set()
    stt = 1

    # resume nếu có file cũ
    if os.path.exists(FILE_NAME):
        old = pd.read_excel(FILE_NAME)
        data = old.to_dict("records")
        scraped_links = set(old["Link"].tolist())
        stt = len(data) + 1
        print(f" Resume: đã có {len(data)} game")

    driver = Driver(uc=True, headless=False)

    try:
        print(" Mở SteamDB Charts...")
        driver.uc_open("https://steamdb.info/charts/")
        time.sleep(4)

        # chỉnh số game hiển thị
        try:
            select = driver.find_element(
                "css selector",
                "select[name='DataTables_Table_0_length']"
            )
            driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('change'));",
                select,
                str(TARGET_COUNT)
            )
            time.sleep(3)
        except:
            pass

        # LẤY LIST GAME
        print(" Lấy danh sách game...")
        games = []
        rows = driver.find_elements("css selector", "tr.app")

        for r in rows:
            try:
                cols = r.find_elements("tag name", "td")
                games.append({
                    "Tên Game": cols[2].text.strip(),
                    "Link": cols[2].find_element("tag name", "a").get_attribute("href"),
                    "Current Players": cols[3].text.strip(),
                    "24h Peak": cols[4].text.strip(),
                    "All-Time Peak": cols[5].text.strip()
                })
            except:
                continue

        #LOOP CÀO 
        for game in games:
            if len(data) >= TARGET_COUNT:
                break

            link = game["Link"]
            if link in scraped_links:
                continue

            print(f"\n➡ [{stt}] Đang cào: {game['Tên Game']}")

            driver.uc_open(link)
            time.sleep(random.uniform(1.8, 2.6))

            if is_cloudflare(driver):
                continue

            def get_val(label):
                try:
                    xp = f"//td[normalize-space()='{label}']/following-sibling::td"
                    return driver.find_element("xpath", xp).text.strip()
                except:
                    return "N/A"

            record = {
                "STT": stt,
                **game,
                "App Type": get_val("App Type"),
                "Developer": get_val("Developer"),
                "Publisher": get_val("Publisher"),
                "Release Date": get_val("Release Date"),
                "Technologies": get_val("Technologies"),
                "Supported Systems": get_val("Supported Systems"),
                "Last Record Update": get_val("Last Record Update"),
                "Scraped At": datetime.now().strftime("%H:%M:%S %d-%m-%Y")
            }

            data.append(record)
            scraped_links.add(link)
            stt += 1

            # ghi ngay mỗi game để chống crash
            pd.DataFrame(data).to_excel(FILE_NAME, index=False)
            print("Đã lưu")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_steamdb()
