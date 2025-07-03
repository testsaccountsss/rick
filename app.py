import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.table as tbl
import json
import os
import io

CONFIG_FILE = "vs_config.json"

DEFAULT_CONFIG = {
    "left_img": "left.png",
    "right_img": "right.png",
    "left_name": "Rick Astley",
    "right_name": "_rickroll",
    "labels": ["INSTA followers", "Age", "Net worth"],
    "left_values": ["690k", "23 years", "460k"],
    "right_values": ["115", "7 days", "1€"]
}

def make_square(img, size=160, color=(255,255,255)):
    w, h = img.size
    if w == h:
        return img.resize((size, size))
    max_side = max(w, h)
    new_img = Image.new('RGB', (max_side, max_side), color)
    new_img.paste(img, ((max_side-w)//2, (max_side-h)//2))
    return new_img.resize((size, size))

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            for k in DEFAULT_CONFIG:
                if k not in config or not config[k]:
                    config[k] = DEFAULT_CONFIG[k]
            return config
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="VS Meme Generator", layout="centered")
st.title("VS Meme Generator")

if "config" not in st.session_state:
    st.session_state.config = load_config()

config = st.session_state.config

with st.form("vs_form"):
    col1, col2 = st.columns(2)
    with col1:
        left_img_file = st.file_uploader("왼쪽 이미지 (left.png)", type=["png", "jpg"], key="left_img")
        left_img_name = st.text_input("왼쪽 이미지 파일명", config["left_img"])
        left_name = st.text_input("왼쪽 이름", config["left_name"])
    with col2:
        right_img_file = st.file_uploader("오른쪽 이미지 (right.png)", type=["png", "jpg"], key="right_img")
        right_img_name = st.text_input("오른쪽 이미지 파일명", config["right_img"])
        right_name = st.text_input("오른쪽 이름", config["right_name"])

    st.markdown("#### 비교 항목")
    cols = st.columns([2,1,1,1])
    with cols[0]:
        label1 = st.text_input("항목1 이름", config["labels"][0])
        label2 = st.text_input("항목2 이름", config["labels"][1])
        label3 = st.text_input("항목3 이름", config["labels"][2])
    with cols[1]:
        left1 = st.text_input("왼쪽 값1", config["left_values"][0])
        left2 = st.text_input("왼쪽 값2", config["left_values"][1])
        left3 = st.text_input("왼쪽 값3", config["left_values"][2])
    with cols[2]:
        right1 = st.text_input("오른쪽 값1", config["right_values"][0])
        right2 = st.text_input("오른쪽 값2", config["right_values"][1])
        right3 = st.text_input("오른쪽 값3", config["right_values"][2])

    submitted = st.form_submit_button("VS 이미지 만들기")

config = {
    "left_img": left_img_name,
    "right_img": right_img_name,
    "left_name": left_name,
    "right_name": right_name,
    "labels": [label1, label2, label3],
    "left_values": [left1, left2, left3],
    "right_values": [right1, right2, right3]
}
st.session_state.config = config
save_config(config)

def get_image(file, fallback_path):
    if file is not None:
        img = Image.open(file)
    elif os.path.exists(fallback_path):
        img = Image.open(fallback_path)
    else:
        img = Image.new("RGB", (160,160), (220,220,220))
    return make_square(img)

left_img = get_image(left_img_file, left_img_name)
right_img = get_image(right_img_file, right_img_name)

if submitted:
    n = 3
    cell_h = 0.18  # 표 셀 높이
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.axis('off')

    # 표 데이터 구성
    table_data = []
    for i in range(n):
        table_data.append([
            config["left_values"][i],
            config["labels"][i],
            config["right_values"][i]
        ])

    # 표 생성 (3행 3열)
    table = ax.table(
        cellText=table_data,
        colLabels=[config["left_name"], "VS.", config["right_name"]],
        cellLoc='center',
        loc='center',
        cellColours=[["#fff"]*3 for _ in range(n)],
        colColours=["#f5f5f5", "#fff0f0", "#f5f5f5"]
    )

    # 표 스타일 조정
    table.auto_set_font_size(False)
    table.set_fontsize(15)
    table.scale(1.2, 2.1)

    # 헤더(이름/VS) 폰트 크기/색상
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_fontsize(17)
            cell.set_text_props(weight='bold')
        if col == 1:
            cell.set_text_props(color='red', weight='bold')
        if row == -1:
            cell.set_height(0.13)
        else:
            cell.set_height(cell_h)
        cell.set_linewidth(1.2)
        cell.set_edgecolor("#cccccc")

    # 이미지 배치 (왼쪽/오른쪽 헤더 셀 위에)
    # 좌표: (x, y, w, h) = (0, 1, 1, 1) 등으로 표 위에 이미지 오버레이
    table_pos = table.get_window_extent(fig.canvas.get_renderer())
    ax_pos = ax.get_position()
    # 이미지 위치는 표의 좌상단/우상단에 맞춰서 배치
    img_y = 0.82
    img_size = 0.18
    ax.imshow(left_img, extent=(-0.05, 0.25, img_y, img_y+img_size), zorder=10)
    ax.imshow(right_img, extent=(0.75, 1.05, img_y, img_y+img_size), zorder=10)

    # VS. 텍스트 강조 (헤더 셀 중앙)
    ax.text(0.5, 0.97, "VS.", fontsize=24, color='red', ha='center', va='center', fontweight='bold', zorder=11)

    plt.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.08)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=180)
    buf.seek(0)
    st.image(buf, width=540)
    plt.close(fig)
    st.success("VS 이미지가 생성되었습니다!")
