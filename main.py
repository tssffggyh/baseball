import random
import streamlit as st

st.set_page_config(page_title="컴프야 V26 라이트", layout="wide")


# --- 게임 데이터 초기화 ---
def init_game():
    st.session_state.game = {
        "inning": 1,
        "score": {"USER": 0, "COM": 0},
        "outs": 0,
        "balls": 0,
        "strikes": 0,
        "bases": [False, False, False],
        "log": [],
        "last_pitch_pos": None,  # (row, col) 형태로 3x3 격자 저장
        "last_pitch_type": "",
        "last_result": "",
    }


if "game" not in st.session_state:
    init_game()

game = st.session_state.game

# --- 선수 능력치 ---
pitcher_stats = {
    "name": "안우진 (ACE)",
    "stuff": 88,
    "control": 82,
    "pitches": ["직구", "슬라이더", "체인지업", "커브"],
}

batter_stats = {
    "name": "이정후 (MVP)",
    "contact": 92,
    "power": 85,
    "eye": 89,
}


# --- 주자 계산 및 이닝 리셋 ---
def reset_at_bat():
    game["balls"] = 0
    game["strikes"] = 0


def advance_runners(hit_type):
    score = 0
    b = game["bases"]

    if hit_type == "안타":
        if b[2]:
            score += 1
        game["bases"] = [True, b[0], b[1]]
    elif hit_type == "2루타":
        if b[2]:
            score += 1
        if b[1]:
            score += 1
        game["bases"] = [False, True, b[0]]
    elif hit_type == "3루타":
        score += sum(b)
        game["bases"] = [False, False, True]
    elif hit_type == "홈런":
        score += sum(b) + 1
        game["bases"] = [False, False, False]
    elif hit_type == "볼넷":
        if b[0] and b[1] and b[2]:
            score += 1
        elif b[0] and b[1]:
            game["bases"][2] = True
        elif b[0]:
            game["bases"][1] = True
        game["bases"][0] = True

    game["score"]["USER"] += score
    return score


# --- 투구 처리 로직 ---
def process_pitch(swing_action):
    pitch_type = random.choice(pitcher_stats["pitches"])

    # 3x3 격자 기반 투구 (0: 스트라이크 존 내부, 1: 볼 존)
    # 제구력에 따라 스트라이크 존에 들어올 확률 결정
    is_strike = random.random() < (pitcher_stats["control"] / 100)

    row = random.randint(0, 2)
    col = random.randint(0, 2)
    game["last_pitch_pos"] = (row, col)
    game["last_pitch_type"] = pitch_type

    if swing_action == "지켜보기 (Take)":
        if is_strike:
            game["strikes"] += 1
            res = "스트라이크!"
            if game["strikes"] >= 3:
                res = "삼진 아웃!"
                game["outs"] += 1
                reset_at_bat()
        else:
            game["balls"] += 1
            res = "볼!"
            if game["balls"] >= 4:
                res = "볼넷 (1루 출루)"
                advance_runners("볼넷")
                reset_at_bat()
    else:  # 스윙
        contact_prob = (batter_stats["contact"] / 100) * (0.8 if is_strike else 0.4)

        if random.random() < contact_prob:
            power_roll = random.randint(1, 100) + (
                batter_stats["power"] - pitcher_stats["stuff"]
            )
            if power_roll > 85:
                res = "🚨 대형 홈런!!"
                advance_runners("홈런")
                reset_at_bat()
            elif power_roll > 65:
                res = "🔥 2루타!"
                advance_runners("2루타")
                reset_at_bat()
            elif power_roll > 35:
                res = "⚾ 안타!"
                advance_runners("안타")
                reset_at_bat()
            elif power_roll > 20:
                res = "파울"
                if game["strikes"] < 2:
                    game["strikes"] += 1
            else:
                res = "플라이 아웃"
                game["outs"] += 1
                reset_at_bat()
        else:
            game["strikes"] += 1
            res = "헛스윙!"
            if game["strikes"] >= 3:
                res = "삼진 아웃!"
                game["outs"] += 1
                reset_at_bat()

    if game["outs"] >= 3:
        game["log"].append(f"--- {game['inning']}이닝 종료 ---")
        game["inning"] += 1
        game["outs"] = 0
        game["bases"] = [False, False, False]
        reset_at_bat()

    game["last_result"] = res
    game["log"].insert(
        0, f"[{pitch_type}] {res} (볼카운트: {game['balls']}B {game['strikes']}S)"
    )


# --- UI 구성 ---
st.title("⚾ COMP2US PRO BASEBALL V26 - Streamlit Edition")

# 스코어보드
col_score1, col_score2, col_score3 = st.columns([2, 2, 2])
with col_score1:
    st.metric(
        label="이닝 / 점수",
        value=f"{game['inning']}회초 | USER {game['score']['USER']} : {game['score']['COM']} COM",
    )
with col_score2:
    st.write(
        f"**B:** {'🟡'*game['balls']}{'⚪'*(3-game['balls'])} | "
        f"**S:** {'🔴'*game['strikes']}{'⚪'*(2-game['strikes'])} | "
        f"**O:** {'🔴'*game['outs']}{'⚪'*(2-game['outs'])}"
    )
    bases_str = f"1루: {'🟢' if game['bases'][0] else '⚪'} | 2루: {'🟢' if game['bases'][1] else '⚪'} | 3루: {'🟢' if game['bases'][2] else '⚪'}"
    st.write(f"**주자:** {bases_str}")
with col_score3:
    if st.button("게임 리셋"):
        init_game()
        st.rerun()

st.divider()

col_left, col_center, col_right = st.columns([3, 3, 3])

with col_left:
    st.subheader("👤 매치업 정보")
    st.info(
        f"**투수:** {pitcher_stats['name']}\n\n- 구위: {pitcher_stats['stuff']} | 제구: {pitcher_stats['control']}"
    )
    st.success(
        f"**타자:** {batter_stats['name']}\n\n- 컨택: {batter_stats['contact']} | 파워: {batter_stats['power']} | 선구: {batter_stats['eye']}"
    )

# Matplotlib 대신 Streamlit 컬럼으로 스트라이크 존 시각화
with col_center:
    st.subheader("🎯 스트라이크 존")
    zone_matrix = [["⬜" for _ in range(3)] for _ in range(3)]

    if game["last_pitch_pos"]:
        r, c = game["last_pitch_pos"]
        zone_matrix[r][c] = "⚾"

    for row in zone_matrix:
        st.markdown(
            f"### &nbsp;&nbsp;&nbsp;&nbsp; {row[0]} &nbsp; {row[1]} &nbsp; {row[2]}"
        )

with col_right:
    st.subheader("🎮 타격 컨트롤러")
    swing = st.radio("타격 방식 선택", ["강타 (Power)", "일반 타격 (Contact)", "지켜보기 (Take)"])

    if st.button("⚾ 공 타격 / 투구 진행", use_container_width=True):
        process_pitch(swing)
        st.rerun()

    if game["last_result"]:
        st.subheader("최근 결과")
        st.warning(f"구종: {game['last_pitch_type']} ➡️ 결과: {game['last_result']}")

st.divider()
st.subheader("📜 경기 중계 로그")
for log_item in game["log"][:8]:
    st.text(log_item)
