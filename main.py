<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>고죠 사토루 풀 영창 자폭 & 100종 보스 레이드 시스템</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: #080810;
            color: #fff;
            font-family: 'Pretendard', 'Segoe UI', sans-serif;
            overflow: hidden;
            user-select: none;
        }

        #game-container {
            position: relative;
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
        }

        canvas {
            position: absolute;
            top: 0;
            left: 0;
            z-index: 1;
        }

        #ui-layer {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 10;
            pointer-events: none;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            padding: 24px;
        }

        /* 보스 UI 정보창 */
        .boss-info {
            background: rgba(15, 15, 25, 0.75);
            padding: 18px 32px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(8px);
            text-align: center;
            min-width: 360px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        }

        .boss-name {
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 10px;
            color: #ff4757;
            text-shadow: 0 0 12px rgba(255, 71, 87, 0.6);
            letter-spacing: 0.5px;
        }

        .hp-bar-container {
            width: 100%;
            height: 20px;
            background: #1e1e2d;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.15);
            position: relative;
        }

        .hp-bar {
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #ff4757, #ff6b81);
            transition: width 0.15s ease-out;
        }

        .hp-text {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.5px;
            text-shadow: 1px 1px 3px #000;
        }

        /* 컨트롤 버튼 */
        .controls {
            margin-bottom: 24px;
            pointer-events: auto;
        }

        .btn-self-destruct {
            background: linear-gradient(135deg, #a55eea, #4b7bec);
            color: white;
            border: none;
            padding: 18px 42px;
            font-size: 19px;
            font-weight: 800;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 0 25px rgba(165, 94, 234, 0.5);
            transition: all 0.25s ease;
            outline: none;
            letter-spacing: 1px;
        }

        .btn-self-destruct:hover {
            transform: scale(1.05);
            box-shadow: 0 0 40px rgba(165, 94, 234, 0.8);
        }

        .btn-self-destruct:disabled {
            background: #333;
            color: #777;
            box-shadow: none;
            cursor: not-allowed;
            transform: none;
        }

        /* 고죠 사토루 풀 영창 자막 */
        #chant-overlay {
            position: absolute;
            bottom: 110px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            text-align: center;
            pointer-events: none;
            z-index: 20;
        }

        .chant-line {
            font-size: 22px;
            font-weight: 900;
            margin: 6px 0;
            opacity: 0;
            transform: translateY(12px);
            transition: all 0.35s ease-out;
            color: #d1d8e0;
            text-shadow: 0 0 10px rgba(0, 0, 0, 0.9);
        }

        .chant-line.active {
            opacity: 1;
            transform: translateY(0);
        }

        .chant-line.highlight-blue {
            color: #4bcffa;
            text-shadow: 0 0 18px #4bcffa;
        }

        .chant-line.highlight-red {
            color: #ff4d4d;
            text-shadow: 0 0 18px #ff4d4d;
        }

        .chant-line.highlight-purple {
            color: #a55eea;
            font-size: 34px;
            text-shadow: 0 0 30px #a55eea, 0 0 60px #00d2d3;
        }

        /* 화면 플래시 이펙트 */
        #fx-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 5;
            opacity: 0;
            background: white;
            transition: opacity 0.1s ease;
        }
    </style>
</head>
<body>
    <div id="game-container">
        <canvas id="canvas"></canvas>
        <div id="fx-overlay"></div>

        <div id="ui-layer">
            <div class="header">
                <div class="boss-info">
                    <div id="boss-name" class="boss-name">보스 탐색 중...</div>
                    <div class="hp-bar-container">
                        <div id="hp-bar" class="hp-bar"></div>
                        <div id="hp-text" class="hp-text">0 / 0</div>
                    </div>
                </div>
            </div>

            <!-- 풀 영창 출력 레이어 -->
            <div id="chant-overlay">
                <div class="chant-line" id="chant-1">九綱 (아홉 개의 밧줄)</div>
                <div class="chant-line" id="chant-2">偏光 (편광)</div>
                <div class="chant-line" id="chant-3">烏と黑杖 (까마귀와 범의 자루)</div>
                <div class="chant-line" id="chant-4">表裏の間 (겉과 속의 사이)</div>
                <div class="chant-line highlight-blue" id="chant-5">術式 順轉「蒼」 (술식 순전 「창」)</div>
                <div class="chant-line highlight-red" id="chant-6">術式 反轉「赫」 (술식 반전 「혁」)</div>
                <div class="chant-line highlight-purple" id="chant-7">虛式「紫」 (허식 「자」)</div>
            </div>

            <div class="controls">
                <button id="btn-suicide" class="btn-self-destruct" onclick="startSelfDestruction()">허식 「자」 - 무제한 자폭</button>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const fxOverlay = document.getElementById('fx-overlay');

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resize);
        resize();

        let currentBossIndex = 0;
        const baseHp = 1000;
        let isExploding = false;
        let isSpawning = false;
        let particles = [];
        let screenShake = 0;

        // 100가지 보스 생성을 위한 조합 배열
        const bossPrefixes = [
            "불타는", "얼어붙은", "심연의", "광기의", "태고의", "죽음의", "파멸의", "전설의", "신성한", "암흑의",
            "공허의", "복수심에 찬", "분노하는", "절망의", "기괴한", "폭주하는", "영원한", "잊혀진", "타락한", "피에 줄린",
            "초월적인", "무자비한", "잔혹한", "원한 서린", "혼돈의", "지옥의", "환영의", "환상의", "번개의", "강철의"
        ];
        
        const bossTypes = [
            "드래곤", "골렘", "데몬", "타이탄", "리치", "베히모스", "히드라", "킹 칠러", "사이클롭스", "서큐버스",
            "발키리", "가고일", "슬라임 퀸", "네크로맨서", "크라켄", "아수라", "바실리스크", "그리폰", "페닉스", "오거 킹",
            "나이트메어", "아비도스", "섀도우 킹", "미노타우로스", "메두사", "뱀파이어 로드", "케르베로스", "소울 이터", "마왕", "신"
        ];

        // 100종의 보스 데이터 생성 (체력 1.2배씩 증가)
        const bossList = [];
        for (let i = 0; i < 100; i++) {
            const pIdx = i % bossPrefixes.length;
            const tIdx = Math.floor(i / bossPrefixes.length) % bossTypes.length;
            const name = `STAGE ${i + 1}. ${bossPrefixes[pIdx]} ${bossTypes[tIdx]}`;
            const hp = Math.floor(baseHp * Math.pow(1.2, i));
            const hue = (i * 37) % 360;
            const color = `hsl(${hue}, 80%, 50%)`;

            bossList.push({ name, maxHp: hp, currentHp: hp, color });
        }

        let currentBoss = null;

        // 보스 스폰 처리 (사망 후 2.5초 대기 후 출현)
        function spawnNextBoss() {
            if (currentBossIndex >= bossList.length) {
                document.getElementById('boss-name').innerText = "ALL BOSSES CLEARED!";
                document.getElementById('hp-bar').style.width = '0%';
                document.getElementById('hp-text').innerText = "승리했습니다!";
                return;
            }

            isSpawning = true;
            document.getElementById('boss-name').innerText = "다음 보스 출현 중...";
            document.getElementById('hp-bar').style.width = '0%';
            document.getElementById('hp-text').innerText = "WAITING...";

            setTimeout(() => {
                currentBoss = bossList[currentBossIndex];
                updateBossUI();
                isSpawning = false;
                document.getElementById('btn-suicide').disabled = false;
            }, 2500);
        }

        function updateBossUI() {
            if (!currentBoss) return;
            document.getElementById('boss-name').innerText = currentBoss.name;
            const hpPercent = Math.max(0, (currentBoss.currentHp / currentBoss.maxHp) * 100);
            document.getElementById('hp-bar').style.width = hpPercent + '%';
            document.getElementById('hp-text').innerText = `${formatNumber(Math.ceil(currentBoss.currentHp))} / ${formatNumber(currentBoss.maxHp)}`;
        }

        function formatNumber(num) {
            return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        }

        // 파티클 생성
        function createParticles(x, y, color, count, speedMultiplier = 1) {
            for (let i = 0; i < count; i++) {
                const angle = Math.random() * Math.PI * 2;
                const speed = (Math.random() * 8 + 2) * speedMultiplier;
                particles.push({
                    x, y,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed,
                    size: Math.random() * 6 + 2,
                    color: color,
                    alpha: 1,
                    decay: Math.random() * 0.015 + 0.005
                });
            }
        }

        // 영창 및 연출 실행
        function startSelfDestruction() {
            if (isExploding || isSpawning || !currentBoss) return;

            isExploding = true;
            document.getElementById('btn-suicide').disabled = true;

            const chantIds = ['chant-1', 'chant-2', 'chant-3', 'chant-4', 'chant-5', 'chant-6', 'chant-7'];
            chantIds.forEach(id => document.getElementById(id).classList.remove('active'));

            const delays = [500, 1500, 2500, 3500, 4700, 5900, 7200];

            delays.forEach((delay, index) => {
                setTimeout(() => {
                    document.getElementById(chantIds[index]).classList.add('active');

                    if (index === 4) { // 苍 (창)
                        screenShake = 6;
                        createParticles(canvas.width / 2, canvas.height / 2, '#4bcffa', 160, 1.5);
                    } else if (index === 5) { // 赫 (혁)
                        screenShake = 12;
                        createParticles(canvas.width / 2, canvas.height / 2, '#ff4d4d', 220, 2);
                    } else if (index === 6) { // 紫 (자)
                        screenShake = 22;
                        fxOverlay.style.background = '#a55eea';
                        fxOverlay.style.opacity = '0.4';
                        setTimeout(() => fxOverlay.style.opacity = '0', 300);
                    }
                }, delay);
            });

            // 영창 후 대폭발 진입
            setTimeout(() => {
                triggerFinalExplosion();
            }, 8500);
        }

        // 대폭발 연출 (3.5초간 지속 폭발)
        function triggerFinalExplosion() {
            screenShake = 45;
            
            fxOverlay.style.background = '#ffffff';
            fxOverlay.style.opacity = '1';
            setTimeout(() => {
                fxOverlay.style.opacity = '0';
                fxOverlay.style.transition = 'opacity 2.5s ease-out';
            }, 100);

            currentBoss.currentHp = 0;
            updateBossUI();

            let explosionDuration = 0;
            const explosionInterval = setInterval(() => {
                explosionDuration += 100;
                
                const colors = ['#a55eea', '#4bcffa', '#ff4d4d', '#ffffff', '#8854d0'];
                const randomColor = colors[Math.floor(Math.random() * colors.length)];
                
                const rx = canvas.width / 2 + (Math.random() - 0.5) * 450;
                const ry = canvas.height / 2 + (Math.random() - 0.5) * 450;
                
                createParticles(rx, ry, randomColor, 90, 3);
                screenShake = Math.max(6, 35 - (explosionDuration / 100));

                if (explosionDuration >= 3500) {
                    clearInterval(explosionInterval);
                    finishExplosion();
                }
            }, 100);
        }

        function finishExplosion() {
            const chantIds = ['chant-1', 'chant-2', 'chant-3', 'chant-4', 'chant-5', 'chant-6', 'chant-7'];
            chantIds.forEach(id => document.getElementById(id).classList.remove('active'));

            isExploding = false;
            currentBossIndex++;

            spawnNextBoss();
        }

        // 메인 프레임 렌더링
        function render() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            ctx.save();
            if (screenShake > 0) {
                const sx = (Math.random() - 0.5) * screenShake;
                const sy = (Math.random() - 0.5) * screenShake;
                ctx.translate(sx, sy);
                screenShake *= 0.92;
                if (screenShake < 0.5) screenShake = 0;
            }

            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;

            if (currentBoss && currentBoss.currentHp > 0) {
                ctx.beginPath();
                ctx.arc(centerX, centerY, 80, 0, Math.PI * 2);
                ctx.fillStyle = currentBoss.color;
                ctx.shadowColor = currentBoss.color;
                ctx.shadowBlur = 30;
                ctx.fill();
                ctx.closePath();
                ctx.shadowBlur = 0;

                const pulse = Math.sin(Date.now() * 0.005) * 6;
                ctx.beginPath();
                ctx.arc(centerX, centerY, 85 + pulse, 0, Math.PI * 2);
                ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
                ctx.lineWidth = 3;
                ctx.stroke();
            }

            for (let i = particles.length - 1; i >= 0; i--) {
                let p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.alpha -= p.decay;

                if (p.alpha <= 0) {
                    particles.splice(i, 1);
                    continue;
                }

                ctx.save();
                ctx.globalAlpha = p.alpha;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.shadowColor = p.color;
                ctx.shadowBlur = 10;
                ctx.fill();
                ctx.restore();
            }

            ctx.restore();
            requestAnimationFrame(render);
        }

        spawnNextBoss();
        render();
    </script>
</body>
</html>
