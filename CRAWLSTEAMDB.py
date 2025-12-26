import time
import pandas as pd
from seleniumbase import Driver
from datetime import datetime

def scrape_steam_basic():
    file_name = "steam_basic.xlsx"
    target_count = 50   # số game cần cào

    driver = Driver(uc=True, headless=False)
    data = []

    try:
        # 1. Mở trang charts
        driver.get("https://steamdb.info/charts/")
        time.sleep(5)

        # 2. Lấy danh sách game
        rows = driver.find_elements("css selector", "tr.app")[:target_count]

        game_list = []
        for row in rows:
            cols = row.find_elements("tag name", "td")
            game_list.append({
                "Tên Game": cols[2].text.strip(),
                "Link": cols[2].find_element("tag name", "a").get_attribute("href"),
                "Current Players": cols[3].text.strip(),
                "24h Peak": cols[4].text.strip(),
                "All-Time Peak": cols[5].text.strip()
            })

        # 3. Vào từng game lấy chi tiết
        for game in game_list:
            driver.get(game["Link"])
            time.sleep(5)

            def get_value(label):
                try:
                    return driver.find_element(
                        "xpath",
                        f"//td[normalize-space()='{label}']/following-sibling::td"
                    ).text.strip()
                except:
                    return "N/A"

            game.update({
                "Developer": get_value("Developer"),
                "Publisher": get_value("Publisher"),
                "Release Date": get_value("Release Date"),
                "App Type": get_value("App Type"),
                "Thời gian cào": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            })

            data.append(game)
            print("Đã cào:", game["Tên Game"])

        # 4. Lưu file Excel
        pd.DataFrame(data).to_excel(file_name, index=False)
        print("Hoàn thành, đã lưu file:", file_name)

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_steam_basic()


