import streamlit as st
import streamlit.components.v1 as components

# 1. Full-Width 화면 최적화 CSS
st.markdown("""
    <style>
        .main .block-container {
            max-width: 100% !important;
            padding: 0.5rem 1rem !important;
        }
        iframe {
            width: 100% !important;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

st.title("⚔️ 기가 수행평가: 하드코어 2D 탄막 던전 크롤러")
st.caption("🎮 이동: WASD / 방향키 | 공격: 좌클릭 | 클래스 스킬: 우클릭 | 대시(무적): Spacebar")

# 2. 고퀄리티 애니메이션 & 난이도 상승 Canvas 2D 엔진
game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background-color: #08080a;
        color: #fff;
        font-family: 'Consolas', 'Courier New', monospace;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
    }
    #game-container {
        position: relative;
        width: 1400px;
        height: 750px;
        border: 2px solid #00f0ff;
        border-radius: 10px;
        box-shadow: 0 0 35px rgba(0, 240, 255, 0.25);
        overflow: hidden;
        background: #111318;
    }
    canvas {
        display: block;
        background: #0a0b0e;
    }
    #ui-layer {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none;
        padding: 20px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .hud-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    .bar-container {
        width: 280px;
        background: rgba(10, 11, 14, 0.85);
        padding: 10px;
        border-radius: 6px;
        border: 1px solid rgba(0, 240, 255, 0.3);
    }
    .bar-label { font-size: 11px; font-weight: bold; margin-bottom: 3px; color: #8a99ad; letter-spacing: 1px; }
    .bar-outer {
        width: 100%; height: 12px;
        background: #1a1d24;
        border-radius: 6px;
        overflow: hidden;
        margin-bottom: 8px;
    }
    .bar-inner-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff0055, #ff5500); transition: width 0.1s; }
    .bar-inner-exp { width: 0%; height: 100%; background: linear-gradient(90deg, #00f0ff, #7000ff); transition: width 0.1s; }
    
    .hud-bottom {
        display: flex;
        justify-content: center;
        gap: 20px;
    }
    .skill-box {
        width: 60px; height: 60px;
        background: rgba(10, 11, 14, 0.85);
        border: 2px solid #00f0ff;
        border-radius: 8px;
        display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        font-size: 11px; font-weight: bold;
        position: relative;
    }

    #class-select {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(8, 8, 10, 0.95);
        display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        z-index: 100;
        pointer-events: auto;
    }
    .class-cards { display: flex; gap: 25px; margin-top: 30px; }
    .card {
        background: #14171f;
        border: 2px solid #222735;
        border-radius: 12px;
        padding: 25px;
        width: 250px;
        text-align: center;
        cursor: pointer;
        transition: all 0.25s ease;
    }
    .card:hover {
        border-color: #00f0ff;
        transform: translateY(-10px);
        box-shadow: 0 0 25px rgba(0, 240, 255, 0.4);
    }
    .card h2 { color: #00f0ff; margin-bottom: 12px; font-size: 22px; }
    .card p { font-size: 12px; color: #8a99ad; line-height: 1.5; }
</style>
</head>
<body>

<div id="game-container">
    <canvas id="gameCanvas" width="1400" height="750"></canvas>
    
    <div id="ui-layer">
        <div class="hud-top">
            <div class="bar-container">
                <div class="bar-label">HP</div>
                <div class="bar-outer"><div id="hp-bar" class="bar-inner-hp"></div></div>
                <div class="bar-label">EXP</div>
                <div class="bar-outer"><div id="exp-bar" class="bar-inner-exp"></div></div>
                <div id="level-info" style="color: #00f0ff; font-weight: bold; font-size: 13px;">Lv.1 클래스</div>
            </div>
            <div style="text-align: right; background: rgba(10, 11, 14, 0.85); padding: 10px 20px; border-radius: 6px; border: 1px solid rgba(255, 0, 85, 0.4);">
                <div id="floor-info" style="font-size: 22px; font-weight: bold; color: #ff0055;">B1F 던전</div>
                <div id="score-info" style="font-size: 12px; color: #8a99ad;">처치 수: 0</div>
            </div>
        </div>

        <div class="hud-bottom">
            <div class="skill-box"><span>SPACE</span><span style="color:#00f0ff">대시</span></div>
            <div class="skill-box"><span>R-CLICK</span><span style="color:#7000ff">스킬</span></div>
        </div>
    </div>

    <div id="class-select">
        <h1 style="color: #00f0ff; font-size: 36px; letter-spacing: 2px;">직업 선택</h1>
        <p style="color: #8a99ad; margin-top: 8px;">높은 난이도의 몬스터와 보스를 격파하세요.</p>
        <div class="class-cards">
            <div class="card" onclick="selectClass('Warrior')">
                <h2>🛡️ 버서커</h2>
                <p>높은 체력 / 360도 강력한 충격파 스킬 발사</p>
            </div>
            <div class="card" onclick="selectClass('Mage')">
                <h2>🔮 아케인 마법사</h2>
                <p>유도형 마법 탄환 & 유도 폭발 스킬 구사</p>
            </div>
            <div class="card" onclick="selectClass('Ranger')">
                <h2>🏹 섀도우 궁수</h2>
                <p>초고속 이동 & 5방향 관통 샷 스킬 사용</p>
            </div>
        </div>
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let gameState = 'MENU';
let killCount = 0;
let dungeonLevel = 1;
let screenShake = 0;

let player = {
    x: 700, y: 375, radius: 15,
    hp: 100, maxHp: 100, exp: 0, maxExp: 40, level: 1,
    speed: 4.2, classType: 'Warrior',
    skillCd: 0, dashCd: 0, isDashing: false,
    trail: []
};

let keys = {};
let mouse = { x: 0, y: 0, left: false, right: false };
let projectiles = [];
let enemyProjectiles = [];
let enemies = [];
let particles = [];
let floatTexts = [];

window.addEventListener('keydown', e => keys[e.key.toLowerCase()] = true);
window.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);
canvas.addEventListener('mousemove', e => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
});
canvas.addEventListener('mousedown', e => {
    if(e.button === 0) mouse.left = true;
    if(e.button === 2) { mouse.right = true; e.preventDefault(); }
});
canvas.addEventListener('mouseup', e => {
    if(e.button === 0) mouse.left = false;
    if(e.button === 2) mouse.right = false;
});
canvas.addEventListener('contextmenu', e => e.preventDefault());

function selectClass(type) {
    player.classType = type;
    if(type === 'Warrior') { player.hp = player.maxHp = 200; player.speed = 3.8; }
    if(type === 'Mage') { player.hp = player.maxHp = 100; player.speed = 4.3; }
    if(type === 'Ranger') { player.hp = player.maxHp = 120; player.speed = 5.2; }
    
    document.getElementById('class-select').style.display = 'none';
    gameState = 'PLAYING';
    spawnEnemies();
    gameLoop();
}

function spawnEnemies() {
    enemies = [];
    enemyProjectiles = [];
    let count = 6 + dungeonLevel * 3;
    let isBossFloor = (dungeonLevel % 3 === 0);

    if(isBossFloor) {
        // 보스 몬스터
        enemies.push({
            x: 700, y: 150, radius: 45,
            hp: 800 + dungeonLevel * 300, maxHp: 800 + dungeonLevel * 300,
            speed: 1.2, color: '#ff0055', type: 'boss', shootCd: 0
        });
    }

    for(let i=0; i<count; i++) {
        let randType = Math.random();
        let eType = 'chaser';
        let color = '#e74c3c';
        let radius = 16;
        let hp = 45 + dungeonLevel * 15;
        let speed = 2.0 + Math.random() * 1.0;

        if(randType > 0.6) {
            eType = 'shooter'; color = '#9b59b6'; radius = 14; speed = 1.8;
        } else if(randType > 0.8) {
            eType = 'dasher'; color = '#e67e22'; radius = 12; speed = 3.5;
        }

        enemies.push({
            x: Math.random() * (canvas.width - 160) + 80,
            y: Math.random() * (canvas.height - 160) + 80,
            radius: radius, hp: hp, maxHp: hp, speed: speed,
            color: color, type: eType, shootCd: 0, dashCd: 0
        });
    }
}

let lastAttack = 0;
function attack() {
    let now = Date.now();
    let cooldown = player.classType === 'Ranger' ? 140 : 250;
    if(now - lastAttack < cooldown) return;
    lastAttack = now;

    screenShake = 3;
    let angle = Math.atan2(mouse.y - player.y, mouse.x - player.x);
    projectiles.push({
        x: player.x, y: player.y,
        vx: Math.cos(angle) * 11, vy: Math.sin(angle) * 11,
        damage: player.classType === 'Mage' ? 45 : 30,
        color: player.classType === 'Mage' ? '#7000ff' : '#00f0ff',
        radius: player.classType === 'Mage' ? 8 : 5
    });

    // 총구 화염 이펙트
    addParticles(player.x + Math.cos(angle)*20, player.y + Math.sin(angle)*20, '#00f0ff', 4);
}

function useSkill() {
    if(player.skillCd > 0) return;
    player.skillCd = 240; // 쿨타임
    screenShake = 8;

    if(player.classType === 'Warrior') {
        for(let i=0; i<20; i++) {
            let ang = (Math.PI * 2 / 20) * i;
            projectiles.push({
                x: player.x, y: player.y,
                vx: Math.cos(ang) * 8, vy: Math.sin(ang) * 8,
                damage: 50, color: '#ff0055', radius: 9
            });
        }
    } else if(player.classType === 'Mage') {
        for(let i=0; i<14; i++) {
            let ang = (Math.PI * 2 / 14) * i;
            projectiles.push({
                x: player.x, y: player.y,
                vx: Math.cos(ang) * 9, vy: Math.sin(ang) * 9,
                damage: 40, color: '#a29bfe', radius: 7
            });
        }
    } else if(player.classType === 'Ranger') {
        let baseAngle = Math.atan2(mouse.y - player.y, mouse.x - player.x);
        for(let offset of [-0.4, -0.2, 0, 0.2, 0.4]) {
            let ang = baseAngle + offset;
            projectiles.push({
                x: player.x, y: player.y,
                vx: Math.cos(ang) * 14, vy: Math.sin(ang) * 14,
                damage: 35, color: '#00b09b', radius: 5
            });
        }
    }
}

function addFloatText(x, y, text, color) {
    floatTexts.push({ x: x, y: y, text: text, color: color, life: 1.0, vy: -1.5 });
}

function addParticles(x, y, color, count) {
    for(let i=0; i<count; i++) {
        particles.push({
            x: x, y: y,
            vx: (Math.random() - 0.5) * 7,
            vy: (Math.random() - 0.5) * 7,
            color: color, life: 1.0
        });
    }
}

function update() {
    if(gameState !== 'PLAYING') return;

    if(player.skillCd > 0) player.skillCd--;
    if(player.dashCd > 0) player.dashCd--;
    if(screenShake > 0) screenShake--;

    // 대시
    if(keys[' '] && player.dashCd === 0) {
        player.isDashing = true;
        player.dashCd = 70;
        screenShake = 5;
        setTimeout(() => player.isDashing = false, 180);
    }

    // 이동
    let moveSpeed = player.isDashing ? player.speed * 2.8 : player.speed;
    let dx = 0, dy = 0;
    if(keys['a'] || keys['arrowleft']) dx -= 1;
    if(keys['d'] || keys['arrowright']) dx += 1;
    if(keys['w'] || keys['arrowup']) dy -= 1;
    if(keys['s'] || keys['arrowdown']) dy += 1;

    if(dx !== 0 && dy !== 0) { dx *= 0.7071; dy *= 0.7071; }

    player.x = Math.max(player.radius, Math.min(canvas.width - player.radius, player.x + dx * moveSpeed));
    player.y = Math.max(player.radius, Math.min(canvas.height - player.radius, player.y + dy * moveSpeed));

    // 플레이어 잔상 효과
    if(dx !== 0 || dy !== 0) {
        player.trail.push({ x: player.x, y: player.y, alpha: 0.5 });
        if(player.trail.length > 6) player.trail.shift();
    }

    if(mouse.left) attack();
    if(mouse.right) useSkill();

    // 아군 투사체
    projectiles.forEach((p, pi) => {
        p.x += p.vx; p.y += p.vy;

        if(p.x < 0 || p.x > canvas.width || p.y < 0 || p.y > canvas.height) {
            projectiles.splice(pi, 1);
            return;
        }

        enemies.forEach((e, ei) => {
            let dist = Math.hypot(e.x - p.x, e.y - p.y);
            if(dist < e.radius + p.radius) {
                e.hp -= p.damage;
                addParticles(p.x, p.y, p.color, 6);
                addFloatText(e.x, e.y - 10, Math.floor(p.damage), '#ff0055');
                projectiles.splice(pi, 1);

                if(e.hp <= 0) {
                    killCount++;
                    player.exp += e.type === 'boss' ? 150 : 25;
                    addParticles(e.x, e.y, e.color, 15);
                    enemies.splice(ei, 1);

                    if(player.exp >= player.maxExp) {
                        player.level++;
                        player.exp -= player.maxExp;
                        player.maxExp = Math.floor(player.maxExp * 1.4);
                        player.maxHp += 25;
                        player.hp = player.maxHp;
                        addFloatText(player.x, player.y - 20, "LEVEL UP!", '#00f0ff');
                    }
                }
            }
        });
    });

    // 적 AI & 공격
    enemies.forEach(e => {
        let ang = Math.atan2(player.y - e.y, player.x - e.x);

        if(e.type === 'chaser' || e.type === 'dasher') {
            e.x += Math.cos(ang) * e.speed;
            e.y += Math.sin(ang) * e.speed;
        } else if(e.type === 'shooter') {
            // 적 원거리 투사체 발사
            e.shootCd++;
            if(e.shootCd > 90) {
                e.shootCd = 0;
                enemyProjectiles.push({
                    x: e.x, y: e.y,
                    vx: Math.cos(ang) * 5, vy: Math.sin(ang) * 5,
                    radius: 5, damage: 15
                });
            }
        } else if(e.type === 'boss') {
            e.shootCd++;
            if(e.shootCd > 60) {
                e.shootCd = 0;
                // 보스 링 탄막 사격
                for(let i=0; i<12; i++) {
                    let bAng = (Math.PI * 2 / 12) * i;
                    enemyProjectiles.push({
                        x: e.x, y: e.y,
                        vx: Math.cos(bAng) * 4.5, vy: Math.sin(bAng) * 4.5,
                        radius: 6, damage: 20
                    });
                }
            }
        }

        // 플레이어 피격 (몸통 충돌)
        let dist = Math.hypot(player.x - e.x, player.y - e.y);
        if(dist < player.radius + e.radius && !player.isDashing) {
            player.hp -= 0.6;
            screenShake = 4;
            if(player.hp <= 0) {
                alert(`게임 오버!\n도달 층수: B${dungeonLevel}F | 처치 수: ${killCount}`);
                location.reload();
            }
        }
    });

    // 적 투사체 업데이트
    enemyProjectiles.forEach((ep, epi) => {
        ep.x += ep.vx; ep.y += ep.vy;

        let dist = Math.hypot(player.x - ep.x, player.y - ep.y);
        if(dist < player.radius + ep.radius && !player.isDashing) {
            player.hp -= ep.damage;
            screenShake = 6;
            addParticles(ep.x, ep.y, '#ff0055', 8);
            enemyProjectiles.splice(epi, 1);

            if(player.hp <= 0) {
                alert(`게임 오버!\n도달 층수: B${dungeonLevel}F | 처치 수: ${killCount}`);
                location.reload();
            }
        }

        if(ep.x < 0 || ep.x > canvas.width || ep.y < 0 || ep.y > canvas.height) {
            enemyProjectiles.splice(epi, 1);
        }
    });

    if(enemies.length === 0) {
        dungeonLevel++;
        spawnEnemies();
    }

    // 파티클 & 텍스트 감소
    particles.forEach((pt, pti) => {
        pt.x += pt.vx; pt.y += pt.vy; pt.life -= 0.05;
        if(pt.life <= 0) particles.splice(pti, 1);
    });

    floatTexts.forEach((ft, fti) => {
        ft.y += ft.vy; ft.life -= 0.03;
        if(ft.life <= 0) floatTexts.splice(fti, 1);
    });

    player.trail.forEach((t) => t.alpha -= 0.05);

    // UI
    document.getElementById('hp-bar').style.width = Math.max(0, (player.hp / player.maxHp * 100)) + '%';
    document.getElementById('exp-bar').style.width = Math.min(100, (player.exp / player.maxExp * 100)) + '%';
    document.getElementById('level-info').innerText = `Lv.${player.level} ${player.classType}`;
    document.getElementById('floor-info').innerText = `B${dungeonLevel}F 던전`;
    document.getElementById('score-info').innerText = `처치 수: ${killCount}`;
}

function draw() {
    ctx.save();
    
    // 화면 흔들림 효과
    if(screenShake > 0) {
        let sx = (Math.random() - 0.5) * screenShake;
        let sy = (Math.random() - 0.5) * screenShake;
        ctx.translate(sx, sy);
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Grid 배경
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
    ctx.lineWidth = 1;
    for(let x=0; x<canvas.width; x+=60) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,canvas.height); ctx.stroke(); }
    for(let y=0; y<canvas.height; y+=60) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(canvas.width,y); ctx.stroke(); }

    // 플레이어 잔상(트레일) 렌더링
    player.trail.forEach(t => {
        if(t.alpha > 0) {
            ctx.fillStyle = `rgba(0, 240, 255, ${t.alpha * 0.4})`;
            ctx.beginPath(); ctx.arc(t.x, t.y, player.radius, 0, Math.PI*2); ctx.fill();
        }
    });

    // 플레이어
    ctx.fillStyle = player.classType === 'Warrior' ? '#ff0055' : (player.classType === 'Mage' ? '#a29bfe' : '#00b09b');
    ctx.beginPath(); ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = player.isDashing ? '#00f0ff' : '#ffffff';
    ctx.lineWidth = 2.5; ctx.stroke();

    // 방향 화살표
    let pAngle = Math.atan2(mouse.y - player.y, mouse.x - player.x);
    ctx.strokeStyle = '#00f0ff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(player.x + Math.cos(pAngle)*18, player.y + Math.sin(pAngle)*18);
    ctx.lineTo(player.x + Math.cos(pAngle)*28, player.y + Math.sin(pAngle)*28);
    ctx.stroke();

    // 아군 투사체
    projectiles.forEach(p => {
        ctx.fillStyle = p.color;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2); ctx.fill();
    });

    // 적 투사체
    enemyProjectiles.forEach(ep => {
        ctx.fillStyle = '#ff0055';
        ctx.beginPath(); ctx.arc(ep.x, ep.y, ep.radius, 0, Math.PI * 2); ctx.fill();
    });

    // 적
    enemies.forEach(e => {
        ctx.fillStyle = e.color;
        ctx.beginPath(); ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2); ctx.fill();
        
        // 체력바
        ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
        ctx.fillRect(e.x - 18, e.y - e.radius - 10, 36, 4);
        ctx.fillStyle = '#ff0055';
        ctx.fillRect(e.x - 18, e.y - e.radius - 10, (e.hp / e.maxHp) * 36, 4);
    });

    // 파티클
    particles.forEach(pt => {
        ctx.fillStyle = pt.color;
        ctx.globalAlpha = pt.life;
        ctx.beginPath(); ctx.arc(pt.x, pt.y, 3, 0, Math.PI * 2); ctx.fill();
        ctx.globalAlpha = 1.0;
    });

    // 대미지 수치 텍스트
    floatTexts.forEach(ft => {
        ctx.fillStyle = ft.color;
        ctx.globalAlpha = ft.life;
        ctx.font = 'bold 13px Consolas';
        ctx.fillText(ft.text, ft.x - 8, ft.y);
        ctx.globalAlpha = 1.0;
    });

    ctx.restore();
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}
</script>
</body>
</html>
"""

# 3. 확장된 맵 스케일에 맞는 높이로 임베딩
components.html(game_html, height=780)
