import streamlit as st
import streamlit.components.v1 as components

# 1. Full-Width Layout CSS
st.markdown("""
    <style>
        .main .block-container {
            max-width: 100% !important;
            padding: 0.5rem 1rem !important;
        }
        iframe { width: 100% !important; border: none; }
    </style>
""", unsafe_allow_html=True)

st.title("☯️ 기가 수행평가: 주술회전 X 영역전개 서바이버")
st.caption("🎮 이동: WASD / 방향키 | 무적 대시: SPACEBAR | 영역 전개(특수기): automatic")

# 2. 주술회전 그래픽 & 액션 게임 엔진
game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background-color: #030305;
        color: #fff;
        font-family: 'Consolas', monospace;
        display: flex; justify-content: center; align-items: center;
        width: 100vw; height: 100vh; overflow: hidden;
    }
    #game-container {
        position: relative;
        width: 1400px; height: 750px;
        border: 2px solid #9b59b6;
        border-radius: 12px;
        box-shadow: 0 0 40px rgba(155, 89, 182, 0.4);
        overflow: hidden;
        background: #08080f;
    }
    canvas { display: block; background: #05050a; }
    #ui-layer {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; padding: 20px;
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .hud-top { display: flex; justify-content: space-between; align-items: flex-start; }
    .bar-box {
        width: 340px; background: rgba(5, 5, 10, 0.85);
        padding: 12px; border-radius: 8px; border: 1px solid #9b59b6;
    }
    .bar-outer {
        width: 100%; height: 12px; background: #1a1a24;
        border-radius: 6px; overflow: hidden; margin-top: 4px; margin-bottom: 8px;
    }
    .bar-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #e74c3c, #ff7675); transition: width 0.1s; }
    .bar-curse { width: 0%; height: 100%; background: linear-gradient(90deg, #a29bfe, #6c5ce7); transition: width 0.1s; }
    
    #class-select {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(3, 3, 5, 0.95);
        display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        z-index: 100;
    }
    .card-group { display: flex; gap: 30px; margin-top: 30px; }
    .card {
        background: #0f0f18; border: 2px solid #9b59b6;
        border-radius: 12px; padding: 25px; width: 280px;
        text-align: center; cursor: pointer; transition: 0.3s;
    }
    .card:hover { transform: translateY(-10px); box-shadow: 0 0 30px #9b59b6; }
    .card h2 { color: #a29bfe; margin-bottom: 10px; font-size: 24px; }
    .card p { font-size: 13px; color: #aaa; line-height: 1.5; }
</style>
</head>
<body>

<div id="game-container">
    <canvas id="gameCanvas" width="1400" height="750"></canvas>
    
    <div id="ui-layer">
        <div class="hud-top">
            <div class="bar-box">
                <div style="font-size:11px; color:#aaa;">주력 체력 (HP)</div>
                <div class="bar-outer"><div id="hp-bar" class="bar-hp"></div></div>
                <div style="font-size:11px; color:#aaa;">주력 게이지 (EXP)</div>
                <div class="bar-outer"><div id="exp-bar" class="bar-curse"></div></div>
                <div id="level-txt" style="color:#a29bfe; font-weight:bold; font-size:14px;">주술사 등급</div>
            </div>
            <div style="text-align:right; background:rgba(5,5,10,0.85); padding:10px 20px; border-radius:8px; border:1px solid #a29bfe;">
                <div id="domain-txt" style="font-size:20px; font-weight:bold; color:#a29bfe;">영역 전개 대기 중</div>
                <div id="kill-txt" style="font-size:12px; color:#aaa;">퇴치한 주령: 0</div>
            </div>
        </div>
    </div>

    <div id="class-select">
        <h1 style="color:#a29bfe; font-size:40px; text-shadow:0 0 15px #9b59b6;">주술사 캐릭터 선택</h1>
        <p style="color:#aaa; margin-top:8px;">자신의 주령 술식을 사용해 주령들을 퇴치하세요.</p>
        <div class="card-group">
            <div class="card" onclick="selectChar('Yuji')">
                <h2>👊 이타도리 유우지</h2>
                <p><strong>술식: 경정권 & 흑섬</strong><br>근접 전투 특화. 일정 확률로 강력한 크리티컬 흑섬 폭발 발동</p>
            </div>
            <div class="card" onclick="selectChar('Gojo')">
                <h2>👁️ 고죠 사토루</h2>
                <p><strong>술식: 무하한 & 허식 「무라사키」</strong><br>자동 유도 술식 사격 및 대형 관통 구체 발사</p>
            </div>
        </div>
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let killCount = 0;
let gameOver = false;
let screenShake = 0;
let domainActive = false;
let domainTimer = 0;

let player = {
    x: 700, y: 375, width: 32, height: 40,
    hp: 150, maxHp: 150, exp: 0, maxExp: 40, level: 1,
    speed: 4.5, dashCd: 0, isDashing: false,
    charType: 'Yuji'
};

let keys = {};
let projectiles = [];
let enemies = [];
let particles = [];
let floatTexts = [];

window.addEventListener('keydown', e => keys[e.key.toLowerCase()] = true);
window.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

function selectChar(type) {
    player.charType = type;
    if(type === 'Gojo') { player.hp = player.maxHp = 120; player.speed = 4.8; }
    document.getElementById('class-select').style.display = 'none';
    gameLoop();
}

// 픽셀 캐릭터 드로잉 (동그라미 대신 사람 모양 캐릭터)
function drawPlayerSprite(x, y, type) {
    ctx.save();
    ctx.translate(x, y);

    if(type === 'Yuji') {
        // 유우지 (분홍 머리 + 주술고전 유니폼)
        ctx.fillStyle = '#11111a'; // 몸통
        ctx.fillRect(-10, -5, 20, 25);
        ctx.fillStyle = '#e74c3c'; // 후드 후드집업
        ctx.fillRect(-8, -8, 16, 6);
        ctx.fillStyle = '#ffb8b8'; // 얼굴
        ctx.fillRect(-8, -20, 16, 12);
        ctx.fillStyle = '#ff7675'; // 머리카락
        ctx.fillRect(-10, -25, 20, 8);
    } else {
        // 고죠 사토루 (백발 + 안대 + 검은 코트)
        ctx.fillStyle = '#0f0f15'; // 몸통 코트
        ctx.fillRect(-10, -5, 20, 25);
        ctx.fillStyle = '#222'; // 안대
        ctx.fillRect(-8, -16, 16, 5);
        ctx.fillStyle = '#ffb8b8'; // 얼굴
        ctx.fillRect(-8, -20, 16, 12);
        ctx.fillStyle = '#ffffff'; // 은발/백발
        ctx.fillRect(-10, -26, 20, 8);
    }

    ctx.restore();
}

// 주령(적) 픽셀 아트 드로잉
function drawCurseEnemy(x, y, radius, isElite) {
    ctx.save();
    ctx.translate(x, y);

    ctx.fillStyle = isElite ? '#8e44ad' : '#27ae60';
    let s = radius;
    // 기형적인 주령 형태
    ctx.beginPath();
    ctx.moveTo(-s, -s);
    ctx.lineTo(s, -s/2);
    ctx.lineTo(s/2, s);
    ctx.lineTo(-s/2, s);
    ctx.closePath();
    ctx.fill();

    // 붉은 눈동자
    ctx.fillStyle = '#ff0055';
    ctx.fillRect(-s/3, -s/3, 4, 4);
    if(isElite) ctx.fillRect(s/4, -s/3, 4, 4);

    ctx.restore();
}

function spawnCurse() {
    if(gameOver) return;
    let margin = 50;
    let x = Math.random() < 0.5 ? margin : canvas.width - margin;
    let y = Math.random() * (canvas.height - margin * 2) + margin;

    let isElite = Math.random() < 0.12;
    enemies.push({
        x: x, y: y,
        radius: isElite ? 20 : 12,
        hp: isElite ? 180 : 30 + killCount * 0.5,
        maxHp: isElite ? 180 : 30 + killCount * 0.5,
        speed: isElite ? 1.6 : 2.2 + Math.random(),
        isElite: isElite
    });
}

let attackTimer = 0;
function autoSkill() {
    if(enemies.length === 0) return;

    if(player.charType === 'Yuji') {
        // 경정권 / 흑섬 공격
        let nearest = null; let minDist = 9999;
        enemies.forEach(e => {
            let d = Math.hypot(e.x - player.x, e.y - player.y);
            if(d < minDist) { minDist = d; nearest = e; }
        });

        if(nearest && minDist < 180) {
            let isBlackFlash = Math.random() < 0.25; // 25% 확률 흑섬
            let ang = Math.atan2(nearest.y - player.y, nearest.x - player.x);
            projectiles.push({
                x: player.x, y: player.y,
                vx: Math.cos(ang) * 14, vy: Math.sin(ang) * 14,
                damage: isBlackFlash ? 120 : 35,
                radius: isBlackFlash ? 16 : 8,
                color: isBlackFlash ? '#000000' : '#e74c3c',
                isBlackFlash: isBlackFlash
            });
            if(isBlackFlash) screenShake = 8;
        }
    } else {
        // 고죠: 무하한/무라사키
        let nearest = null; let minDist = 9999;
        enemies.forEach(e => {
            let d = Math.hypot(e.x - player.x, e.y - player.y);
            if(d < minDist) { minDist = d; nearest = e; }
        });

        if(nearest) {
            let ang = Math.atan2(nearest.y - player.y, nearest.x - player.x);
            projectiles.push({
                x: player.x, y: player.y,
                vx: Math.cos(ang) * 10, vy: Math.sin(ang) * 10,
                damage: 40, radius: 7, color: '#a29bfe'
            });
        }
    }
}

function update() {
    if(gameOver) return;

    if(player.dashCd > 0) player.dashCd--;
    if(screenShake > 0) screenShake--;

    // 대시
    if(keys[' '] && player.dashCd === 0) {
        player.isDashing = true; player.dashCd = 45;
        setTimeout(() => player.isDashing = false, 150);
    }

    // 이동
    let spd = player.isDashing ? player.speed * 2.4 : player.speed;
    if(keys['a'] || keys['arrowleft']) player.x = Math.max(20, player.x - spd);
    if(keys['d'] || keys['arrowright']) player.x = Math.min(canvas.width - 20, player.x + spd);
    if(keys['w'] || keys['arrowup']) player.y = Math.max(20, player.y - spd);
    if(keys['s'] || keys['arrowdown']) player.y = Math.min(canvas.height - 20, player.y + spd);

    attackTimer++;
    if(attackTimer > 18) { autoSkill(); attackTimer = 0; }

    if(Math.random() < 0.08) spawnCurse();

    // 영역 전개 활성화 체크 (레벨 5 달성 시)
    if(player.level >= 5 && !domainActive) {
        domainActive = true;
        domainTimer = 300; // 300 프레임 동안 영역 전개
    }

    if(domainActive) {
        domainTimer--;
        if(domainTimer <= 0) { domainActive = false; }
    }

    // 투사체 처리
    projectiles.forEach((p, pi) => {
        p.x += p.vx; p.y += p.vy;

        enemies.forEach((e, ei) => {
            let d = Math.hypot(e.x - p.x, e.y - p.y);
            if(d < e.radius + p.radius) {
                e.hp -= p.damage;
                projectiles.splice(pi, 1);

                if(e.hp <= 0) {
                    killCount++;
                    player.exp += e.isElite ? 35 : 12;
                    enemies.splice(ei, 1);

                    if(player.exp >= player.maxExp) {
                        player.level++;
                        player.exp -= player.maxExp;
                        player.maxExp = Math.floor(player.maxExp * 1.3);
                        player.hp = player.maxHp;
                    }
                }
            }
        });
    });

    // 적 이동 및 충돌
    enemies.forEach(e => {
        let ang = Math.atan2(player.y - e.y, player.x - e.x);
        let currentSpeed = domainActive ? e.speed * 0.2 : e.speed; // 영역 전개 시 적 속도 격감
        e.x += Math.cos(ang) * currentSpeed;
        e.y += Math.sin(ang) * currentSpeed;

        let d = Math.hypot(player.x - e.x, player.y - e.y);
        if(d < e.radius + 15 && !player.isDashing) {
            player.hp -= 0.4;
            if(player.hp <= 0) {
                alert(`퇴치 실패! 최종 등급: Lv.${player.level} | 퇴치한 주령: ${killCount}마리`);
                location.reload();
            }
        }
    });

    // UI
    document.getElementById('hp-bar').style.width = Math.max(0, (player.hp / player.maxHp * 100)) + '%';
    document.getElementById('exp-bar').style.width = Math.min(100, (player.exp / player.maxExp * 100)) + '%';
    document.getElementById('level-txt').innerText = `Lv.${player.level} ${player.charType === 'Yuji' ? '이타도리' : '고죠'}`;
    document.getElementById('domain-txt').innerText = domainActive ? '☯️ 영역 전개 중!' : '영역 전개 준비 중';
    document.getElementById('kill-txt').innerText = `퇴치한 주령: ${killCount}`;
}

function draw() {
    ctx.save();
    if(screenShake > 0) ctx.translate((Math.random()-0.5)*screenShake, (Math.random()-0.5)*screenShake);

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 영역 전개 백그라운드 연출
    if(domainActive) {
        ctx.fillStyle = 'rgba(108, 92, 231, 0.15)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    // 격자 배경
    ctx.strokeStyle = 'rgba(155, 89, 182, 0.08)';
    for(let x=0; x<canvas.width; x+=60) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,canvas.height); ctx.stroke(); }
    for(let y=0; y<canvas.height; y+=60) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(canvas.width,y); ctx.stroke(); }

    // 캐릭터 그리기
    drawPlayerSprite(player.x, player.y, player.charType);

    // 적 그리기
    enemies.forEach(e => drawCurseEnemy(e.x, e.y, e.radius, e.isElite));

    // 투사체
    projectiles.forEach(p => {
        ctx.fillStyle = p.color;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2); ctx.fill();
        if(p.isBlackFlash) {
            ctx.strokeStyle = '#e74c3c'; ctx.lineWidth = 3; ctx.stroke();
        }
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

components.html(game_html, height=780)
