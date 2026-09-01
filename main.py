import streamlit as st
import streamlit.components.v1 as components

# 1. 화면 전체를 가득 채우는 CSS 스타일 적용 (반 짤림 현상 완벽 해결)
st.markdown("""
    <style>
        .main .block-container {
            max-width: 100% !important;
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        iframe {
            width: 100% !important;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

st.title("⚔️ 기가 수행평가: 웹 2D 탑다운 액션 RPG 던전 크롤러")
st.caption("🎮 조작법 | 이동: WASD / 방향키 | 기본공격: 마우스 좌클릭 | 특수스킬: 마우스 우클릭 | 대시: 스페이스바")

# 2. 고퀄리티 Canvas 2D 게임 엔진 (확장된 해상도 & 시스템)
game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background-color: #0b0c10;
        color: #fff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
    }
    #game-container {
        position: relative;
        width: 1100px;
        height: 650px;
        border: 2px solid #45f3ff;
        border-radius: 12px;
        box-shadow: 0 0 30px rgba(69, 243, 255, 0.3);
        overflow: hidden;
        background: #1f2833;
    }
    canvas {
        display: block;
        background: #0b0c10;
    }
    #ui-layer {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none;
        padding: 15px;
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
        width: 240px;
        background: rgba(0,0,0,0.6);
        padding: 8px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .bar-label { font-size: 12px; font-weight: bold; margin-bottom: 2px; color: #c5c6c7; }
    .bar-outer {
        width: 100%; height: 14px;
        background: #111;
        border-radius: 7px;
        overflow: hidden;
        margin-bottom: 6px;
    }
    .bar-inner-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff416c, #ff4b2b); transition: width 0.1s; }
    .bar-inner-exp { width: 0%; height: 100%; background: linear-gradient(90deg, #00b09b, #96c93d); transition: width 0.1s; }
    
    .hud-bottom {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
    }
    .skill-slot {
        width: 50px; height: 50px;
        background: rgba(0,0,0,0.7);
        border: 2px solid #66fcf1;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-size: 10px;
        font-weight: bold;
        position: relative;
    }
    .skill-slot .cd-overlay {
        position: absolute; top:0; left:0; width:100%; height:100%;
        background: rgba(0,0,0,0.7);
        height: 0%;
        transition: height 0.1s;
    }

    #class-select {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(11, 12, 16, 0.95);
        display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        z-index: 100;
        pointer-events: auto;
    }
    .class-card-group { display: flex; gap: 20px; margin-top: 25px; }
    .class-card {
        background: #1f2833;
        border: 2px solid #45f3ff;
        border-radius: 10px;
        padding: 20px;
        width: 220px;
        text-align: center;
        cursor: pointer;
        transition: 0.3s;
    }
    .class-card:hover { transform: translateY(-8px); box-shadow: 0 0 20px #45f3ff; }
    .class-card h3 { color: #66fcf1; margin-bottom: 10px; }
    .class-card p { font-size: 13px; color: #c5c6c7; line-height: 1.4; }
</style>
</head>
<body>

<div id="game-container">
    <canvas id="gameCanvas" width="1100" height="650"></canvas>
    
    <div id="ui-layer">
        <div class="hud-top">
            <div class="bar-container">
                <div class="bar-label">HEALTH</div>
                <div class="bar-outer"><div id="hp-bar" class="bar-inner-hp"></div></div>
                <div class="bar-label">EXP</div>
                <div class="bar-outer"><div id="exp-bar" class="bar-inner-exp"></div></div>
                <div id="level-info" style="color: #66fcf1; font-weight: bold; font-size: 14px; margin-top: 4px;">Lv.1 전사</div>
            </div>
            <div style="text-align: right; background: rgba(0,0,0,0.6); padding: 8px 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2);">
                <div id="floor-info" style="font-size: 18px; font-weight: bold; color: #ff0055;">B1F 던전</div>
                <div id="score-info" style="font-size: 12px; color: #c5c6c7;">처치한 적: 0</div>
            </div>
        </div>

        <div class="hud-bottom">
            <div class="skill-slot">
                <span>Space</span>
                <span>대시</span>
            </div>
            <div class="skill-slot">
                <span>R-Click</span>
                <span>스킬</span>
            </div>
        </div>
    </div>

    <div id="class-select">
        <h1 style="color: #66fcf1; font-size: 32px; text-shadow: 0 0 10px #66fcf1;">직업을 선택하세요</h1>
        <p style="color: #c5c6c7; margin-top: 5px;">기가 수행평가 2D 액션 던전 크롤러 프로젝트</p>
        <div class="class-card-group">
            <div class="class-card" onclick="selectClass('Warrior')">
                <h3>🛡️ 전사</h3>
                <p>높은 체력과 강력한 범위 충격파 스킬을 사용하는 근접 특화 클래스</p>
            </div>
            <div class="class-card" onclick="selectClass('Mage')">
                <h3>🔮 마법사</h3>
                <p>360도 전방위 유도 마법 탄환 스킬을 구사하는 강력한 딜러</p>
            </div>
            <div class="class-card" onclick="selectClass('Ranger')">
                <h3>🏹 궁수</h3>
                <p>빠른 이동속도와 멀티 샷 부채꼴 사격 스킬을 가진 기동형 클래스</p>
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

let player = {
    x: 550, y: 325, radius: 16,
    hp: 100, maxHp: 100, exp: 0, maxExp: 50, level: 1,
    speed: 4, classType: 'Warrior',
    skillCd: 0, dashCd: 0, isDashing: false
};

let keys = {};
let mouse = { x: 0, y: 0, left: false, right: false };
let projectiles = [];
let enemies = [];
let particles = [];
let items = [];

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
    if(type === 'Warrior') { player.hp = player.maxHp = 160; player.speed = 3.8; }
    if(type === 'Mage') { player.hp = player.maxHp = 90; player.speed = 4.2; }
    if(type === 'Ranger') { player.hp = player.maxHp = 110; player.speed = 5.0; }
    
    document.getElementById('class-select').style.display = 'none';
    gameState = 'PLAYING';
    spawnEnemies();
    gameLoop();
}

function spawnEnemies() {
    enemies = [];
    let count = 5 + dungeonLevel * 2;
    for(let i=0; i<count; i++) {
        let isBoss = (i === 0 && dungeonLevel % 3 === 0);
        enemies.push({
            x: Math.random() * (canvas.width - 120) + 60,
            y: Math.random() * (canvas.height - 120) + 60,
            radius: isBoss ? 32 : (Math.random() > 0.5 ? 14 : 18),
            hp: isBoss ? 300 + dungeonLevel * 50 : 30 + dungeonLevel * 12,
            maxHp: isBoss ? 300 + dungeonLevel * 50 : 30 + dungeonLevel * 12,
            speed: isBoss ? 1.2 : (Math.random() * 1.5 + 1.2),
            color: isBoss ? '#ff0055' : (Math.random() > 0.5 ? '#e74c3c' : '#e67e22'),
            isBoss: isBoss
        });
    }
}

let lastAttack = 0;
function attack() {
    let now = Date.now();
    let cooldown = player.classType === 'Ranger' ? 180 : 300;
    if(now - lastAttack < cooldown) return;
    lastAttack = now;

    let angle = Math.atan2(mouse.y - player.y, mouse.x - player.x);
    projectiles.push({
        x: player.x, y: player.y,
        vx: Math.cos(angle) * 9, vy: Math.sin(angle) * 9,
        damage: player.classType === 'Mage' ? 40 : 25,
        color: player.classType === 'Mage' ? '#a29bfe' : '#ffeaa7',
        radius: player.classType === 'Mage' ? 7 : 5,
        owner: 'player'
    });
}

function useSkill() {
    if(player.skillCd > 0) return;
    player.skillCd = 200; // Frame base cd

    if(player.classType === 'Warrior') {
        // 충격파
        for(let i=0; i<16; i++) {
            let ang = (Math.PI * 2 / 16) * i;
            projectiles.push({
                x: player.x, y: player.y,
                vx: Math.cos(ang) * 6, vy: Math.sin(ang) * 6,
                damage: 30, color: '#ff7675', radius: 8, owner: 'player'
            });
        }
    } else if(player.classType === 'Mage') {
        // 전방위 화염구
        for(let i=0; i<12; i++) {
            let ang = (Math.PI * 2 / 12) * i;
            projectiles.push({
                x: player.x, y: player.y,
                vx: Math.cos(ang) * 7, vy: Math.sin(ang) * 7,
                damage: 25, color: '#74b9ff', radius: 6, owner: 'player'
            });
        }
    } else if(player.classType === 'Ranger') {
        // 멀티 샷
        let baseAngle = Math.atan2(mouse.y - player.y, mouse.x - player.x);
        for(let offset of [-0.3, -0.15, 0, 0.15, 0.3]) {
            let ang = baseAngle + offset;
            projectiles.push({
                x: player.x, y: player.y,
                vx: Math.cos(ang) * 12, vy: Math.sin(ang) * 12,
                damage: 20, color: '#55efc4', radius: 4, owner: 'player'
            });
        }
    }
}

function update() {
    if(gameState !== 'PLAYING') return;

    // 쿨타임 감소
    if(player.skillCd > 0) player.skillCd--;
    if(player.dashCd > 0) player.dashCd--;

    // 대시 스킬
    if(keys[' '] && player.dashCd === 0) {
        player.isDashing = true;
        player.dashCd = 60;
        setTimeout(() => player.isDashing = false, 150);
    }

    // 플레이어 이동
    let moveSpeed = player.isDashing ? player.speed * 2.5 : player.speed;
    if(keys['a'] || keys['arrowleft']) player.x = Math.max(player.radius, player.x - moveSpeed);
    if(keys['d'] || keys['arrowright']) player.x = Math.min(canvas.width - player.radius, player.x + moveSpeed);
    if(keys['w'] || keys['arrowup']) player.y = Math.max(player.radius, player.y - moveSpeed);
    if(keys['s'] || keys['arrowdown']) player.y = Math.min(canvas.height - player.radius, player.y + moveSpeed);

    if(mouse.left) attack();
    if(mouse.right) useSkill();

    // 아이템 습득
    items.forEach((item, index) => {
        let dist = Math.hypot(player.x - item.x, player.y - item.y);
        if(dist < player.radius + 10) {
            if(item.type === 'hp') player.hp = Math.min(player.maxHp, player.hp + 35);
            if(item.type === 'exp') player.exp += 25;
            createBurst(item.x, item.y, item.type === 'hp' ? '#ff7675' : '#74b9ff', 8);
            items.splice(index, 1);
        }
    });

    // 투사체 처리
    projectiles.forEach((p, pi) => {
        p.x += p.vx; p.y += p.vy;

        // 화면 밖 제거
        if(p.x < 0 || p.x > canvas.width || p.y < 0 || p.y > canvas.height) {
            projectiles.splice(pi, 1);
            return;
        }

        if(p.owner === 'player') {
            enemies.forEach((e, ei) => {
                let dist = Math.hypot(e.x - p.x, e.y - p.y);
                if(dist < e.radius + p.radius) {
                    e.hp -= p.damage;
                    createBurst(p.x, p.y, p.color, 5);
                    projectiles.splice(pi, 1);

                    if(e.hp <= 0) {
                        killCount++;
                        player.exp += e.isBoss ? 100 : 20;
                        
                        // 아이템 드롭
                        if(Math.random() < 0.4) {
                            items.push({ x: e.x, y: e.y, type: Math.random() < 0.5 ? 'hp' : 'exp' });
                        }

                        enemies.splice(ei, 1);

                        // 레벨업 체크
                        if(player.exp >= player.maxExp) {
                            player.level++;
                            player.exp -= player.maxExp;
                            player.maxExp = Math.floor(player.maxExp * 1.35);
                            player.maxHp += 20;
                            player.hp = player.maxHp;
                            createBurst(player.x, player.y, '#ffeaa7', 20);
                        }
                    }
                }
            });
        }
    });

    // 적 추적 AI
    enemies.forEach(e => {
        let ang = Math.atan2(player.y - e.y, player.x - e.x);
        e.x += Math.cos(ang) * e.speed;
        e.y += Math.sin(ang) * e.speed;

        let dist = Math.hypot(player.x - e.x, player.y - e.y);
        if(dist < player.radius + e.radius && !player.isDashing) {
            player.hp -= e.isBoss ? 1.0 : 0.4;
            if(player.hp <= 0) {
                alert(`게임 오버!\n최종 도달 층수: B${dungeonLevel}F\n처치한 적: ${killCount}마리`);
                location.reload();
            }
        }
    });

    // 다음 층 이동
    if(enemies.length === 0) {
        dungeonLevel++;
        spawnEnemies();
    }

    // 파티클 업데이트
    particles.forEach((pt, pti) => {
        pt.x += pt.vx; pt.y += pt.vy; pt.life -= 0.04;
        if(pt.life <= 0) particles.splice(pti, 1);
    });

    // UI 갱신
    document.getElementById('hp-bar').style.width = Math.max(0, (player.hp / player.maxHp * 100)) + '%';
    document.getElementById('exp-bar').style.width = Math.min(100, (player.exp / player.maxExp * 100)) + '%';
    document.getElementById('level-info').innerText = `Lv.${player.level} ${player.classType}`;
    document.getElementById('floor-info').innerText = `B${dungeonLevel}F 던전`;
    document.getElementById('score-info').innerText = `처치한 적: ${killCount}`;
}

function createBurst(x, y, color, count) {
    for(let i=0; i<count; i++) {
        particles.push({
            x: x, y: y,
            vx: (Math.random() - 0.5) * 6,
            vy: (Math.random() - 0.5) * 6,
            color: color, life: 1.0
        });
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 격자 배경 렌더링
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
    ctx.lineWidth = 1;
    for(let x=0; x<canvas.width; x+=50) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,canvas.height); ctx.stroke(); }
    for(let y=0; y<canvas.height; y+=50) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(canvas.width,y); ctx.stroke(); }

    // 아이템 렌더링
    items.forEach(item => {
        ctx.fillStyle = item.type === 'hp' ? '#ff7675' : '#74b9ff';
        ctx.beginPath(); ctx.arc(item.x, item.y, 6, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.5; ctx.stroke();
    });

    // 플레이어 렌더링
    ctx.fillStyle = player.classType === 'Warrior' ? '#ff7675' : (player.classType === 'Mage' ? '#a29bfe' : '#55efc4');
    ctx.beginPath(); ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = player.isDashing ? '#66fcf1' : '#ffffff';
    ctx.lineWidth = 2.5; ctx.stroke();

    // 조준 선
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(player.x, player.y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke();

    // 투사체 렌더링
    projectiles.forEach(p => {
        ctx.fillStyle = p.color;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2); ctx.fill();
    });

    // 적 렌더링
    enemies.forEach(e => {
        ctx.fillStyle = e.color;
        ctx.beginPath(); ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2); ctx.fill();
        
        // 체력바
        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.fillRect(e.x - 20, e.y - e.radius - 12, 40, 5);
        ctx.fillStyle = '#ff7675';
        ctx.fillRect(e.x - 20, e.y - e.radius - 12, (e.hp / e.maxHp) * 40, 5);
    });

    // 이펙트 파티클
    particles.forEach(pt => {
        ctx.fillStyle = pt.color;
        ctx.globalAlpha = pt.life;
        ctx.beginPath(); ctx.arc(pt.x, pt.y, 3, 0, Math.PI * 2); ctx.fill();
        ctx.globalAlpha = 1.0;
    });
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

# 3. 충분한 높이로 컴포넌트 임베딩
components.html(game_html, height=700)
