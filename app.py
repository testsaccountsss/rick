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
    "labels": ["INSTA followers", "Age", "Posts", "Net worth"],
    "left_values": ["690k", "23 years", "1.2k", "460k"],
    "right_values": ["115", "7 days", "3", "1€"]
}

def make_square(img, size=200, color=(255,255,255)):
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
            # 기존 3개 항목을 4개로 업데이트
            if len(config.get("labels", [])) == 3:
                config["labels"] = DEFAULT_CONFIG["labels"]
                config["left_values"] = DEFAULT_CONFIG["left_values"]
                config["right_values"] = DEFAULT_CONFIG["right_values"]
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
        label4 = st.text_input("항목4 이름", config["labels"][3])
    with cols[1]:
        left1 = st.text_input("왼쪽 값1", config["left_values"][0])
        left2 = st.text_input("왼쪽 값2", config["left_values"][1])
        left3 = st.text_input("왼쪽 값3", config["left_values"][2])
        left4 = st.text_input("왼쪽 값4", config["left_values"][3])
    with cols[2]:
        right1 = st.text_input("오른쪽 값1", config["right_values"][0])
        right2 = st.text_input("오른쪽 값2", config["right_values"][1])
        right3 = st.text_input("오른쪽 값3", config["right_values"][2])
        right4 = st.text_input("오른쪽 값4", config["right_values"][3])

    submitted = st.form_submit_button("VS 이미지 만들기")

# --- 입력값 저장 ---
config = {
    "left_img": left_img_name,
    "right_img": right_img_name,
    "left_name": left_name,
    "right_name": right_name,
    "labels": [label1, label2, label3, label4],
    "left_values": [left1, left2, left3, left4],
    "right_values": [right1, right2, right3, right4]
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
        img = Image.new("RGB", (200,200), (220,220,220))
    return make_square(img)

left_img = get_image(left_img_file, left_img_name)
right_img = get_image(right_img_file, right_img_name)

# --- VS 이미지 생성 및 출력 ---
if submitted:
    # 크기를 줄이고 비율 조정
    fig, ax = plt.subplots(figsize=(10, 8))  # 높이를 8로 증가
    ax.axis('off')
    
    # 전체 배경 박스
    rect = patches.FancyBboxPatch(
        (0.08, 0.08), 0.84, 0.84,
        boxstyle="round,pad=0.02", linewidth=2,
        edgecolor='#999999', facecolor='white', zorder=1
    )
    ax.add_patch(rect)
    
    # 이미지 배치 (상단) - 위치와 크기 조정
    img_size = 0.22
    img_y = 0.68
    left_img_x = 0.18
    right_img_x = 0.60
    
    # 이미지 표시
    ax.imshow(left_img, extent=[left_img_x, left_img_x+img_size, img_y, img_y+img_size], zorder=2)
    ax.imshow(right_img, extent=[right_img_x, right_img_x+img_size, img_y, img_y+img_size], zorder=2)
    
    # 이름 표시 (이미지 아래) - 위치 조정
    name_y = 0.64
    ax.text(left_img_x + img_size/2, name_y, left_name, fontsize=18, ha='center', va='top', 
            fontweight='bold', color='#333333', zorder=3)
    ax.text(0.5, name_y, "VS.", fontsize=26, ha='center', va='top', 
            fontweight='bold', color='#ff4444', zorder=3)
    ax.text(right_img_x + img_size/2, name_y, right_name, fontsize=18, ha='center', va='top', 
            fontweight='bold', color='#333333', zorder=3)
    
    # 구분선
    ax.plot([0.12, 0.88], [0.58, 0.58], color='#cccccc', linewidth=2, zorder=3)
    
    # 비교 항목들 - 4개 항목으로 조정
    row_positions = [0.48, 0.38, 0.28, 0.18]  # 4개 항목으로 간격 조정
    
    # 각 열의 x 위치 정의
    left_col_x = left_img_x + img_size/2
    center_col_x = 0.5
    right_col_x = right_img_x + img_size/2
    
    for i, y_pos in enumerate(row_positions):
        # 왼쪽 값
        ax.text(left_col_x, y_pos, config["left_values"][i], 
                fontsize=16, ha='center', va='center', color='#444444', zorder=3)
        # 중앙 라벨
        ax.text(center_col_x, y_pos, config["labels"][i], 
                fontsize=16, ha='center', va='center', color='#222222', zorder=3)
        # 오른쪽 값
        ax.text(right_col_x, y_pos, config["right_values"][i], 
                fontsize=16, ha='center', va='center', color='#444444', zorder=3)
        
        # 항목 간 구분선 (더 짧고 연하게)
        if i < len(row_positions) - 1:
            ax.plot([0.15, 0.85], [y_pos - 0.05, y_pos - 0.05], color='#e8e8e8', linewidth=1, zorder=3)
    
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.tight_layout()
    
    # 이미지 저장 및 출력 - 크기 제한 추가
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150, facecolor='white')
    buf.seek(0)
    
    # 컬럼을 사용해서 중앙에 배치하고 크기 제한
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(buf, width=720)  # 고정 폭 설정 (600 -> 720, 120% 확대)
    
    plt.close(fig)
    st.success("VS 이미지가 생성되었습니다!")
