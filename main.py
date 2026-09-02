import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Jujutsu Kaisen Game", layout="wide")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Jujutsu Kaisen Battle</title>
    <style>
        body {
            margin: 0;
            background-color: #05050a;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
            user-select: none;
        }
        #ui-container {
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            pointer-events: none;
            z-index: 10;
        }
        .status-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .bar-container {
            width: 220px;
            height: 18px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 9px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        #hp-bar {
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #ff4757, #ff6b81);
            transition: width 0.1s linear;
        }
        #ult-bar {
            width: 0%;
            height: 100%;
            background: linear-gradient(90deg, #3742fa, #70a1ff);
            transition: width 0.1s linear;
        }
        .label {
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        #kill-counter {
            background: rgba(0, 0, 0, 0.6);
            padding: 10px 15px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: right;
        }
        #kill-status {
            font-size: 14px;
            font-weight: bold;
            color: #f1c40f;
        }
        canvas {
            display: block;
        }
    </style>
</head>
<body>

<div id="ui-container">
    <div class="status-group">
        <div>
            <div class="label">HP</div>
            <div class="bar-container"><div id="hp-bar"></div></div>
        </div>
        <div>
            <div class="label">Ultimate Energy</div>
            <div class="bar-container"><div id="ult-bar"></div></div>
        </div>
    </div>
    <div id="kill-counter">
        <div class="label">Monster Kills</div>
        <div id="kill-status">처치한 몬스터: 0 마리</div>
    </div>
</div>

<canvas id="gameCanvas"></canvas>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);
resize();

const WORLD_WIDTH = 3000;
const WORLD_HEIGHT = 3000;

let player = {
    x: WORLD_WIDTH / 2,
    y: WORLD_HEIGHT / 2,
    hp: 100,
    maxHp: 100,
    ultEnergy: 0,
    maxUlt: 100,
    speed: 5,
    charType: 'Gojo'
};

let camera = { x: 0, y: 0 };
let keys = {};
let mouse = { x: 0, y: 0, worldX: 0, worldY: 0, down: false };
let enemies = [];
let projectiles = [];
let purpleProjectiles = [];
let explosions = [];
let purpleEffects = [];
let blackHoles = [];
let blueOrbs = [];
let activeDomain = null;
let limitlessActive = false;
let screenShake = 0;
let isGameOver = false;

// 몬스터 처치 수 카운트 변수
let normalKillCount = 0;

window.addEventListener('keydown', e => keys[e.key.toLowerCase()] = true);
window.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

window.addEventListener('mousemove', e => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
    mouse.worldX = camera.x + mouse.x;
    mouse.worldY = camera.y + mouse.y;
});

window.addEventListener('mousedown', () => {
    mouse.down = true;
    useBasicAttack();
});
window.addEventListener('mouseup', () => mouse.down = false);

window.addEventListener('keydown', e => {
    if(e.key === 'q' || e.key === 'Q') useAka();
    if(e.key === 'e' || e.key === 'E') useMurasaki();
    if(e.key === 'r' || e.key === 'R') useDomain();
});

function triggerVibration(intensity) {
    screenShake = intensity;
}

function addUlt(amount) {
    // 궁 게이지 상승량을 기존보다 낮게 수정 (조절값: 0.3 곱하기)
    player.ultEnergy = Math.min(player.maxUlt, player.ultEnergy + amount * 0.3);
}

function takeDamage(amount) {
    player.hp -= amount;
    triggerVibration(10);
    if(player.hp <= 0) {
        isGameOver = true;
        alert('Game Over');
        location.reload();
    }
}

// 스킬 구현
function useBasicAttack() {
    let angle = Math.atan2(mouse.worldY - player.y, mouse.worldX - player.x);
    projectiles.push({
        x: player.x, y: player.y,
        vx: Math.cos(angle) * 12,
        vy: Math.sin(angle) * 12,
        radius: 6, damage: 15, color: '#00d2ff', type: 'normal'
    });
}

function useAka() {
    let angle = Math.atan2(mouse.worldY - player.y, mouse.worldX - player.x);
    projectiles.push({
        x: player.x, y: player.y,
        targetX: mouse.worldX, targetY: mouse.worldY,
        vx: Math.cos(angle) * 10, vy: Math.sin(angle) * 10,
        radius: 12, damage: 50, color: '#ff4757', type: 'aka'
    });
}

function useMurasaki() {
    let angle = Math.atan2(mouse.worldY - player.y, mouse.worldX - player.x);
    purpleProjectiles.push({
        x: player.x, y: player.y,
        vx: Math.cos(angle) * 8, vy: Math.sin(angle) * 8,
        radius: 25, damage: 150, life: 180
    });
}

function useDomain() {
    if(player.ultEnergy < player.maxUlt) return;
    player.ultEnergy = 0;
    activeDomain = { type: player.charType, timer: 300 };
    triggerVibration(30);
}

// 몬스터 스폰 (주기적)
function spawnEnemy() {
    if(enemies.length < 30) {
        let angle = Math.random() * Math.PI * 2;
        let dist = 800 + Math.random() * 400;
        enemies.push({
            x: player.x + Math.cos(angle) * dist,
            y: player.y + Math.sin(angle) * dist,
            radius: 14, hp: 30, maxHp: 30, speed: 2, damage: 10,
            color: '#a55eea', isBoss: false, spikes: 6
        });
    }
}
setInterval(spawnEnemy, 1000);

function update() {
    if(isGameOver) return;

    if(screenShake > 0) screenShake *= 0.9;

    // 플레이어 이동
    let dx = 0, dy = 0;
    if(keys['w'] || keys['ㅈ']) dy -= 1;
    if(keys['s'] || keys['ㄴ']) dy += 1;
    if(keys['a'] || keys['ㅁ']) dx -= 1;
    if(keys['d'] || keys['ㅇ']) dx += 1;

    if(dx !== 0 && dy !== 0) {
        dx *= 0.7071; dy *= 0.7071;
    }
    player.x += dx * player.speed;
    player.y += dy * player.speed;

    // 맵 경계 제한
    player.x = Math.max(20, Math.min(WORLD_WIDTH - 20, player.x));
    player.y = Math.max(20, Math.min(WORLD_HEIGHT - 20, player.y));

    camera.x = player.x - canvas.width / 2;
    camera.y = player.y - canvas.height / 2;

    if(activeDomain) {
        activeDomain.timer--;
        if(activeDomain.timer <= 0) activeDomain = null;
    }

    // 무라사키 관통 투사체 업데이트
    purpleProjectiles.forEach((pp, ppi) => {
        pp.x += pp.vx;
        pp.y += pp.vy;
        pp.life--;

        enemies.forEach((e, ei) => {
            if(Math.hypot(e.x - pp.x, e.y - pp.y) < e.radius + pp.radius) {
                e.hp -= pp.damage;
            }
        });

        if(pp.life <= 0) {
            purpleProjectiles.splice(ppi, 1);
        }
    });

    // 일반 및 아카 투사체 업데이트
    projectiles.forEach((p, pi) => {
        p.x += p.vx;
        p.y += p.vy;

        if(p.type === 'aka') {
            let reachedTarget = Math.hypot(p.targetX - p.x, p.targetY - p.y) < 15;
            let hitEnemy = false;
            enemies.forEach(e => {
                if(Math.hypot(e.x - p.x, e.y - p.y) < e.radius + p.radius) hitEnemy = true;
            });

            if(reachedTarget || hitEnemy) {
                explosions.push({
                    x: p.x, y: p.y, radius: 20, maxRadius: 160, color: '#ff4757', life: 20, damage: p.damage
                });
                triggerVibration(20);
                enemies.forEach(e => {
                    if(Math.hypot(e.x - p.x, e.y - p.y) < 160) {
                        e.hp -= p.damage;
                    }
                });
                projectiles.splice(pi, 1);
                return;
            }
        }

        enemies.forEach((e, ei) => {
            if(p.type !== 'aka' && Math.hypot(e.x - p.x, e.y - p.y) < e.radius + p.radius) {
                e.hp -= p.damage;
                projectiles.splice(pi, 1);
            }
        });

        if(p.x < 0 || p.x > WORLD_WIDTH || p.y < 0 || p.y > WORLD_HEIGHT) {
            projectiles.splice(pi, 1);
        }
    });

    // 적 업데이트
    enemies.forEach((e, ei) => {
        let ang = Math.atan2(player.y - e.y, player.x - e.x);
        e.x += Math.cos(ang) * e.speed;
        e.y += Math.sin(ang) * e.speed;

        let distToPlayer = Math.hypot(player.x - e.x, player.y - e.y);
        if(distToPlayer < e.radius + 15) {
            takeDamage(e.damage * 0.1);
        }

        if(e.hp <= 0) {
            enemies.splice(ei, 1);
            normalKillCount++;
            document.getElementById('kill-status').innerText = `처치한 몬스터: ${normalKillCount} 마리`;
            addUlt(6); // 처치 시 궁 게이지 소량 상승
        }
    });

    explosions.forEach((exp, exi) => {
        exp.radius += (exp.maxRadius - exp.radius) * 0.2;
        exp.life--;
        if(exp.life <= 0) explosions.splice(exi, 1);
    });
}

function draw() {
    ctx.fillStyle = '#05050a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.save();
    let renderX = -camera.x + (Math.random() - 0.5) * screenShake;
    let renderY = -camera.y + (Math.random() - 0.5) * screenShake;
    ctx.translate(renderX, renderY);

    // 격자 배경
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
    ctx.lineWidth = 1;
    let gridSize = 120;
    for(let x=0; x<=WORLD_WIDTH; x+=gridSize) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, WORLD_HEIGHT); ctx.stroke();
    }
    for(let y=0; y<=WORLD_HEIGHT; y+=gridSize) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(WORLD_WIDTH, y); ctx.stroke();
    }

    if(activeDomain) {
        ctx.fillStyle = 'rgba(112, 161, 255, 0.12)';
        ctx.beginPath();
        ctx.arc(player.x, player.y, 900, 0, Math.PI * 2);
        ctx.fill();
    }

    // 적 렌더링
    enemies.forEach(e => {
        ctx.fillStyle = e.color;
        ctx.beginPath();
        ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2);
        ctx.fill();
    });

    // 무라사키 관통 투사체 렌더링
    purpleProjectiles.forEach(pp => {
        ctx.fillStyle = '#a855f7';
        ctx.beginPath(); ctx.arc(pp.x, pp.y, pp.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#e056fd'; ctx.lineWidth = 4; ctx.stroke();
    });

    // 일반/아카 투사체 렌더링
    projectiles.forEach(p => {
        ctx.fillStyle = p.color || '#00d2ff';
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
    });

    // 폭발 효과 렌더링
    explosions.forEach(exp => {
        ctx.fillStyle = exp.color;
        ctx.beginPath(); ctx.arc(exp.x, exp.y, exp.radius, 0, Math.PI*2); ctx.fill();
    });

    // 플레이어 렌더링
    ctx.fillStyle = '#70a1ff';
    ctx.beginPath(); ctx.arc(player.x, player.y, 18, 0, Math.PI * 2); ctx.fill();

    ctx.restore();

    document.getElementById('hp-bar').style.width = Math.max(0, (player.hp / player.maxHp * 100)) + '%';
    document.getElementById('ult-bar').style.width = (player.ultEnergy / player.maxUlt * 100) + '%';
}

function gameLoop() {
    update();
    draw();
    if(!isGameOver) requestAnimationFrame(gameLoop);
}
gameLoop();
</script>
</body>
</html>
"""

components.html(game_html, height=800, scrolling=False)
