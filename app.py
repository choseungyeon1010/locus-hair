import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os

# ---------------------------------------------------------
# [설정] 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(page_title="Locus Hair", page_icon="💇‍♂️", layout="wide")

# ---------------------------------------------------------
# [디자인] CSS 스타일링
# ---------------------------------------------------------
st.markdown("""
    <style>
    .big-font { 
        font-size: 80px !important; 
        font-weight: 900; 
        color: #000000 !important; 
        margin-bottom: 20px;
    }
    .medium-font { 
        font-size: 35px !important; 
        font-weight: bold; 
        color: #333333;
    }
    .status-box { 
        padding: 50px; 
        border-radius: 20px; 
        background-color: #ffffff; 
        text-align: center; 
        border: 4px solid #333;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    div[data-testid="stTextInput"] input {
        font-size: 30px !important;
        height: 70px !important;
        padding: 10px 20px !important;
        border-radius: 10px !important;
        border: 2px solid #333 !important;
    }
    div[data-testid="stFormSubmitButton"] button {
        font-size: 25px !important;
        height: 70px !important;
        background-color: #000000 !important;
        color: white !important;
    }
    section[data-testid="stSidebar"] { width: 300px !important; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# [데이터] 파일 저장소 (주의: 무료 서버 재부팅 시 초기화될 수 있음)
# ---------------------------------------------------------
DATA_FILE = "locus_queue.csv"

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["no", "name", "time", "status"])
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ---------------------------------------------------------
# [메뉴] 사이드바
# ---------------------------------------------------------
with st.sidebar:
    st.header("💇‍♂️ Locus Hair")
    st.info("화면 모드를 선택하세요.")
    
    mode = st.radio(
        "모드 선택", 
        ["1. 고객용 키오스크", "2. 대기 현황판 (TV용)", "3. 관리자 컨트롤러"],
        index=0
    )
    
    st.markdown("---")
    if st.button("🗑️ 데이터 초기화", type="secondary"):
        df = pd.DataFrame(columns=["no", "name", "time", "status"])
        save_data(df)
        st.success("초기화 완료!")
        time.sleep(1)
        st.rerun()

# 데이터 로드
df = load_data()

# ---------------------------------------------------------
# [탭 1] 키오스크
# ---------------------------------------------------------
if "1. 고객용" in mode:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("대기 접수")
        st.write("### 아래 칸을 터치하여 성함을 입력해주세요.")
        st.markdown("---")
        
        with st.form("register_form", clear_on_submit=True):
            name = st.text_input("성함 입력", placeholder="예: 홍길동")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("대기 접수하기 🎫", type="primary", use_container_width=True)
            
            if submit:
                if not name:
                    st.warning("성함을 입력해주세요.")
                else:
                    new_no = len(df) + 1
                    new_entry = pd.DataFrame([{
                        "no": new_no, 
                        "name": name, 
                        "time": datetime.now().strftime("%H:%M"), 
                        "status": "대기중"
                    }])
                    if df.empty: df = new_entry
                    else: df = pd.concat([df, new_entry], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ {new_no}번 접수 완료! 잠시만 기다려주세요.")
                    time.sleep(2)
                    st.rerun()

# ---------------------------------------------------------
# [탭 2] 대기 현황판 (실시간 자동 갱신)
# ---------------------------------------------------------
elif "2. 대기 현황판" in mode:
    st.header("📋 실시간 대기 현황")
    
    st.markdown("### 📢 호출 고객")
    called = df[df['status'] == "호출완료"]
    
    if not called.empty:
        c = called.iloc[-1]
        st.markdown(f"""
        <div class="status-box">
            <p class="medium-font">대기번호 {c['no']}번</p>
            <p class="big-font">{c['name']} 님</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("현재 호출된 고객이 없습니다.")
    
    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader(f"⏳ 대기 리스트 ({len(df[df['status']=='대기중'])}명)")
    waiting = df[df['status'] == "대기중"]
    
    if not waiting.empty:
        display_df = waiting[['no', 'name', 'time']].copy()
        display_df.columns = ['번호', '성함', '접수시간']
        st.table(display_df)
    else:
        st.write("대기자가 없습니다.")

    time.sleep(1)
    st.rerun()

# ---------------------------------------------------------
# [탭 3] 관리자 컨트롤러
# ---------------------------------------------------------
elif "3. 관리자" in mode:
    st.header("🔧 관리자 모드")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("대기 목록")
        waiting = df[df['status'] == "대기중"]
        if not waiting.empty:
            for i, r in waiting.iterrows():
                st.info(f"[{r['no']}번] {r['name']} ({r['time']})")
        else: st.write("대기자 없음")
        
    with col2:
        st.subheader("호출하기")
        if st.button("🔔 다음 손님 호출", type="primary", use_container_width=True):
            waiting = df[df['status'] == "대기중"]
            if not waiting.empty:
                idx = waiting.index[0]
                df.at[idx, 'status'] = "호출완료"
                save_data(df)
                st.success(f"{df.at[idx, 'name']}님 호출!")
                st.rerun()
            else: st.error("대기자가 없습니다.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("❌ 호출 화면 끄기"):
            called = df[df['status'] == "호출완료"]
            for i in called.index: df.at[i, 'status'] = "완료"
            save_data(df)
            st.success("현황판 정리 완료")
            st.rerun()
