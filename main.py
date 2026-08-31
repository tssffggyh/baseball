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
        
        #team-modal { position: absolute; inset: 0; z-index: 100; background: rgba(11, 14, 20, 0.95); display: flex; flex-direction: column; justify-content: center; align-items: center; }
        .modal-card { background: #161b22; border: 1px solid #30363d; border-radius: 16px; padding: 32px; width: 480px; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.6); }
        .modal-title { font-size: 28px; font-weight: 800; color: #58a6ff; margin-bottom: 8px; }
        .modal-sub { font-size: 14px; color: #8b949e; margin-bottom: 24px; }
        select { width: 100%; padding: 12px 16px; font-size: 16px; background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 8px; margin-bottom: 20px; outline: none; }
        .start-btn { width: 100%; padding: 14px; font-size: 18px; font-weight: 700; background: #238636; color: #fff; border: none; border-radius: 8px; cursor: pointer; transition: 0.2s; }
        .start-btn:hover { background: #2ea043; }

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

        #timing-feedback { position: absolute; top: 25%; left: 50%; transform: translate(-50%, -50%); z-index: 20; font-size: 42px; font-weight: 900; text-shadow: 0 4px 12px rgba(0,0,0,0.8); pointer-events: none; opacity: 0; transition: 0.1s; }
        
        #controls { position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%); z-index: 10; display: flex; flex-direction: column; align-items: center; gap: 8px; }
        .swing-btn { padding: 16px 48px; font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #f85149, #da3633); color: #fff; border: none; border-radius: 50px; cursor: pointer; box-shadow: 0 8px 24px rgba(218, 54, 51, 0.4); transition: transform 0.1s; }
        .swing-btn:active { transform: scale(0.95); }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="game-container">
        <div id="team-modal">
            <div class="modal-card">
                <div class="modal-title">⚾ 2026 KBO 3D REAL</div>
                <div class="modal-sub">구단을 선택하여 경기를 시작하세요</div>
                <select id="team-select">
                    <option value="DOOSAN">두산 베어스 (박찬호)</option>
                    <option value="KIA">KIA 타이거즈 (김도영)</option>
                    <option value="SAMSUNG">삼성 라이온즈 (구자욱)</option>
                    <option value="LG">LG 트윈스 (오스틴)</option>
                    <option value="KT">KT 위즈 (강백호)</option>
                    <option value="SSG">SSG 랜더스 (최정)</option>
                    <option value="LOTTE">롯데 자이언츠 (레이예스)</option>
                    <option value="HANWHA">한화 이글스 (노시환)</option>
                    <option value="NC">NC 다이노스 (박건우)</option>
                    <option value="KIWOOM">키움 히어로즈 (송성문)</option>
                </select>
                <button class="start-btn" onclick="initGame()">PLAY GAME</button>
            </div>
        </div>

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

        <div id="controls">
            <button class="swing-btn" onclick="swing()">SWING</button>
        </div>
    </div>

    <script>
        const kboData = {
            'DOOSAN': { name: '두산 베어스', roster: [{n:'박찬호', c:88, p:70}, {n:'정수빈', c:87, p:66}, {n:'양의지', c:93, p:89}, {n:'김재환', c:80, p:91}, {n:'양석환', c:79, p:88}] },
            'KIA': { name: 'KIA 타이거즈', roster: [{n:'최원준', c:85, p:74}, {n:'소크라테스', c:85, p:86}, {n:'김도영', c:95, p:94}, {n:'최형우', c:90, p:92}, {n:'나성범', c:86, p:90}] },
            'SAMSUNG': { name: '삼성 라이온즈', roster: [{n:'김지찬', c:88, p:65}, {n:'윤정빈', c:80, p:78}, {n:'구자욱', c:94, p:90}, {n:'디아즈', c:83, p:92}, {n:'강민호', c:86, p:88}] },
            'LG': { name: 'LG 트윈스', roster: [{n:'홍창기', c:94, p:70}, {n:'신민재', c:86, p:62}, {n:'오스틴', c:92, p:93}, {n:'문보경', c:88, p:85}, {n:'오지환', c:82, p:83}] },
            'KT': { name: 'KT 위즈', roster: [{n:'로하스', c:90, p:93}, {n:'강백호', c:89, p:90}, {n:'장성우', c:84, p:82}, {n:'문상철', c:81, p:85}, {n:'황재균', c:82, p:80}] },
            'SSG': { name: 'SSG 랜더스', roster: [{n:'최지훈', c:84, p:72}, {n:'박성한', c:87, p:76}, {n:'최정', c:89, p:96}, {n:'에레디아', c:93, p:86}, {n:'한유섬', c:78, p:89}] },
            'LOTTE': { name: '롯데 자이언츠', roster: [{n:'황성빈', c:86, p:60}, {n:'윤동희', c:88, p:82}, {n:'전준우', c:90, p:86}, {n:'레이예스', c:94, p:85}, {n:'나승엽', c:85, p:81}] },
            'HANWHA': { name: '한화 이글스', roster: [{n:'최인호', c:82, p:72}, {n:'페라자', c:86, p:91}, {n:'노시환', c:84, p:93}, {n:'채은성', c:85, p:86}, {n:'안치홍', c:86, p:80}] },
            'NC': { name: 'NC 다이노스', roster: [{n:'박민우', c:92, p:68}, {n:'권희동', c:85, p:80}, {n:'박건우', c:91, p:85}, {n:'데이비드슨', c:82, p:95}, {n:'손아섭', c:89, p:76}] },
            'KIWOOM': { name: '키움 히어로즈', roster: [{n:'이주형', c:86, p:80}, {n:'도슨', c:89, p:84}, {n:'송성문', c:90, p:86}, {n:'최주환', c:81, p:85}, {n:'김혜성', c:92, p:78}] }
        };

        let currentTeam = null;
        let batterIdx = 0;
        let balls = 0, strikes = 0, outs = 0;
        let userScore = 0;

        let scene, camera, renderer, ball, bat;
        let fielders = [];
        let pitcherMesh = null;
        let isPitching = false;
        let isHitInFlight = false;
        let pitchProgress = 0;
        let currentPitch = { cx: 0, cy: 0, spd: 0.012 };

        const defaultCamPos = new THREE.Vector3(0, 1.8, 2.8);
        const defaultCamLook = new THREE.Vector3(0, 1.2, -22);

        let hitFlightProgress = 0;
        let flightSpeed = 0.0035;
        let hitStartPos = new THREE.Vector3();
        let hitTargetPos = new THREE.Vector3();
        let hitMaxHeight = 0;
        let currentResultType = "";
        let assignedFielder = null;
        let isDiving = false;

        const STADIUM_CENTER_Z = -15;
        const OUTFIELD_WALL_RADIUS = 78; // 야수 통과 방지 경계선 반경

        function initGame() {
            const teamKey = document.getElementById('team-select').value;
            currentTeam = kboData[teamKey];
            document.getElementById('user-team-label').innerText = currentTeam.name.split(' ')[0];
            document.getElementById('team-modal').style.display = 'none';

            init3D();
            updateBatterHUD();
            startPitchSequence();
        }

        function createHumanoidModel(x, y, z, colorHex) {
            const character = new THREE.Group();
            const mat = new THREE.MeshStandardMaterial({ color: colorHex });
            const skinMat = new THREE.MeshStandardMaterial({ color: 0xffdbac });

            const torsoGeo = new THREE.BoxGeometry(0.5, 0.75, 0.3);
            const torso = new THREE.Mesh(torsoGeo, mat);
            torso.position.y = 1.0;
            character.add(torso);

            const headGeo = new THREE.SphereGeometry(0.2, 12, 12);
            const head = new THREE.Mesh(headGeo, skinMat);
            head.position.y = 1.55;
            character.add(head);

            const armGeo = new THREE.CylinderGeometry(0.07, 0.06, 0.65);
            const leftArmGroup = new THREE.Group();
            leftArmGroup.position.set(-0.35, 1.3, 0);
            const leftArm = new THREE.Mesh(armGeo, mat);
            leftArm.position.y = -0.3;
            leftArmGroup.add(leftArm);
            character.add(leftArmGroup);

            const rightArmGroup = new THREE.Group();
            rightArmGroup.position.set(0.35, 1.3, 0);
            const rightArm = new THREE.Mesh(armGeo, mat);
            rightArm.position.y = -0.3;
            rightArmGroup.add(rightArm);
            character.add(rightArmGroup);

            const legGeo = new THREE.CylinderGeometry(0.09, 0.07, 0.75);
            const leftLegGroup = new THREE.Group();
            leftLegGroup.position.set(-0.16, 0.6, 0);
            const leftLeg = new THREE.Mesh(legGeo, mat);
            leftLeg.position.y = -0.35;
            leftLegGroup.add(leftLeg);
            character.add(leftLegGroup);

            const rightLegGroup = new THREE.Group();
            rightLegGroup.position.set(0.16, 0.6, 0);
            const rightLeg = new THREE.Mesh(legGeo, mat);
            rightLeg.position.y = -0.35;
            rightLegGroup.add(rightLeg);
            character.add(rightLegGroup);

            character.position.set(x, y, z);
            character.userData = { 
                originX: x, originY: y, originZ: z, 
                rightArmGroup, leftArmGroup, leftLegGroup, rightLegGroup, torso
            };

            scene.add(character);
            return character;
        }

        function createStrikeZone9Grid() {
            const zoneGroup = new THREE.Group();
            const width = 0.6;
            const height = 0.8;
            const subW = width / 3;
            const subH = height / 3;

            for (let r = 0; r < 3; r++) {
                for (let c = 0; c < 3; c++) {
                    const gridGeo = new THREE.PlaneGeometry(subW * 0.95, subH * 0.95);
                    const gridMat = new THREE.MeshBasicMaterial({ 
                        color: (r === 1 && c === 1) ? 0xff4d4d : 0x58a6ff, 
                        wireframe: true, 
                        transparent: true, 
                        opacity: 0.18
                    });
                    const cell = new THREE.Mesh(gridGeo, gridMat);
                    cell.position.set(-subW + (c * subW), -subH + (r * subH), 0);
                    zoneGroup.add(cell);
                }
            }
            zoneGroup.position.set(0, 1.2, 0);
            scene.add(zoneGroup);
        }

        function createStadiumEnvironment() {
            const fieldGeo = new THREE.PlaneGeometry(260, 260);
            const fieldMat = new THREE.MeshStandardMaterial({ color: 0x1e5631, roughness: 0.8 });
            const field = new THREE.Mesh(fieldGeo, fieldMat);
            field.rotation.x = -Math.PI / 2;
            scene.add(field);

            const dirtGeo = new THREE.PlaneGeometry(45, 45);
            const dirtMat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b });
            const dirt = new THREE.Mesh(dirtGeo, dirtMat);
            dirt.rotation.x = -Math.PI / 2;
            dirt.rotation.z = Math.PI / 4;
            dirt.position.set(0, 0.01, -15);
            scene.add(dirt);

            const moundGeo = new THREE.CylinderGeometry(3.5, 4.5, 0.4, 32);
            const moundMat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b });
            const mound = new THREE.Mesh(moundGeo, moundMat);
            mound.position.set(0, 0.2, -18.4);
            scene.add(mound);

            const colors = [0xe74c3c, 0x3498db, 0xf1c40f, 0xecf0f1, 0x9b59b6, 0x1abc9c];
            for (let i = 0; i < 8; i++) {
                const radius = 80 + i * 2.5;
                const standGeo = new THREE.CylinderGeometry(radius, radius, 1.5, 48, 1, true, Math.PI * 0.15, Math.PI * 0.7);
                const standMat = new THREE.MeshStandardMaterial({ color: 0x22272e, side: THREE.DoubleSide });
                const stand = new THREE.Mesh(standGeo, standMat);
                stand.position.set(0, 1 + i * 1.5, STADIUM_CENTER_Z);
                scene.add(stand);

                for (let j = 0; j < 60; j++) {
                    const angle = Math.PI * 0.18 + (j / 60) * (Math.PI * 0.64);
                    const spectatorGeo = new THREE.BoxGeometry(0.6, 0.8, 0.6);
                    const spectatorMat = new THREE.MeshBasicMaterial({ color: colors[Math.floor(Math.random() * colors.length)] });
                    const spectator = new THREE.Mesh(spectatorGeo, spectatorMat);
                    spectator.position.set(
                        Math.cos(angle) * radius,
                        2.0 + i * 1.5,
                        Math.sin(angle) * radius + STADIUM_CENTER_Z
                    );
                    scene.add(spectator);
                }
            }
        }

        function resetFielderPositions() {
            fielders.forEach(f => {
                f.position.set(f.userData.originX, f.userData.originY, f.userData.originZ);
                f.rotation.set(0, 0, 0);
                f.userData.leftArmGroup.rotation.set(0, 0, 0);
                f.userData.rightArmGroup.rotation.set(0, 0, 0);
                f.userData.leftLegGroup.rotation.set(0, 0, 0);
                f.userData.rightLegGroup.rotation.set(0, 0, 0);
            });
            assignedFielder = null;
            isDiving = false;
        }

        function resetCamera() {
            camera.position.copy(defaultCamPos);
            camera.lookAt(defaultCamLook);
        }

        function init3D() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a1118);
            scene.fog = new THREE.FogExp2(0x0a1118, 0.004);

            camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
            resetCamera();

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.getElementById('game-container').appendChild(renderer.domElement);

            const mainLight = new THREE.DirectionalLight(0xffffff, 1.2);
            mainLight.position.set(20, 40, 20);
            scene.add(mainLight);
            scene.add(new THREE.AmbientLight(0x505864));

            createStrikeZone9Grid();
            createStadiumEnvironment();

            fielders.push(createHumanoidModel(-12, 0, -12, 0x1d4ed8));  // 3루수
            fielders.push(createHumanoidModel(-8, 0, -26, 0x1d4ed8));   // 유격수
            fielders.push(createHumanoidModel(8, 0, -26, 0x1d4ed8));    // 2루수
            fielders.push(createHumanoidModel(12, 0, -12, 0x1d4ed8));   // 1루수
            fielders.push(createHumanoidModel(-38, 0, -50, 0x1d4ed8));  // 좌익수
            fielders.push(createHumanoidModel(0, 0, -65, 0x1d4ed8));    // 중견수
            fielders.push(createHumanoidModel(38, 0, -50, 0x1d4ed8));   // 우익수

            pitcherMesh = createHumanoidModel(0, 0.4, -18.4, 0xda3633);

            const ballGeo = new THREE.SphereGeometry(0.08, 16, 16);
            const ballMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
            ball = new THREE.Mesh(ballGeo, ballMat);
            scene.add(ball);

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

            resetFielderPositions();
            resetCamera();
            isHitInFlight = false;

            const trajectories = [
                { cx: 0, cy: -0.05, spd: 0.010 },
                { cx: -0.15, cy: -0.1, spd: 0.009 },
                { cx: 0.15, cy: -0.1, spd: 0.009 }
            ];
            currentPitch = trajectories[Math.floor(Math.random() * trajectories.length)];

            pitchProgress = 0;
            ball.position.set(0, 1.7, -18.4);
            isPitching = true;
        }

        function animate() {
            requestAnimationFrame(animate);

            if (isPitching) {
                pitchProgress += currentPitch.spd;
                
                if (pitcherMesh && pitcherMesh.userData.rightArmGroup) {
                    pitcherMesh.userData.rightArmGroup.rotation.x = -Math.sin(pitchProgress * Math.PI) * 2.5;
                }

                ball.position.z = -18.4 + (18.4 * pitchProgress);
                ball.position.x = currentPitch.cx * Math.pow(pitchProgress, 1.5);
                ball.position.y = 1.7 + (currentPitch.cy * pitchProgress) - (0.05 * Math.pow(pitchProgress, 2));

                if (pitchProgress >= 1.0) {
                    isPitching = false;
                    handleTake();
                }
            }

            if (isHitInFlight) {
                hitFlightProgress += flightSpeed;

                ball.position.x = THREE.MathUtils.lerp(hitStartPos.x, hitTargetPos.x, hitFlightProgress);
                ball.position.z = THREE.MathUtils.lerp(hitStartPos.z, hitTargetPos.z, hitFlightProgress);

                if (currentResultType === "GROUND") {
                    ball.position.y = Math.max(0.08, Math.abs(Math.sin(hitFlightProgress * Math.PI * 4)) * (1.2 * (1 - hitFlightProgress)));
                } else {
                    ball.position.y = Math.max(0.08, hitStartPos.y + Math.sin(hitFlightProgress * Math.PI) * hitMaxHeight);
                }

                camera.position.x = THREE.MathUtils.lerp(camera.position.x, ball.position.x * 0.3, 0.04);
                camera.position.y = THREE.MathUtils.lerp(camera.position.y, ball.position.y + 12, 0.04);
                camera.position.z = THREE.MathUtils.lerp(camera.position.z, ball.position.z + 20, 0.04);
                camera.lookAt(ball.position);

                if (assignedFielder) {
                    const runProgress = Math.min(1.0, hitFlightProgress * 0.85);
                    
                    let targetX = THREE.MathUtils.lerp(assignedFielder.userData.originX, hitTargetPos.x, runProgress);
                    let targetZ = THREE.MathUtils.lerp(assignedFielder.userData.originZ, hitTargetPos.z, runProgress);

                    // 야수가 외야 관중석 경계선을 넘지 못하도록 충돌 제어 (펜스 관통 차단)
                    const distFromCenter = Math.hypot(targetX, targetZ - STADIUM_CENTER_Z);
                    if (distFromCenter > OUTFIELD_WALL_RADIUS) {
                        const angle = Math.atan2(targetZ - STADIUM_CENTER_Z, targetX);
                        targetX = Math.cos(angle) * OUTFIELD_WALL_RADIUS;
                        targetZ = Math.sin(angle) * OUTFIELD_WALL_RADIUS + STADIUM_CENTER_Z;
                    }

                    assignedFielder.position.x = targetX;
                    assignedFielder.position.z = targetZ;

                    const runLegAngle = Math.sin(hitFlightProgress * 25) * 0.7;
                    assignedFielder.userData.leftLegGroup.rotation.x = runLegAngle;
                    assignedFielder.userData.rightLegGroup.rotation.x = -runLegAngle;
                    assignedFielder.userData.leftArmGroup.rotation.x = -runLegAngle;
                    assignedFielder.userData.rightArmGroup.rotation.x = runLegAngle;

                    if (isDiving && runProgress > 0.5 && runProgress < 0.9) {
                        assignedFielder.rotation.x = -Math.PI / 2.5;
                        assignedFielder.position.y = 0.3;
                    } else if (runProgress >= 0.9) {
                        assignedFielder.rotation.x = 0;
                        assignedFielder.position.y = 0;
                        assignedFielder.userData.leftArmGroup.rotation.x = -Math.PI / 1.8;
                        assignedFielder.userData.rightArmGroup.rotation.x = -Math.PI / 1.8;
                    }
                }

                if (hitFlightProgress >= 1.0) {
                    isHitInFlight = false;
                    finishHitEvent();
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
            let timingType = "";

            if (Math.abs(diff) < 0.03) timingType = "PERFECT";
            else if (Math.abs(diff) < 0.07) timingType = diff < 0 ? "SLIGHT_EARLY" : "SLIGHT_LATE";
            else if (Math.abs(diff) < 0.11) timingType = diff < 0 ? "EARLY" : "LATE";
            else timingType = "MISS";

            processHitOutcome(timingType);
        }

        function processHitOutcome(timing) {
            const rand = Math.random() * 100;
            let result = "";

            if (timing === "PERFECT") {
                showFeedback("🔥 PERFECT!", "#f85149");
                if (rand < 35) result = "HOMERUN";
                else if (rand < 65) result = "HIT";
                else if (rand < 85) result = "GROUND";
                else result = "FLY";
            } else if (timing === "SLIGHT_EARLY" || timing === "SLIGHT_LATE") {
                showFeedback(timing === "SLIGHT_EARLY" ? "⚡ SLIGHT EARLY" : "⏳ SLIGHT LATE", "#58a6ff");
                if (rand < 15) result = "HOMERUN";
                else if (rand < 45) result = "HIT";
                else if (rand < 75) result = "GROUND";
                else if (rand < 90) result = "FLY";
                else result = "FOUL";
            } else if (timing === "EARLY" || timing === "LATE") {
                showFeedback(timing === "EARLY" ? "EARLY (파울)" : "LATE (파울)", "#d29922");
                if (rand < 60) result = "FOUL";
                else result = "GROUND";
            } else {
                showFeedback("LATE (헛스윙)", "#8b949e");
                addStrike();
                return;
            }

            launchBall(result);
        }

        function launchBall(result) {
            currentResultType = result;
            hitFlightProgress = 0;
            hitStartPos.copy(ball.position);

            if (result === "HOMERUN") {
                flightSpeed = 0.0035;
                hitTargetPos.set((Math.random() - 0.5) * 60, 0, -95);
                hitMaxHeight = 35;
            } else if (result === "HIT") {
                flightSpeed = 0.004;
                hitTargetPos.set((Math.random() - 0.5) * 55, 0, -48);
                hitMaxHeight = 12;
            } else if (result === "GROUND") {
                flightSpeed = 0.0045;
                hitTargetPos.set((Math.random() - 0.5) * 40, 0, -28);
                hitMaxHeight = 0.5;
            } else if (result === "FLY") {
                flightSpeed = 0.0035;
                hitTargetPos.set((Math.random() - 0.5) * 30, 0, -32);
                hitMaxHeight = 25;
            } else if (result === "FOUL") {
                flightSpeed = 0.005;
                hitTargetPos.set(Math.random() > 0.5 ? 45 : -45, 0, -10);
                hitMaxHeight = 15;
            }

            let minDistance = Infinity;
            fielders.forEach(f => {
                const d = f.position.distanceTo(hitTargetPos);
                if (d < minDistance) {
                    minDistance = d;
                    assignedFielder = f;
                }
            });

            isDiving = (minDistance > 18 && minDistance < 30 && result !== "HOMERUN");
            isHitInFlight = true;
        }

        function finishHitEvent() {
            let catchDistance = Infinity;
            if (assignedFielder) {
                catchDistance = assignedFielder.position.distanceTo(hitTargetPos);
            }

            if (currentResultType === "HOMERUN") {
                showFeedback("🚨 대형 홈런 (HOME RUN)!!", "#f85149");
                userScore += 1;
                document.getElementById('user-score').innerText = userScore;
                resetCount();
                setTimeout(nextBatter, 2500);
            } else if (currentResultType === "FOUL") {
                showFeedback("FOUL (파울)", "#8b949e");
                if (strikes < 2) strikes++;
                updateBSOHUD();
                setTimeout(startPitchSequence, 1500);
            } else {
                if (catchDistance <= 3.0) {
                    showFeedback(currentResultType === "GROUND" ? "OUT (땅볼 포구 아웃)" : "OUT (야수 포구 아웃)", "#d29922");
                    outs++;
                    resetCount();
                    updateBSOHUD();
                    setTimeout(nextBatter, 2500);
                } else {
                    showFeedback("⚾ 안타 성공 (HIT)!", "#58a6ff");
                    resetCount();
                    setTimeout(nextBatter, 2500);
                }
            }
        }

        function handleTake() {
            if (Math.abs(ball.position.x) < 0.3 && ball.position.y > 0.8 && ball.position.y < 1.6) {
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
