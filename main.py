import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="2026 KBO 3D Real Baseball",
    layout="wide",
    initial_sidebar_state="collapsed",
)

html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>2026 KBO 3D Baseball</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body { background-color: #0b0e14; font-family: 'Pretendard', -apple-system, sans-serif; color: #fff; overflow: hidden; }
        #game-container { width: 100vw; height: 100vh; position: relative; }
        
        /* 팀 선택 UI */
        #team-modal { position: absolute; inset: 0; z-index: 100; background: rgba(11, 14, 20, 0.95); display: flex; flex-direction: column; justify-content: center; align-items: center; }
        .modal-card { background: #161b22; border: 1px solid #30363d; border-radius: 16px; padding: 32px; width: 480px; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.6); }
        .modal-title { font-size: 28px; font-weight: 800; color: #58a6ff; margin-bottom: 8px; }
        .modal-sub { font-size: 14px; color: #8b949e; margin-bottom: 24px; }
        select { width: 100%; padding: 12px 16px; font-size: 16px; background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 8px; margin-bottom: 20px; outline: none; }
        .start-btn { width: 100%; padding: 14px; font-size: 18px; font-weight: 700; background: #238636; color: #fff; border: none; border-radius: 8px; cursor: pointer; transition: 0.2s; }
        .start-btn:hover { background: #2ea043; }

        /* HUD 및 전광판 */
        #hud-top { position: absolute; top: 16px; left: 16px; right: 16px; z-index: 10; display: flex; justify-content: space-between; pointer-events: none; }
        .scoreboard { background: rgba(22, 27, 34, 0.85); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 12px 20px; display: flex; gap: 24px; align-items: center; }
        .score-team { text-align: center; }
        .team-name { font-size: 12px; color: #8b949e; font-weight: 600; }
        .team-score { font-size: 24px; font-weight: 800; }
        .bso-box { display: flex; gap: 12px; font-size: 14px; font-weight: 700; border-left: 1px solid #30363d; padding-left: 16px; }
        .bso-dots { display: flex; gap: 4px; align-items: center; }
        .dot { width: 10px; height: 10px; border-radius: 50%; background: #30363d; }
        .dot.b { background: #58a6ff; }
        .dot.s { background: #f85149; }
        .dot.o { background: #d29922; }

        .batter-card { background: rgba(22, 27, 34, 0.85); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 12px 20px; text-align: right; }
        .batter-order { font-size: 12px; color: #2f81f7; font-weight: 700; }
        .batter-name { font-size: 20px; font-weight: 800; }
        .batter-stats { font-size: 12px; color: #8b949e; }

        /* 타격 판정 알림 */
        #timing-feedback { position: absolute; top: 35%; left: 50%; transform: translate(-50%, -50%); z-index: 20; font-size: 42px; font-weight: 900; text-shadow: 0 4px 12px rgba(0,0,0,0.8); pointer-events: none; opacity: 0; transition: 0.1s; }
        
        /* 스윙 컨트롤러 */
        #controls { position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%); z-index: 10; display: flex; flex-direction: column; align-items: center; gap: 8px; }
        .swing-btn { padding: 16px 48px; font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #f85149, #da3633); color: #fff; border: none; border-radius: 50px; cursor: pointer; box-shadow: 0 8px 24px rgba(218, 54, 51, 0.4); transition: transform 0.1s; }
        .swing-btn:active { transform: scale(0.95); }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="game-container">
        <!-- 팀 선택 모달 -->
        <div id="team-modal">
            <div class="modal-card">
                <div class="modal-title">⚾ 2026 KBO 3D REAL</div>
                <div class="modal-sub">구단을 선택하여 경기를 시작하세요</div>
                <select id="team-select">
                    <option value="KIA">KIA 타이거즈</option>
                    <option value="DOOSAN">두산 베어스</option>
                    <option value="SAMSUNG">삼성 라이온즈</option>
                    <option value="LG">LG 트윈스</option>
                    <option value="KT">KT 위즈</option>
                    <option value="SSG">SSG 랜더스</option>
                    <option value="LOTTE">롯데 자이언츠</option>
                    <option value="HANWHA">한화 이글스</option>
                    <option value="NC">NC 다이노스</option>
                    <option value="KIWOOM">키움 히어로즈</option>
                </select>
                <button class="start-btn" onclick="initGame()">PLAY GAME</button>
            </div>
        </div>

        <!-- HUD -->
        <div id="hud-top">
            <div class="scoreboard">
                <div class="score-team">
                    <div class="team-name" id="user-team-label">USER</div>
                    <div class="team-score" id="user-score">0</div>
                </div>
                <div style="font-size: 18px; font-weight: 700; color: #484f58;">VS</div>
                <div class="score-team">
                    <div class="team-name">COM</div>
                    <div class="team-score" id="com-score">0</div>
                </div>
                <div class="bso-box">
                    <div>
                        <div style="color:#8b949e; font-size:10px;">BALL</div>
                        <div class="bso-dots" id="b-dots">
                            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
                        </div>
                    </div>
                    <div>
                        <div style="color:#8b949e; font-size:10px;">STRIKE</div>
                        <div class="bso-dots" id="s-dots">
                            <div class="dot"></div><div class="dot"></div>
                        </div>
                    </div>
                    <div>
                        <div style="color:#8b949e; font-size:10px;">OUT</div>
                        <div class="bso-dots" id="o-dots">
                            <div class="dot"></div><div class="dot"></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="batter-card">
                <div class="batter-order" id="batter-order-txt">1번 타자</div>
                <div class="batter-name" id="batter-name-txt">-</div>
                <div class="batter-stats" id="batter-stat-txt">컨택 90 | 파워 85</div>
            </div>
        </div>

        <div id="timing-feedback">PERFECT!</div>

        <!-- 컨트롤러 -->
        <div id="controls">
            <button class="swing-btn" onclick="swing()">SWING</button>
        </div>
    </div>

    <script>
        // 2026 KBO 최신 이적반영 10개 팀 라인업
        const kboData = {
            'KIA': { name: 'KIA 타이거즈', roster: [
                {n:'최원준', c:85, p:74}, {n:'소크라테스', c:85, p:86}, {n:'김도영', c:95, p:94},
                {n:'최형우', c:90, p:92}, {n:'나성범', c:86, p:90}, {n:'김선빈', c:89, p:68},
                {n:'이우성', c:82, p:80}, {n:'한준수', c:78, p:76}, {n:'변우혁', c:76, p:78}
            ]},
            'DOOSAN': { name: '두산 베어스', roster: [
                {n:'박찬호', c:88, p:70}, {n:'정수빈', c:87, p:66}, {n:'양의지', c:93, p:89},
                {n:'김재환', c:80, p:91}, {n:'양석환', c:79, p:88}, {n:'강승호', c:82, p:84},
                {n:'허경민', c:88, p:74}, {n:'전민재', c:78, p:68}, {n:'조수행', c:84, p:60}
            ]},
            'SAMSUNG': { name: '삼성 라이온즈', roster: [
                {n:'김지찬', c:88, p:65}, {n:'윤정빈', c:80, p:78}, {n:'구자욱', c:94, p:90},
                {n:'디아즈', c:83, p:92}, {n:'강민호', c:86, p:88}, {n:'김영웅', c:81, p:89},
                {n:'박병호', c:76, p:91}, {n:'류지혁', c:82, p:70}, {n:'이재현', c:80, p:82}
            ]},
            'LG': { name: 'LG 트윈스', roster: [
                {n:'홍창기', c:94, p:70}, {n:'신민재', c:86, p:62}, {n:'오스틴', c:92, p:93},
                {n:'문보경', c:88, p:85}, {n:'오지환', c:82, p:83}, {n:'김현수', c:87, p:82},
                {n:'박동원', c:80, p:86}, {n:'박해민', c:83, p:68}, {n:'구본혁', c:80, p:70}
            ]},
            'KT': { name: 'KT 위즈', roster: [
                {n:'로하스', c:90, p:93}, {n:'강백호', c:89, p:90}, {n:'장성우', c:84, p:82},
                {n:'문상철', c:81, p:85}, {n:'황재균', c:82, p:80}, {n:'김민혁', c:86, p:68},
                {n:'배정대', c:80, p:76}, {n:'오윤석', c:78, p:74}, {n:'심우준', c:79, p:65}
            ]},
            'SSG': { name: 'SSG 랜더스', roster: [
                {n:'최지훈', c:84, p:72}, {n:'박성한', c:87, p:76}, {n:'최정', c:89, p:96},
                {n:'에레디아', c:93, p:86}, {n:'한유섬', c:78, p:89}, {n:'이지영', c:82, p:68},
                {n:'고명준', c:79, p:80}, {n:'하재훈', c:76, p:82}, {n:'김성현', c:78, p:66}
            ]},
            'LOTTE': { name: '롯데 자이언츠', roster: [
                {n:'황성빈', c:86, p:60}, {n:'윤동희', c:88, p:82}, {n:'전준우', c:90, p:86},
                {n:'레이예스', c:94, p:85}, {n:'나승엽', c:85, p:81}, {n:'노진혁', c:78, p:76}, {n:'손성빈', c:75, p:74}, {n:'유강남', c:76, p:78}, {n:'박승욱', c:80, p:70}
            ]},
            'HANWHA': { name: '한화 이글스', roster: [
                {n:'최인호', c:82, p:72}, {n:'페라자', c:86, p:91}, {n:'노시환', c:84, p:93}, {n:'채은성', c:85, p:86}, {n:'안치홍', c:86, p:80}, {n:'하주석', c:78, p:72}, {n:'최재훈', c:80, p:68}, {n:'장진혁', c:80, p:74}, {n:'이도윤', c:79, p:62}
            ]},
            'NC': { name: 'NC 다이노스', roster: [
                {n:'박민우', c:92, p:68}, {n:'권희동', c:85, p:80}, {n:'박건우', c:91, p:85}, {n:'데이비드슨', c:82, p:95}, {n:'손아섭', c:89, p:76}, {n:'김휘집', c:78, p:81}, {n:'서호철', c:83, p:75}, {n:'김형준', c:75, p:80}, {n:'김주원', c:79, p:74}
            ]},
            'KIWOOM': { name: '키움 히어로즈', roster: [
                {n:'이주형', c:86, p:80}, {n:'도슨', c:89, p:84}, {n:'송성문', c:90, p:86}, {n:'최주환', c:81, p:85}, {n:'김혜성', c:92, p:78}, {n:'변상권', c:78, p:74}, {n:'김건희', c:76, p:76}, {n:'김태진', c:80, p:62}, {n:'장재영', c:72, p:80}
            ]}
        };

        let currentTeam = null;
        let batterIdx = 0;
        let balls = 0, strikes = 0, outs = 0;
        let userScore = 0;

        let scene, camera, renderer, ball, bat;
        let isPitching = false;
        let pitchProgress = 0;
        let currentPitch = { cx: 0, cy: 0, speedFactor: 0.012 }; // 구속 연산 속도 대폭 낮춤

        function initGame() {
            const teamKey = document.getElementById('team-select').value;
            currentTeam = kboData[teamKey];

            document.getElementById('user-team-label').innerText = currentTeam.name.split(' ')[0];
            document.getElementById('team-modal').style.display = 'none';

            init3D();
            updateBatterHUD();
            startPitchSequence();
        }

        function createFielder(x, z) {
            const group = new THREE.Group();
            // 몸통
            const bodyGeo = new THREE.CylinderGeometry(0.2, 0.15, 0.8);
            const bodyMat = new THREE.MeshStandardMaterial({ color: 0x1d4ed8 });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.position.y = 0.4;
            group.add(body);
            // 머리
            const headGeo = new THREE.SphereGeometry(0.15, 8, 8);
            const headMat = new THREE.MeshStandardMaterial({ color: 0xffdbac });
            const head = new THREE.Mesh(headGeo, headMat);
            head.position.y = 0.9;
            group.add(head);

            group.position.set(x, 0, z);
            scene.add(group);
        }

        function init3D() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a1118);
            scene.fog = new THREE.FogExp2(0x0a1118, 0.012);

            camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0.6, 1.4, 1.8);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.getElementById('game-container').appendChild(renderer.domElement);

            const mainLight = new THREE.DirectionalLight(0xffffff, 1.2);
            mainLight.position.set(10, 20, 10);
            scene.add(mainLight);
            scene.add(new THREE.AmbientLight(0x404854));

            // 야구장 잔디
            const fieldGeo = new THREE.PlaneGeometry(100, 100);
            const fieldMat = new THREE.MeshStandardMaterial({ color: 0x1e5631, roughness: 0.8 });
            const field = new THREE.Mesh(fieldGeo, fieldMat);
            field.rotation.x = -Math.PI / 2;
            scene.add(field);

            // 내야 흙
            const dirtGeo = new THREE.PlaneGeometry(24, 24);
            const dirtMat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b });
            const dirt = new THREE.Mesh(dirtGeo, dirtMat);
            dirt.rotation.x = -Math.PI / 2;
            dirt.rotation.z = Math.PI / 4;
            dirt.position.set(0, 0.01, -8);
            scene.add(dirt);

            // 야수(수비수) 3D 모델 배치
            createFielder(-5, -6);  // 3루수
            createFielder(-2.5, -12); // 유격수
            createFielder(2.5, -12);  // 2루수
            createFielder(5, -6);   // 1루수
            createFielder(-15, -25); // 좌익수
            createFielder(0, -30);   // 중견수
            createFielder(15, -25);  // 우익수

            // 투수
            createFielder(0, -18.4);

            // 공
            const ballGeo = new THREE.SphereGeometry(0.08, 16, 16);
            const ballMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
            ball = new THREE.Mesh(ballGeo, ballMat);
            scene.add(ball);

            // 배트
            const batGeo = new THREE.CylinderGeometry(0.035, 0.018, 0.9);
            const batMat = new THREE.MeshStandardMaterial({ color: 0xc49a45 });
            bat = new THREE.Mesh(batGeo, batMat);
            bat.position.set(0.4, 1.1, 0.2);
            bat.rotation.set(0.2, 0, 0.6);
            scene.add(bat);

            animate();
        }

        function startPitchSequence() {
            if (outs >= 3) return;

            // 랜덤 무작위 궤적 (구종 유출 금지)
            const trajectories = [
                { cx: 0, cy: 0, spd: 0.015 },
                { cx: -0.3, cy: -0.1, spd: 0.013 },
                { cx: 0.2, cy: -0.2, spd: 0.012 }
            ];
            const p = trajectories[Math.floor(Math.random() * trajectories.length)];
            currentPitch = p;

            pitchProgress = 0;
            ball.position.set(0, 1.6, -18.4);
            isPitching = true;
        }

        function animate() {
            requestAnimationFrame(animate);

            if (isPitching) {
                // 공이 보이는 속도를 크게 완화함
                pitchProgress += currentPitch.spd;
                
                ball.position.z = -18.4 + (18.6 * pitchProgress);
                ball.position.x = currentPitch.cx * Math.pow(pitchProgress, 2);
                ball.position.y = 1.6 + (currentPitch.cy * pitchProgress) - (0.1 * Math.pow(pitchProgress, 2));

                if (pitchProgress >= 1.0) {
                    isPitching = false;
                    handleTake();
                }
            }

            renderer.render(scene, camera);
        }

        function swing() {
            if (!isPitching) return;
            isPitching = false;

            bat.rotation.y = -Math.PI / 2;
            setTimeout(() => { bat.rotation.y = 0; }, 200);

            const diff = pitchProgress - 0.90;
            
            if (Math.abs(diff) < 0.04) {
                showFeedback("🔥 PERFECT!", "#f85149");
                triggerHit(Math.random() > 0.4 ? "홈런" : "2루타");
            } else if (Math.abs(diff) < 0.09) {
                showFeedback("⚾ GOOD HIT", "#58a6ff");
                triggerHit("안타");
            } else if (diff < -0.09) {
                showFeedback("EARLY (파울)", "#d29922");
                addStrike();
            } else {
                showFeedback("LATE (헛스윙)", "#8b949e");
                addStrike();
            }
        }

        function handleTake() {
            if (Math.abs(ball.position.x) < 0.35 && ball.position.y > 0.7 && ball.position.y < 1.8) {
                showFeedback("STRIKE!", "#f85149");
                addStrike();
            } else {
                showFeedback("BALL", "#58a6ff");
                balls++;
                if (balls >= 4) {
                    showFeedback("볼넷 출루!", "#2f81f7");
                    resetCount();
                    nextBatter();
                }
            }
            updateBSOHUD();
        }

        function triggerHit(type) {
            if (type === "홈런") {
                userScore += 1;
                document.getElementById('user-score').innerText = userScore;
            }
            resetCount();
            setTimeout(nextBatter, 1500);
        }

        function addStrike() {
            strikes++;
            if (strikes >= 3) {
                showFeedback("삼진 아웃!", "#f85149");
                outs++;
                resetCount();
                setTimeout(nextBatter, 1500);
            } else {
                setTimeout(startPitchSequence, 1500);
            }
            updateBSOHUD();
        }

        function resetCount() {
            balls = 0;
            strikes = 0;
            updateBSOHUD();
        }

        function nextBatter() {
            if (outs >= 3) {
                showFeedback("3아웃 공수교대", "#d29922");
                outs = 0;
                resetCount();
            }
            batterIdx = (batterIdx + 1) % currentTeam.roster.length;
            updateBatterHUD();
            setTimeout(startPitchSequence, 1000);
        }

        function updateBatterHUD() {
            const b = currentTeam.roster[batterIdx];
            document.getElementById('batter-order-txt').innerText = `${batterIdx + 1}번 타자`;
            document.getElementById('batter-name-txt').innerText = b.n;
            document.getElementById('batter-stat-txt').innerText = `컨택 ${b.c} | 파워 ${b.p}`;
        }

        function updateBSOHUD() {
            const renderDots = (containerId, count, cssClass) => {
                const dots = document.getElementById(containerId).children;
                for (let i = 0; i < dots.length; i++) {
                    dots[i].className = 'dot' + (i < count ? ' ' + cssClass : '');
                }
            };
            renderDots('b-dots', balls, 'b');
            renderDots('s-dots', strikes, 's');
            renderDots('o-dots', outs, 'o');
        }

        function showFeedback(txt, color) {
            const el = document.getElementById('timing-feedback');
            el.innerText = txt;
            el.style.color = color;
            el.style.opacity = '1';
            setTimeout(() => { el.style.opacity = '0'; }, 1000);
        }

        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space') swing();
        });
    </script>
</body>
</html>
"""

components.html(html_code, height=800, scrolling=False)
