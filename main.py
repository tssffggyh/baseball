import random
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.set_page_config(page_title="컴프야 V26 라이트", layout="wide")


# --- 게임 데이터 초기화 ---
def init_game():
    st.session_state.game = {
        "inning": 1,
        "is_top": True,  # True: 초(공격), False: 말(수비)
        "score": {"USER": 0, "COM": 0},
        "outs": 0,
        "balls": 0,
        "strikes": 0,
        "bases": [False, False, False],  # 1루, 2루, 3루
        "log": [],
        "last_pitch_pos": None,
        "last_pitch_type": "",
        "last_result": "",
    }


if "game" not in st.session_state:
    init_game()

game = st.session_state.game

# --- 선수 능력치 설정 ---
pitcher_stats = {
    "name": "안우진 (ACE)",
    "stuff": 88,  # 구위
    "control": 82,  # 제구
    "pitches": {
        "직구": {"speed": 155, "power": 88},
        "슬라이더": {"speed": 142, "power": 85},
        "체인지업": {"speed": 135, "power": 78},
        "커브": {"speed": 128, "power": 80},
    },
}

batter_stats = {
    "name": "이정후 (MVP)",
    "contact": 92,  # 컨택
    "power": 85,  # 파워
    "eye": 89,  # 선구안
}

# --- 스트라이크 존 시각화 함수 ---
def draw_strike_zone(pitch_pos=None, is_strike=False):
    fig, ax = plt.subplots(figsize=(3, 3))
    # 스트라이크 존 경계 설정
    ax.plot([-1, 1, 1, -1, -1], [-1, -1, 1, 1, -1], "k-", lw=2)

    if pitch_pos:
        x, y = pitch_pos
        color = "red" if is_strike else "blue"
        ax.scatter(x, y, color=color, s=250, zorder=5)
        ax.text(
            x,
            y,
            "⚾",
            fontsize=12,
            ha="center",
            va="center",
            color="white",
            fontweight="bold",
        )

    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.axis("off")
    return fig


# --- 주자 및 이닝 리셋 ---
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


# --- 투구 및 타격 로직 ---
def process_pitch(swing_action, target_zone):
    pitch_type = random.choice(list(pitcher_stats["pitches"].keys()))
    # 제구력에 따른 공 위치 변동
    err = (100 - pitcher_stats["control"]) / 50
    pitch_x = np.clip(random.uniform(-0.8, 0.8) + random.uniform(-err, err), -1.8, 1.8)
    pitch_y = np.clip(random.uniform(-0.8, 0.8) + random.uniform(-err, err), -1.8, 1.8)

    is_strike = (-1.0 <= pitch_x <= 1.0) and (-1.0 <= pitch_y <= 1.0)
    game["last_pitch_pos"] = (pitch_x, pitch_y)
    game["last_pitch_type"] = pitch_type

    # 결과 판정
    if swing_action == "지켜보기":
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
        # 타격 타이밍 및 존 일치 여부 계산
        contact_prob = (batter_stats["contact"] / 100) * 0.7
        if is_strike:
            contact_prob += 0.2

        if random.random() < contact_prob:
            # 타격 성공 -> 안타/파울/아웃 판정
            power_roll = random.randint(1, 100) + (
                batter_stats["power"] - pitcher_stats["stuff"]
            )
            if power_roll > 85:
                res = "🚨 대형 홈런!!"
                runs = advance_runners("홈런")
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

    # 아웃 카운트 처리
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


# --- UI 레이아웃 ---
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

# 메인 게임 화면
col_left, col_center, col_right = st.columns([3, 3, 3])

with col_left:
    st.subheader("👤 매치업 정보")
    st.info(
        f"**투수:** {pitcher_stats['name']}\n\n- 구위: {pitcher_stats['stuff']} | 제구: {pitcher_stats['control']}"
    )
    st.success(
        f"**타자:** {batter_stats['name']}\n\n- 컨택: {batter_stats['contact']} | 파워: {batter_stats['power']} | 선구: {batter_stats['eye']}"
    )

with col_center:
    st.subheader("🎯 스트라이크 존 (Pitch Zone)")
    if game["last_pitch_pos"]:
        is_str = (
            "스트라이크" in game["last_result"]
            or "안타" in game["last_result"]
            or "홈런" in game["last_result"]
        )
        fig = draw_strike_zone(game["last_pitch_pos"], is_str)
        st.pyplot(fig)
    else:
        fig = draw_strike_zone()
        st.pyplot(fig)

with col_right:
    st.subheader("🎮 타격 컨트롤러")
    swing = st.radio("타격 방식 선택", ["강타 (Power)", "일반 타격 (Contact)", "지켜보기 (Take)"])

    if st.button("⚾ 공 타격 / 투구 진행", use_container_width=True):
        process_pitch(swing, None)
        st.rerun()

    if game["last_result"]:
        st.subheader("최근 결과")
        st.warning(f"구종: {game['last_pitch_type']} ➡️ 결과: {game['last_result']}")

# 중계 로그
st.divider()
st.subheader("📜 경기 중계 로그")
for log_item in game["log"][:8]:
    st.text(log_item)
