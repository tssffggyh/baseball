import streamlit as st
import streamlit.components.v1 as components

# 제목 출력
st.title("⚔️ 기가 수행평가: 웹 파이썬 2D 던전 크롤러")
st.caption("Streamlit 클라우드 환경 완벽 지원 | 방향키/WASD: 이동 | 마우스: 공격/스킬")

# HTML5/JS 기반 게임 임베딩 코드
game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
    body {
        background-color: #0d0f12;
        color: white;
        font-family: 'Courier New', Courier, monospace;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0;
        padding: 10px;
    }
    #game-container {
        position: relative;
        box-shadow: 0 0 20px rgba(0,255,200,0.2);
        border-radius: 10px;
        overflow: hidden;
    }
    canvas {
        background: #15181e;
        display: block;
    }
    #ui-overlay {
        position: absolute;
        top: 15px;
        left: 15px;
        color: #fff;
        font-size: 16px;
        font-weight: bold;
        text-shadow: 2px 2px 4px #000;
        pointer-events: none;
    }
    .bar-bg {
        width: 200px;
        height: 16px;
        background: #333;
        border: 2px solid #fff;
        border-radius: 8px;
        margin-bottom: 5px;
        overflow: hidden;
    }
    .hp-bar { width: 100%; height: 100%; background: #e74c3c; transition: width 0.1s; }
    .exp-bar { width: 0%; height: 100%; background: #2ecc71; transition: width 0.1s; }
    #class-select {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(13, 15, 18, 0.95);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 10;
    }
    .btn {
        background: #2980b9;
        color: white;
        border: none;
        padding: 12px 24px;
        margin: 10px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        cursor: pointer;
        transition: 0.2s;
        width: 250px;
    }
    .btn:hover { background: #3498db; transform: scale(1.05); }
</style>
</head>
<body>

<div id="game-container">
    <canvas id="gameCanvas" width="900" height="550"></canvas>
    
    <div id="ui-overlay">
        <div>HP</div>
        <div class="bar-bg"><div id="hp" class="hp-bar"></div></div>
        <div>EXP</div>
        <div class="bar-bg"><div id="exp" class="exp-bar"></div></div>
        <div id="stats" style="margin-top: 5px; color: #f1c40f;">Lv.1 전사 | 층수: B1F</div>
    </div>

    <div id="class-select">
        <h1 style="color: #f1c40f;">⚔️ 캐릭터 직업 선택</h1>
        <p>기가 수행평가 프로젝트 - 웹 던전 RPG</p>
        <button class="btn" onclick="startGame('Warrior')">🛡️ 전사 (높은 체력)</button>
        <button class="btn" onclick="startGame('Mage')" style="background:#8e44ad;">🔮 마법사 (원거리 폭딜)</button>
        <button class="btn" onclick="startGame('Ranger')" style="background:#27ae60;">🏹 궁수 (빠른 이동)</button>
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let gameState = 'MENU';
let player = { x: 450, y: 275, size: 20, hp: 100, maxHp: 100, exp: 0, maxExp: 50, level: 1, speed: 4, class: 'Warrior' };
let dungeonLevel = 1;
let keys = {};
let mouse = { x: 0, y: 0, down: false, rightDown: false };
let bullets = [];
let enemies = [];
let particles = [];

window.addEventListener('keydown', e => keys[e.key.toLowerCase()] = true);
window.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);
canvas.addEventListener('mousemove', e => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
});
canvas.addEventListener('mousedown', e => {
    if(e.button === 0) mouse.down = true;
    if(e.button === 2) { mouse.rightDown = true; e.preventDefault(); }
});
canvas.addEventListener('mouseup', e => {
    if(e.button === 0) mouse.down = false;
    if(e.button === 2) mouse.rightDown = false;
});
canvas.addEventListener('contextmenu', e => e.preventDefault());

function startGame(className) {
    player.class = className;
    if(className === 'Warrior') { player.hp = player.maxHp = 150; player.speed = 3.5; }
    if(className === 'Mage') { player.hp = player.maxHp = 80; player.speed = 4.0; }
    if(className === 'Ranger') { player.hp = player.maxHp = 100; player.speed = 5.0; }
    
    document.getElementById('class-select').style.display = 'none';
    gameState = 'PLAYING';
    spawnEnemies();
    gameLoop();
}

function spawnEnemies() {
    enemies = [];
    let count = 4 + dungeonLevel * 2;
    for(let i=0; i<count; i++) {
        enemies.push({
            x: Math.random() * (canvas.width - 100) + 50,
            y: Math.random() * (canvas.height - 100) + 50,
            size: 18,
            hp: 30 + dungeonLevel * 10,
            maxHp: 30 + dungeonLevel * 10,
            speed: 1.5 + Math.random(),
            color: '#e74c3c'
        });
    }
}

let lastShoot = 0;
function shoot() {
    let now = Date.now();
    if(now - lastShoot < (player.class === 'Ranger' ? 200 : 350)) return;
    lastShoot = now;

    let angle = Math.atan2(mouse.y - player.y, mouse.x - player.x);
    bullets.push({
        x: player.x, y: player.y,
        vx: Math.cos(angle) * 8, vy: Math.sin(angle) * 8,
        damage: player.class === 'Mage' ? 35 : 20,
        color: player.class === 'Mage' ? '#9b59b6' : '#f1c40f',
        radius: player.class === 'Mage' ? 8 : 5
    });
}

function update() {
    if(gameState !== 'PLAYING') return;

    if(keys['a'] || keys['arrowleft']) player.x = Math.max(player.size, player.x - player.speed);
    if(keys['d'] || keys['arrowright']) player.x = Math.min(canvas.width - player.size, player.x + player.speed);
    if(keys['w'] || keys['arrowup']) player.y = Math.max(player.size, player.y - player.speed);
    if(keys['s'] || keys['arrowdown']) player.y = Math.min(canvas.height - player.size, player.y + player.speed);

    if(mouse.down) shoot();

    bullets.forEach((b, bi) => {
        b.x += b.vx; b.y += b.vy;
        enemies.forEach((e, ei) => {
            let dist = Math.hypot(e.x - b.x, e.y - b.y);
            if(dist < e.size + b.radius) {
                e.hp -= b.damage;
                createParticles(b.x, b.y, b.color);
                bullets.splice(bi, 1);
                if(e.hp <= 0) {
                    player.exp += 20;
                    enemies.splice(ei, 1);
                    if(player.exp >= player.maxExp) {
                        player.level++;
                        player.exp -= player.maxExp;
                        player.maxExp = Math.floor(player.maxExp * 1.3);
                        player.maxHp += 15;
                        player.hp = player.maxHp;
                    }
                }
            }
        });
    });

    enemies.forEach(e => {
        let angle = Math.atan2(player.y - e.y, player.x - e.x);
        e.x += Math.cos(angle) * e.speed;
        e.y += Math.sin(angle) * e.speed;

        let dist = Math.hypot(player.x - e.x, player.y - e.y);
        if(dist < player.size + e.size) {
            player.hp -= 0.5;
            if(player.hp <= 0) {
                alert("게임 오버! B" + dungeonLevel + "F 에서 전사했습니다.");
                location.reload();
            }
        }
    });

    if(enemies.length === 0) {
        dungeonLevel++;
        spawnEnemies();
    }

    particles.forEach((p, i) => {
        p.x += p.vx; p.y += p.vy; p.life -= 0.05;
        if(p.life <= 0) particles.splice(i, 1);
    });

    document.getElementById('hp').style.width = Math.max(0, (player.hp / player.maxHp * 100)) + '%';
    document.getElementById('exp').style.width = Math.min(100, (player.exp / player.maxExp * 100)) + '%';
    document.getElementById('stats').innerText = `Lv.${player.level} ${player.class} | 층수: B${dungeonLevel}F`;
}

function createParticles(x, y, color) {
    for(let i=0; i<6; i++) {
        particles.push({
            x: x, y: y,
            vx: (Math.random() - 0.5) * 4,
            vy: (Math.random() - 0.5) * 4,
            color: color, life: 1.0
        });
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = '#1a1f26';
    ctx.lineWidth = 1;
    for(let x=0; x<canvas.width; x+=40) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,canvas.height); ctx.stroke(); }
    for(let y=0; y<canvas.height; y+=40) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(canvas.width,y); ctx.stroke(); }

    ctx.fillStyle = player.class === 'Warrior' ? '#3498db' : (player.class === 'Mage' ? '#9b59b6' : '#2ecc71');
    ctx.beginPath();
    ctx.arc(player.x, player.y, player.size, 0, Math.PI * 2);
    ctx.fill();

    bullets.forEach(b => {
        ctx.fillStyle = b.color;
        ctx.beginPath(); ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2); ctx.fill();
    });

    enemies.forEach(e => {
        ctx.fillStyle = e.color;
        ctx.beginPath(); ctx.arc(e.x, e.y, e.size, 0, Math.PI * 2); ctx.fill();
        
        ctx.fillStyle = '#c0392b';
        ctx.fillRect(e.x - 15, e.y - 25, 30, 4);
        ctx.fillStyle = '#2ecc71';
        ctx.fillRect(e.x - 15, e.y - 25, (e.hp / e.maxHp) * 30, 4);
    });

    particles.forEach(p => {
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.life;
        ctx.beginPath(); ctx.arc(p.x, p.y, 3, 0, Math.PI * 2); ctx.fill();
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

components.html(game_html, height=620)
