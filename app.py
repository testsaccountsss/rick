import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
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

st.set_page_config(page_title="VS Meme Generator", layout="wide")
st.title("VS Meme Generator")

# --- 입력값 불러오기/초기화 ---
if "config" not in st.session_state:
    st.session_state.config = load_config()

config = st.session_state.config

# --- 입력 폼 ---
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

# --- 입력값 저장 ---
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

# --- 이미지 불러오기 ---
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

# --- VS 이미지 생성 및 출력 ---
if submitted:
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.axis('off')

    # 전체 박스 - 더 넓은 마진과 둥근 모서리
    box_x, box_y, box_w, box_h = 0.05, 0.05, 0.90, 0.90
    rect = patches.FancyBboxPatch(
        (box_x, box_y), box_w, box_h,
        boxstyle="round,pad=0.015", linewidth=2.5,
        edgecolor='#999999', facecolor='white', zorder=1
    )
    ax.add_patch(rect)

    # 이미지 영역 계산 - 더 정확한 중앙 정렬
    content_x = box_x + 0.04
    content_w = box_w - 0.08
    content_y = box_y + 0.04
    content_h = box_h - 0.08
    
    # 이미지 크기와 위치 (상단 30% 영역 사용)
    img_area_h = content_h * 0.35
    img_size = min(content_w * 0.35, img_area_h * 0.8)
    img_y = content_y + content_h - img_size - 0.02
    
    # 이미지 중앙 정렬을 위한 x 좌표 계산
    left_img_x = content_x + content_w * 0.25 - img_size/2
    right_img_x = content_x + content_w * 0.75 - img_size/2
    
    # 이미지 배치
    ax.imshow(left_img, extent=(left_img_x, left_img_x+img_size, img_y, img_y+img_size), zorder=2)
    ax.imshow(right_img, extent=(right_img_x, right_img_x+img_size, img_y, img_y+img_size), zorder=2)

    # 이름 텍스트 - 이미지 중앙에 정렬
    name_y = img_y - 0.03
    left_name_x = left_img_x + img_size/2
    right_name_x = right_img_x + img_size/2
    vs_x = content_x + content_w/2
    
    ax.text(left_name_x, name_y, left_name, fontsize=18, ha='center', va='top', 
            fontweight='bold', zorder=3, color='#333333')
    ax.text(vs_x, name_y, "VS.", fontsize=28, color='#ff4444', ha='center', va='top', 
            fontweight='bold', zorder=3)
    ax.text(right_name_x, name_y, right_name, fontsize=18, ha='center', va='top', 
            fontweight='bold', zorder=3, color='#333333')

    # VS 아래 구분선
    line_y = name_y - 0.05
    line_x1 = content_x + 0.02
    line_x2 = content_x + content_w - 0.02
    ax.plot([line_x1, line_x2], [line_y, line_y], color='#cccccc', linewidth=2, zorder=3)

    # 비교 항목 영역 계산
    n = 3
    items_start_y = line_y - 0.03
    items_h = content_y + content_h * 0.15 - items_start_y
    dy = items_h / n
    
    # 각 항목별 행
    for i in range(n):
        y = items_start_y - i * dy
        
        # 값들을 이름과 동일한 x 좌표에 배치
        ax.text(left_name_x, y, config["left_values"][i], fontsize=16, ha='center', va='center', 
                zorder=3, color='#444444', fontweight='500')
        ax.text(vs_x, y, config["labels"][i], fontsize=16, ha='center', va='center', 
                fontweight='bold', zorder=3, color='#222222')
        ax.text(right_name_x, y, config["right_values"][i], fontsize=16, ha='center', va='center', 
                zorder=3, color='#444444', fontweight='500')
        
        # 항목 간 구분선 (마지막 항목 제외)
        if i < n-1:
            sep_y = y - dy/2
            ax.plot([line_x1, line_x2], [sep_y, sep_y], color='#e0e0e0', linewidth=1, zorder=3)

    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.tight_layout()

    # 이미지 저장 및 출력
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=250, facecolor='white')
    buf.seek(0)
    st.image(buf, use_column_width=True)
    plt.close(fig)
    st.success("VS 이미지가 생성되었습니다!")
