from seleniumbase import Driver
import pandas as pd
import time
import random
from datetime import datetime
import os

def auto_bypass_verify(driver):
    captcha_indicators = ["Verify you are human", "Just a moment...", "cloudflare-static"]
    if any(ind.lower() in driver.title.lower() for ind in captcha_indicators):
        print(f"   [!] Cloudflare chặn đường. Đang thử giải...")
        try:
            driver.uc_gui_handle_captcha()
            time.sleep(5)
            return True
        except: pass
    return False

def scrape_steam_resume():
    file_name = "cao_10000_steam.xlsx"
    target_count = 1000    #cào 10000 dòng cho sau này
    
    # ĐỌC DỮ LIỆU CŨ ĐỂ CHẠY TIẾP 
    scraped_links = []
    final_data = []
    if os.path.exists(file_name):
        df_old = pd.read_excel(file_name)
        final_data = df_old.to_dict('records')
        scraped_links = df_old['Link'].tolist()
        print(f"--- Tìm thấy dữ liệu cũ. Đã có {len(scraped_links)} game. Sẽ cào tiếp... ---")

    driver = Driver(uc=True, headless=False)

    try:
        # LẤY DANH SÁCH TỪ CHARTS 
        print("--- Đang vào trang Charts để lấy danh sách mới nhất ---")
        driver.uc_open("https://steamdb.info/charts/")
        time.sleep(5)
        auto_bypass_verify(driver)

        chart_rows = driver.find_elements("css selector", "tr.app")[:target_count]
        temp_list = []
        for row in chart_rows:
            try:
                cols = row.find_elements("tag name", "td")
                link = cols[2].find_element("tag name", "a").get_attribute("href")
                if link not in scraped_links: # Chỉ lấy những link chưa cào
                    temp_list.append({
                        "STT": cols[0].text.strip(),
                        "Tên Game": cols[2].text.strip(),
                        "Link": link,
                        "Current Players": cols[3].text.strip(),
                        "24h Peak": cols[4].text.strip(),
                        "All-Time Peak": cols[5].text.strip()
                    })
            except: continue

        # CÀO CHI TIẾT VÀ LƯU TỨC THÌ 
        for i, game in enumerate(temp_list):
            try:
                if i > 0 and i % 20 == 0:
                    print("\n[!] Đã cào được 20 game. Bạn nên tắt script, đổi IP rồi chạy lại để an toàn.")
                
                driver.uc_open(game["Link"])
                time.sleep(random.uniform(5.5, 8.5))
                auto_bypass_verify(driver)

                def get_row_val(label):
                    try:
                        xpath = f"//td[normalize-space()='{label}']/following-sibling::td"
                        return driver.find_element("xpath", xpath).text.strip()
                    except: return "N/A"

                nums = driver.find_elements("css selector", ".header-thing-number")
                review_val = nums[0].text.strip() if nums else "N/A"

                game.update({
                    "App Type": get_row_val("App Type"),
                    "Developer": get_row_val("Developer"),
                    "Publisher": get_row_val("Publisher"),
                    "Ngày phát hành": get_row_val("Release Date"),
                    "Technologies": get_row_val("Technologies"),
                    "Supported Systems": get_row_val("Supported Systems"),
                    "Last Record Update": get_row_val("Last Record Update"),
                    "Lượt Review": review_val,
                    "Thời gian cào thành công": datetime.now().strftime("%H:%M:%S %d-%m-%Y")
                })

                final_data.append(game)
                
                # GHI ĐÈ FILE 
                pd.DataFrame(final_data).to_excel(file_name, index=False)
                print(f"[{len(final_data)}] Đã lưu: {game['Tên Game']}")

            except Exception as e:
                print(f"Lỗi: {e}")
                continue

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_steam_resume()

# code chưa có phần cào giá game & discount
# bị chặn vpn nên nhiều lúc phải verify thủ công 