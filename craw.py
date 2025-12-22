# -------------------------------
# CÀO DỮ LIỆU GAME RATINGS TỪ STEAMDB (ĐẦY ĐỦ CỘT, AN TOÀN)
# -------------------------------

import sqlite3, os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

# -------------------------------
# 1. HÀM TIỆN ÍCH CHUYỂN ĐỔI AN TOÀN
# -------------------------------

def safe_int(text):
    """Chuyển chuỗi thành int, nếu rỗng hoặc lỗi thì trả về None."""
    try:
        return int(text.replace(",", "").strip())
    except:
        return None

def safe_float(text):
    """Chuyển chuỗi thành float, nếu rỗng hoặc lỗi thì trả về None."""
    try:
        return float(text.replace("%", "").strip())
    except:
        return None

# -------------------------------
# 2. TẠO CƠ SỞ DỮ LIỆU SQLITE
# -------------------------------

DB_FILE = r"C:\Users\Binh An\OneDrive\Máy tính\CODER\.vscode\Y3\MNM\osds-ht1b-an\cuoiky\SteamDB_Games_Full.db"

# Tạo thư mục cha nếu chưa có
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

# Kết nối tới SQLite
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Tạo bảng games với đầy đủ cột
cursor.execute("""
CREATE TABLE IF NOT EXISTS games (
    app_id INTEGER PRIMARY KEY,      -- ID game trên Steam
    name TEXT,                       -- Tên game
    score REAL,                      -- Giá hiển thị (chuỗi, vì có ký hiệu ₫)
    price TEXT,  
    rating TEXT,                     -- % đánh giá tích cực
    release TEXT,                    -- Ngày phát hành
    follows INTEGER,                 -- Số người theo dõi
    reviews INTEGER,                 -- Tổng số review
    peak INTEGER,                    -- Peak concurrent players
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()

# -------------------------------
# 3. CÀO DỮ LIỆU
# -------------------------------

try:
    driver = webdriver.Firefox()
    driver.get("https://steamdb.info/stats/gameratings/?sort=id_asc")
    time.sleep(3)  # chờ trang load

    # Đổi dropdown từ 100 -> All
    dropdown = driver.find_element(By.ID, "dt-length-0")
    Select(dropdown).select_by_value("-1")
    time.sleep(5)  # chờ bảng load lại toàn bộ dữ liệu

    # Lấy tất cả các thẻ game
    rows = driver.find_elements(By.CSS_SELECTOR, "tr.app")

    saved = 0
    for r in rows:  # demo: chỉ lấy 5 game đầu tiên
        try:
            app_id = int(r.get_attribute("data-appid"))
            cols = r.find_elements(By.TAG_NAME, "td")

            # Cấu trúc cột: [ID, Name, Price, %, Release, Follows, Reviews, Peak]
            name = cols[2].text.strip()
            score   = safe_float(cols[3].text)   # cột %
            price   = cols[4].text.strip()
            rating  = cols[5].text.strip()   # cột Rating
            release = cols[6].text.strip()
            follows = safe_int(cols[7].text)
            reviews = safe_int(cols[8].text)
            peak = safe_int(cols[9].text)


            # Lưu vào DB
            cursor.execute("""INSERT OR REPLACE INTO games 
    VALUES (?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)""",
    (app_id, name, score, price, rating, release, follows, reviews, peak))
            conn.commit()
            saved += 1
            print(f"Đã lưu: {app_id} - {name[:40]}...")

        except Exception as e:
            print("Lỗi:", e)

    print(f"✅ Tổng cộng đã lưu {saved} game.")

finally:
    driver.quit()
    conn.close()