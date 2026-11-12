import os
import urllib.request
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm

# 1. Setup Thai Font in Matplotlib (โหลดอัตโนมัติ + ตรวจว่าไฟล์ฟอนต์ใช้ได้จริง)
FONT_PATH = "Kanit-Regular.ttf"
FONT_URLS = [
    "https://github.com/google/fonts/raw/main/ofl/kanit/Kanit-Regular.ttf",
    "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/kanit/Kanit-Regular.ttf",
    "https://raw.githubusercontent.com/google/fonts/main/ofl/kanit/Kanit-Regular.ttf",
]

def _is_valid_font(path):
    try:
        if os.path.getsize(path) < 20000:
            return False
        with open(path, "rb") as f:
            return f.read(4) in (b"\x00\x01\x00\x00", b"OTTO", b"true")
    except OSError:
        return False

def _has_thai(path):
    """เช็คว่าไฟล์ฟอนต์มีอักษรไทยจริง (ก = U+0E01)"""
    try:
        return fm.get_font(path).get_char_index(0x0E01) != 0
    except Exception:
        return False

def load_thai_font():
    # 1) ฟอนต์ Kanit: ใช้ไฟล์ที่มีอยู่ หรือโหลดใหม่ถ้ายังไม่มี/ไฟล์เสีย
    if not (_is_valid_font(FONT_PATH) and _has_thai(FONT_PATH)):
        if os.path.exists(FONT_PATH):
            os.remove(FONT_PATH)
        for url in FONT_URLS:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=20) as r, open(FONT_PATH, "wb") as f:
                    f.write(r.read())
                if _is_valid_font(FONT_PATH) and _has_thai(FONT_PATH):
                    break
                os.remove(FONT_PATH)
            except Exception:
                if os.path.exists(FONT_PATH):
                    os.remove(FONT_PATH)
    if os.path.exists(FONT_PATH) and _has_thai(FONT_PATH):
        return fm.FontProperties(fname=FONT_PATH)
    # 2) สำรอง: หาฟอนต์ไทยที่ติดตั้งในเครื่อง (ชื่อที่รู้จักก่อน แล้วสแกนทั้งหมด)
    preferred = ["Noto Sans Thai", "Sarabun", "TH Sarabun New", "Tahoma", "Leelawadee UI",
                 "Garuda", "Loma", "Waree", "Norasi", "Kinnari", "Umpush", "Laksaman"]
    for name in preferred:
        try:
            path = fm.findfont(name, fallback_to_default=False)
            if _has_thai(path):
                return fm.FontProperties(fname=path)
        except Exception:
            continue
    for path in sorted({f.fname for f in fm.fontManager.ttflist}):
        if _has_thai(path):
            return fm.FontProperties(fname=path)
    return None

THAI_FONT = load_thai_font()

def font_kw(size):
    """คืนค่า font สำหรับใส่ในข้อความของกราฟ (ระบุฟอนต์ตรง ๆ ไม่พึ่ง rcParams)"""
    if THAI_FONT is None:
        return {"fontsize": size}
    fp = THAI_FONT.copy()
    fp.set_size(size)
    return {"fontproperties": fp}

plt.rcParams["axes.unicode_minus"] = False

# 2. Localized Thai Dataset
thai_data = [
    # เทนนิส (Tennis)
    {101: ("ไม้เทนนิส Wilson Federer", "เทนนิส", "ผู้เริ่มต้น", 45.0, "ต่ำ", 4.2)},
    {102: ("ไม้เทนนิส Babolat Pure Drive", "เทนนิส", "ระดับสูง", 219.0, "สูง", 4.8)},
    {103: ("ไม้เทนนิส Head Ti.S6", "เทนนิส", "ระดับกลาง", 99.0, "ปานกลาง", 4.5)},
    {104: ("ลูกเทนนิส Penn Championship (แพ็ก 3 ลูก)", "เทนนิส", "ผู้เริ่มต้น", 4.99, "ต่ำ", 4.7)},
    # บาสเกตบอล (Basketball)
    {105: ("ลูกบาสเกตบอล Spalding TF-1000", "บาสเกตบอล", "ระดับสูง", 69.99, "ปานกลาง", 4.6)},
    {106: ("ลูกบาสเกตบอล Wilson NCAA Replica", "บาสเกตบอล", "ระดับกลาง", 29.99, "ต่ำ", 4.4)},
    {107: ("แป้นบาสเกตบอลปรับระดับได้ Lifetime", "บาสเกตบอล", "ระดับกลาง", 249.99, "สูง", 4.3)},
    {108: ("ถุงเท้าบาสเกตบอล Nike Elite", "บาสเกตบอล", "ผู้เริ่มต้น", 14.0, "ต่ำ", 4.5)},
    # วิ่ง (Running)
    {109: ("รองเท้าวิ่ง Nike Pegasus 40", "วิ่ง", "ระดับกลาง", 130.0, "ปานกลาง", 4.7)},
    {110: ("รองเท้าวิ่ง Asics Gel-Kayano 30", "วิ่ง", "ระดับสูง", 160.0, "สูง", 4.8)},
    {111: ("รองเท้าวิ่ง Decathlon Kalenji Run Active", "วิ่ง", "ผู้เริ่มต้น", 24.99, "ต่ำ", 4.0)},
    {112: ("นาฬิกา GPS Garmin Forerunner 55", "วิ่ง", "ระดับกลาง", 199.99, "สูง", 4.6)},
    # ฟุตบอล (Soccer)
    {113: ("ลูกฟุตบอล Adidas Al Rihla World Cup", "ฟุตบอล", "ระดับสูง", 160.0, "สูง", 4.9)},
    {114: ("รองเท้าสตั๊ด Nike Mercurial Vapor Academy", "ฟุตบอล", "ระดับกลาง", 85.0, "ปานกลาง", 4.3)},
    {115: ("รองเท้าสตั๊ด Puma Future Play FG/AG", "ฟุตบอล", "ผู้เริ่มต้น", 55.0, "ปานกลาง", 4.1)},
    {116: ("สนับแข้ง Adidas Tiro Club", "ฟุตบอล", "ผู้เริ่มต้น", 12.0, "ต่ำ", 4.2)},
    {117: ("ตาข่ายประตูฟุตบอล Kwik Goal", "ฟุตบอล", "ระดับสูง", 350.0, "สูง", 4.7)},
    {118: ("ลูกบาสเกตบอล Wilson Evolution Game", "บาสเกตบอล", "ระดับสูง", 79.95, "ปานกลาง", 4.8)},
    {119: ("กระเป๋าเทนนิส Babolat Team", "เทนนิส", "ระดับกลาง", 65.0, "ปานกลาง", 4.4)},
    {120: ("กางเกงวิ่งขาสั้น Under Armour", "วิ่ง", "ผู้เริ่มต้น", 28.0, "ต่ำ", 4.3)}
]

flat_thai_data = []
for item in thai_data:
    for prod_id, details in item.items():
        flat_thai_data.append({
            "Product_ID": prod_id,
            "Product_Name": details[0],
            "Sport": details[1],
            "Skill_Level": details[2],
            "Price": details[3],
            "Budget_Category": details[4],
            "Rating": details[5]
        })

df_equipment = pd.DataFrame(flat_thai_data)

# 3. Streamlit UI Layout
st.set_page_config(page_title="ระบบแนะนำอุปกรณ์กีฬาอัจฉริยะ", layout="wide")

st.title("🏆 ระบบแนะนำอุปกรณ์กีฬาอัจฉริยะ (Sports Equipment Recommendation System)")
st.markdown("**ค้นหาอุปกรณ์กีฬาที่ตอบโจทย์ความต้องการและระดับทักษะของคุณได้อย่างรวดเร็วและคุ้มค่าที่สุด**")
st.write("--- ")

# 4. Sidebar Filter Widgets
st.sidebar.header("⚙️ ตัวกรองข้อมูล (Filters)")

# Sport category
sport_options = ["ทั้งหมด"] + list(df_equipment['Sport'].unique())
selected_sport = st.sidebar.selectbox("⚽ เลือกประเภทกีฬา", sport_options)

# Budget category
budget_options = ["ทั้งหมด"] + list(df_equipment['Budget_Category'].unique())
selected_budget = st.sidebar.selectbox("💰 ระดับงบประมาณ", budget_options)

# Skill level
skill_options = ["ทั้งหมด"] + list(df_equipment['Skill_Level'].unique())
selected_skill = st.sidebar.selectbox("👟 ระดับทักษะผู้เล่น", skill_options)

# Price Range slider
min_price_val = float(df_equipment['Price'].min())
max_price_val = float(df_equipment['Price'].max())
price_range = st.sidebar.slider(
    "💸 ช่วงราคา (USD)",
    min_value=0.0,
    max_value=400.0,
    value=(0.0, 400.0)
)

# 5. Filter Recommendation Logic
filtered_df = df_equipment.copy()

if selected_sport != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df['Sport'] == selected_sport]

if selected_budget != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df['Budget_Category'] == selected_budget]

if selected_skill != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df['Skill_Level'] == selected_skill]

filtered_df = filtered_df[
    (filtered_df['Price'] >= price_range[0]) &
    (filtered_df['Price'] <= price_range[1])
]

# Sort recommendations: highest rating first, then lowest price
filtered_df = filtered_df.sort_values(by=['Rating', 'Price'], ascending=[False, True])

# 6. Main Content Area
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📦 รายการอุปกรณ์กีฬาที่แนะนำ")
    if filtered_df.empty:
        st.warning("⚠️ ไม่พบอุปกรณ์ที่ตรงตามเงื่อนไข กรุณาลองปรับลดตัวกรองใหม่อีกครั้ง")
    else:
        st.dataframe(filtered_df.rename(columns={
            "Product_ID": "รหัสสินค้า",
            "Product_Name": "ชื่อสินค้า",
            "Sport": "ประเภทกีฬา",
            "Skill_Level": "ระดับทักษะ",
            "Price": "ราคา (USD)",
            "Budget_Category": "งบประมาณ",
            "Rating": "คะแนนรีวิว"
        }), use_container_width=True, hide_index=True)

with col2:
    st.subheader("📊 การแจกแจงวิเคราะห์ความคุ้มค่า")
    if not filtered_df.empty:
        if THAI_FONT is None:
            st.caption("⚠️ ไม่พบฟอนต์ภาษาไทยในระบบ ตัวอักษรไทยในกราฟอาจแสดงเป็นกล่อง")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.scatterplot(
            ax=ax,
            data=filtered_df,
            x="Price",
            y="Rating",
            hue="Sport",
            style="Skill_Level",
            s=150,
            palette="Set1",
            alpha=0.9
        )
        ax.set_title("วิเคราะห์ความคุ้มค่า (ราคา vs คะแนนรีวิว)", pad=15, **font_kw(15))
        ax.set_xlabel("ราคา (USD)", **font_kw(12))
        ax.set_ylabel("คะแนนรีวิว (1.0 ถึง 5.0)", **font_kw(12))
        ax.set_xlim(left=max(0, price_range[0] - 10), right=price_range[1] + 10)
        ax.set_ylim(0.5, 5.5)
        ax.grid(True, linestyle="--", alpha=0.5)
        # ตัวอักษรไทยในกล่องคำอธิบาย (legend)
        legend = ax.get_legend()
        if legend is not None and THAI_FONT is not None:
            for t in legend.get_texts():
                t.set_fontproperties(THAI_FONT)
            legend.get_title().set_fontproperties(THAI_FONT)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("ไม่มีข้อมูลเพื่อสร้างแผนภูมิการวิเคราะห์")
