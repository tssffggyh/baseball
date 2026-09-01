import streamlit as st
import streamlit.components.v1 as components

# 1. Full-Width 화면 최적화
st.markdown("""
    <style>
        .main .block-container {
            max-width: 100% !important;
            padding: 0.5rem 1rem !important;
        }
        iframe { width: 100% !important; border: none; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ 기가 수행평가: 사이버 서바이버 (핵앤슬래시)")
st.caption("🎮 이동: WASD / 방향키 | 무기 자동 발사 | 무적 대시: SPACEBAR")

# 2. 게임 엔진
game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background-color: #050508;
        color: #fff;
        font-family: 'Consolas', monospace;
        display: flex; justify-content: center; align-items: center;
        width: 100vw; height: 100vh; overflow: hidden;
    }
    #game-container {
        position: relative;
        width: 1400px; height: 750px;
        border: 2px solid #ff0055;
        border-radius: 12px;
        box-shadow: 0 0 40px rgba(ff, 0, 85, 0.3);
        overflow: hidden;
        background: #0a0a10;
    }
    canvas { display: block; background: #07070c; }
    #ui-layer {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; padding: 20px;
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .hud-top { display: flex; justify-content: space-between; align-items: flex-start; }
    .bar-box {
        width: 320px; background: rgba(10, 10, 16, 0.85);
        padding: 12px; border-radius: 8px; border: 1px solid #ff0055;
    }
    .bar-outer {
        width: 100%; height: 12px; background: #1a1a24;
        border-radius: 6px; overflow: hidden; margin-top: 4px; margin-bottom: 8px;
    }
    .bar-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff0055, #ff5500); transition: width 0.1s; }
    .bar-exp { width: 0%; height: 100%; background: linear-gradient(90deg, #00f0ff, #7000ff); transition: width 0.1s; }
    
    #game-over-screen {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(5, 5, 8, 0.9);
        display: none; flex-direction: column;
        justify-content: center; align-items: center;
        z-index: 100;
    }
    .btn-restart {
        background: #ff0055; color: white; border: none;
        padding: 15px 35px; font-size: 18px; font-weight: bold;
        border-radius: 8px; cursor: pointer; margin-top: 20px;
        box-shadow: 0 0 15px #ff0055;
    }
</style>
</head>
<body>

<div id="game-container">
    <canvas id="gameCanvas" width="1400" height="750"></canvas>
    
    <div id="ui-layer">
        <div class="hud-top">
            <div class="bar-box">
                <div style="font-size:11px; color:#aaa;">HEALTH</div>
                <div class="bar-outer"><div id="hp-bar" class="bar-hp"></div></div>
                <div style="font-size:11px; color:#aaa;">EXP (NEXT LEVEL)</div>
                <div class="bar-outer"><div id="exp-bar" class="bar-exp"></div></div>
                <div id="level-txt" style="color:#00f0ff; font-weight:bold; font-size:14px;">Lv.1 사이버 닌자</div>
            </div>
            <div style="text-align:right; background:rgba(10,10,16,0.85); padding:10px 20px; border-radius:8px; border:1px solid #00f0ff;">
                <div id="time-txt" style="font-size:24px; font-weight:bold; color:#00f0ff;">00:00</div>
                <div id="kill-txt" style="font-size:12px; color:#aaa;">처치 수: 0</div>
            </div>
        </div>
    </div>

    <div id="game-over-screen">
        <h1 style="color:#ff0055; font-size:48px;">MISSION FAILED</h1>
        <p id="final-stats" style="color:#aaa; margin-top:10px; font-size:18px;"></p>
        <button class="btn-restart" onclick="location.reload()">다시 시작</button>
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let killCount = 0;
let survivalTime = 0;
let gameOver = false;
let screenShake = 0;

let player = {
    x: 700, y: 375, radius: 14,
    hp: 120, maxHp: 120, exp: 0, maxExp: 30, level: 1,
    speed: 4.5, dashCd: 0, isDashing: false,
    bladeAngle: 0
};

let keys = {};
let projectiles = [];
let enemies = [];
let particles = [];
let gems = [];
let floatTexts = [];

window.addEventListener('keydown', e => keys[e.key.toLowerCase()] = true);
window.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

// 타이머
setInterval(() => {
    if(!gameOver) {
        survivalTime++;
        let m = Math.floor(survivalTime / 60).toString().padStart(2, '0');
        let s = (survivalTime % 60).toString().padStart(2, '0');
        document.getElementById('time-txt').innerText = `${m}:${s}`;
    }
}, 1000);

// 안전한 영역 안에서 몬스터 스폰 (맵 밖 스폰 버그 해결)
function spawnEnemy() {
    if(gameOver) return;
    
    // 맵 테두리 내부에서 안전하게 스폰 (안쪽 여백 40px 확보)
    let margin = 40;
    let x, y;
    
    if(Math.random() < 0.5) {
        x = Math.random() < 0.5 ? margin : canvas.width - margin;
        y = Math.random() * (canvas.height - margin * 2) + margin;
    } else {
        x = Math.random() * (canvas.width - margin * 2) + margin;
        y = Math.random() < 0.5 ? margin : canvas.height - margin;
    }

    let isElite = Math.random() < 0.1;
    enemies.push({
        x: x, y: y,
        radius: isElite ? 22 : 12,
        hp: isElite ? 150 : 25 + Math.floor(survivalTime * 0.5),
        maxHp: isElite ? 150 : 25 + Math.floor(survivalTime * 0.5),
        speed: isElite ? 1.8 : 2.2 + Math.random() * 0.8,
        color: isElite ? '#ff0055' : '#7000ff',
        isElite: isElite
    });
}

// 자동 무기 발사 (가장 가까운 적 추적)
let autoAttackTimer = 0;
function autoShoot() {
    if(enemies.length === 0) return;

    // 가장 가까운 적 검색
    let nearest = null;
    let minDist = 99999;
    enemies.forEach(e => {
        let d = Math.hypot(e.x - player.x, e.y - player.y);
        if(d < minDist) { minDist = d; nearest = e; }
    });

    if(nearest && minDist < 600) {
        let ang = Math.atan2(nearest.y - player.y, nearest.x - player.x);
        projectiles.push({
            x: player.x, y: player.y,
            vx: Math.cos(ang) * 12, vy: Math.sin(ang) * 12,
            damage: 20 + player.level * 3, radius: 5, color: '#00f0ff'
        });
    }
}

function addParticles(x, y, color, count) {
    for(let i=0; i<count; i++) {
        particles.push({
            x: x, y: y,
            vx: (Math.random() - 0.5) * 6, vy: (Math.random() - 0.5) * 6,
            color: color, life: 1.0
        });
    }
}

function update() {
    if(gameOver) return;

    // 대시
    if(player.dashCd > 0) player.dashCd--;
    if(screenShake > 0) screenShake--;

    if(keys[' '] && player.dashCd === 0) {
        player.isDashing = true;
        player.dashCd = 50;
        screenShake = 4;
        setTimeout(() => player.isDashing = false, 150);
    }

    // 플레이어 이동
    let speed = player.isDashing ? player.speed * 2.5 : player.speed;
    let dx = 0, dy = 0;
    if(keys['a'] || keys['arrowleft']) dx -= 1;
    if(keys['d'] || keys['arrowright']) dx += 1;
    if(keys['w'] || keys['arrowup']) dy -= 1;
    if(keys['s'] || keys['arrowdown']) dy += 1;

    if(dx !== 0 && dy !== 0) { dx *= 0.7071; dy *= 0.7071; }
    player.x = Math.max(player.radius + 10, Math.min(canvas.width - player.radius - 10, player.x + dx * speed));
    player.y = Math.max(player.radius + 10, Math.min(canvas.height - player.radius - 10, player.y + dy * speed));

    // 회전 블레이드 각도
    player.bladeAngle += 0.08;

    // 자동 공격 쿨타임
    autoAttackTimer++;
    if(autoAttackTimer > Math.max(10, 25 - player.level)) {
        autoAttackTimer = 0;
        autoShoot();
    }

    // 주기적 스폰 (시간에 따라 점점 빨라짐)
    if(Math.random() < 0.05 + Math.min(0.1, survivalTime * 0.001)) {
        spawnEnemy();
    }

    // 회전 블레이드 충돌 판정
    let bladeX = player.x + Math.cos(player.bladeAngle) * 55;
    let bladeY = player.y + Math.sin(player.bladeAngle) * 55;

    enemies.forEach((e, ei) => {
        // 블레이드 타격
        let bDist = Math.hypot(e.x - bladeX, e.y - bladeY);
        if(bDist < e.radius + 12) {
            e.hp -= 2;
            addParticles(bladeX, bladeY, '#ff0055', 2);
        }

        // 이동 AI
        let ang = Math.atan2(player.y - e.y, player.x - e.x);
        e.x += Math.cos(ang) * e.speed;
        e.y += Math.sin(ang) * e.speed;

        // 플레이어 충돌
        let pDist = Math.hypot(player.x - e.x, player.y - e.y);
        if(pDist < player.radius + e.radius && !player.isDashing) {
            player.hp -= 0.5;
            screenShake = 3;
            if(player.hp <= 0) {
                gameOver = true;
                document.getElementById('final-stats').innerText = `생존 시간: ${survivalTime}초 | 처치 수: ${killCount}마리`;
                document.getElementById('game-over-screen').style.display = 'flex';
            }
        }
    });

    // 투사체 이동 & 충돌
    projectiles.forEach((p, pi) => {
        p.x += p.vx; p.y += p.vy;

        enemies.forEach((e, ei) => {
            let dist = Math.hypot(e.x - p.x, e.y - p.y);
            if(dist < e.radius + p.radius) {
                e.hp -= p.damage;
                addParticles(p.x, p.y, p.color, 4);
                projectiles.splice(pi, 1);

                if(e.hp <= 0) {
                    killCount++;
                    gems.push({ x: e.x, y: e.y, exp: e.isElite ? 40 : 10 });
                    addParticles(e.x, e.y, e.color, 8);
                    enemies.splice(ei, 1);
                }
            }
        });

        if(p.x < 0 || p.x > canvas.width || p.y < 0 || p.y > canvas.height) {
            projectiles.splice(pi, 1);
        }
    });

    // 경험치 보석 습득 (자동 끌림)
    gems.forEach((g, gi) => {
        let dist = Math.hypot(player.x - g.x, player.y - g.y);
        if(dist < 150) {
            let ang = Math.atan2(player.y - g.y, player.x - g.x);
            g.x += Math.cos(ang) * 8;
            g.y += Math.sin(ang) * 8;
        }
        if(dist < player.radius + 8) {
            player.exp += g.exp;
            gems.splice(gi, 1);

            // 레벨업
            if(player.exp >= player.maxExp) {
                player.level++;
                player.exp -= player.maxExp;
                player.maxExp = Math.floor(player.maxExp * 1.3);
                player.maxHp += 15;
                player.hp = player.maxHp;
                screenShake = 10;
                addParticles(player.x, player.y, '#00f0ff', 25);
            }
        }
    });

    // 파티클
    particles.forEach((pt, pti) => {
        pt.x += pt.vx; pt.y += pt.vy; pt.life -= 0.05;
        if(pt.life <= 0) particles.splice(pti, 1);
    });

    // UI
    document.getElementById('hp-bar').style.width = Math.max(0, (player.hp / player.maxHp * 100)) + '%';
    document.getElementById('exp-bar').style.width = Math.min(100, (player.exp / player.maxExp * 100)) + '%';
    document.getElementById('level-txt').innerText = `Lv.${player.level} 사이버 닌자`;
    document.getElementById('kill-txt').innerText = `처치 수: ${killCount}`;
}

function draw() {
    ctx.save();
    if(screenShake > 0) {
        ctx.translate((Math.random() - 0.5) * screenShake, (Math.random() - 0.5) * screenShake);
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 네온 그리드 배경
    ctx.strokeStyle = 'rgba(255, 0, 85, 0.05)';
    ctx.lineWidth = 1;
    for(let x=0; x<canvas.width; x+=50) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,canvas.height); ctx.stroke(); }
    for(let y=0; y<canvas.height; y+=50) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(canvas.width,y); ctx.stroke(); }

    // 경험치 보석
    gems.forEach(g => {
        ctx.fillStyle = '#00f0ff';
        ctx.beginPath(); ctx.arc(g.x, g.y, 4, 0, Math.PI * 2); ctx.fill();
    });

    // 플레이어
    ctx.fillStyle = '#00f0ff';
    ctx.beginPath(); ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = player.isDashing ? '#ffffff' : '#7000ff'; ctx.lineWidth = 3; ctx.stroke();

    // 회전 블레이드
    let bladeX = player.x + Math.cos(player.bladeAngle) * 55;
    let bladeY = player.y + Math.sin(player.bladeAngle) * 55;
    ctx.fillStyle = '#ff0055';
    ctx.beginPath(); ctx.arc(bladeX, bladeY, 8, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = 'rgba(255,0,85,0.3)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(player.x, player.y, 55, 0, Math.PI * 2); ctx.stroke();

    // 투사체
    projectiles.forEach(p => {
        ctx.fillStyle = p.color;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2); ctx.fill();
    });

    // 적
    enemies.forEach(e => {
        ctx.fillStyle = e.color;
        ctx.beginPath(); ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2); ctx.fill();
    });

    // 파티클
    particles.forEach(pt => {
        ctx.fillStyle = pt.color;
        ctx.globalAlpha = pt.life;
        ctx.beginPath(); ctx.arc(pt.x, pt.y, 2.5, 0, Math.PI * 2); ctx.fill();
        ctx.globalAlpha = 1.0;
    });

    ctx.restore();
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

gameLoop();
</script>
</body>
</html>
"""

components.html(game_html, height=780)
