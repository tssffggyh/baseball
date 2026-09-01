import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="주술회전: 무량처처")

st.markdown("""
    <style>
        .main .block-container {
            max-width: 100% !important;
            padding: 0rem !important;
        }
        iframe { width: 100% !important; border: none; }
        header { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background-color: #020204;
        color: #fff;
        font-family: 'Consolas', monospace;
        display: flex; justify-content: center; align-items: center;
        width: 100vw; height: 100vh; overflow: hidden;
    }
    #game-container {
        position: relative;
        width: 100vw; height: 100vh;
        overflow: hidden;
        background: #000;
    }
    canvas { display: block; }
    
    #ui-layer {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; padding: 25px;
        display: flex; flex-direction: column; justify-content: space-between;
        z-index: 10;
    }
    
    .hud-card {
        background: rgba(10, 10, 18, 0.75);
        backdrop-filter: blur(10px);
        padding: 15px 20px; border-radius: 12px;
        border: 1px solid rgba(155, 89, 182, 0.4);
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    }
    
    .bar-outer {
        width: 260px; height: 10px; background: rgba(255,255,255,0.1);
        border-radius: 5px; overflow: hidden; margin: 5px 0 10px 0;
    }
    .bar-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff4757, #ff6b81); transition: width 0.1s; }
    .bar-exp { width: 0%; height: 100%; background: linear-gradient(90deg, #70a1ff, #1e90ff); transition: width 0.1s; }
    
    #class-select {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(3, 3, 6, 0.92); backdrop-filter: blur(15px);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        z-index: 100;
    }
    .card-group { display: flex; gap: 40px; margin-top: 40px; }
    .card {
        background: rgba(20, 20, 35, 0.6);
        border: 2px solid rgba(168, 85, 247, 0.3);
        border-radius: 20px; padding: 35px 25px; width: 320px;
        text-align: center; cursor: pointer; transition: all 0.4s ease;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .card:hover {
        transform: translateY(-12px) scale(1.03);
        border-color: #a855f7;
        box-shadow: 0 20px 40px rgba(168, 85, 247, 0.4);
        background: rgba(30, 30, 50, 0.8);
    }
    .card h2 { color: #f3e8ff; margin-bottom: 12px; font-size: 26px; }
    .card p { font-size: 13px; color: #a1a1aa; line-height: 1.6; }
</style>
</head>
<body>

<div id="game-container">
    <canvas id="gameCanvas"></canvas>
    
    <div id="ui-layer">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div class="hud-card">
                <div id="char-name" style="color:#a855f7; font-weight:bold; font-size:16px; margin-bottom:4px;">주술사</div>
                <div style="font-size:10px; color:#aaa;">주력 체력 (HP)</div>
                <div class="bar-outer"><div id="hp-bar" class="bar-hp"></div></div>
                <div style="font-size:10px; color:#aaa;">주력 동기화율 (EXP)</div>
                <div class="bar-outer"><div id="exp-bar" class="bar-exp"></div></div>
            </div>
            
            <div class="hud-card" style="text-align:right;">
                <div id="domain-status" style="font-size:18px; font-weight:bold; color:#70a1ff;">영역 전개: 게이지 충전 중</div>
                <div id="kill-status" style="font-size:13px; color:#aaa; margin-top:4px;">제령한 특급 주령: 0</div>
            </div>
        </div>
    </div>

    <div id="class-select">
        <h1 style="color:#f3e8ff; font-size:48px; letter-spacing:2px; text-shadow:0 0 25px #a855f7;">JUJUTSU KAISEN</h1>
        <p style="color:#a1a1aa; margin-top:10px; font-size:16px;">주술사를 선택하여 대형 영역 내의 주령들을 퇴치하십시오.</p>
        <div class="card-group">
            <div class="card" onclick="selectChar('Gojo')">
                <h2 style="color:#70a1ff;">👁️ 고죠 사토루</h2>
                <p><strong>[특급 주술사]</strong><br><br>• 무하한 바리어로 피해 무효화<br>• 술식 반전 「아카」 자동 난사<br>• 궁극기: 영역 전개 <strong>「무량처처」</strong></p>
            </div>
            <div class="card" onclick="selectChar('Yuji')">
                <h2 style="color:#ff4757;">👊 이타도리 유우지</h2>
                <p><strong>[주인공 / 스쿠나의 그릇]</strong><br><br>• 압도적인 이동 속도 및 기동성<br>• 타격 시 칠흑의 불꽃 <strong>「흑섬」</strong> 발동<br>• 궁극기: 영역 전개 <strong>「복마어주자」</strong></p>
            </div>
        </div>
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// 메가 맵 크기 정의 (2400 x 1600)
const WORLD_WIDTH = 2400;
const WORLD_HEIGHT = 1600;

let killCount = 0;
let gameOver = false;
let screenShake = 0;
let domainActive = false;
let domainTimer = 0;

let camera = { x: 0, y: 0 };

let player = {
    x: WORLD_WIDTH / 2, y: WORLD_HEIGHT / 2,
    vx: 0, vy: 0,
    speed: 5.5, hp: 200, maxHp: 200, exp: 0, maxExp: 50, level: 1,
    charType: 'Gojo', dashCd: 0, isDashing: false, facing: 1
};

let keys = {};
let projectiles = [];
let enemies = [];
let particles = [];
let slicedEffects = [];

window.addEventListener('keydown', e => keys[e.key.toLowerCase()] = true);
window.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

function selectChar(type) {
    player.charType = type;
    document.getElementById('char-name').innerText = type === 'Gojo' ? '특급 주술사 : 고죠 사토루' : '숙주 : 이타도리 유우지';
    document.getElementById('class-select').style.display = 'none';
    
    // 시작 적 생성
    for(let i=0; i<30; i++) spawnCurse();
    gameLoop();
}

// 고품질 도트 스프라이트 렌더러
function drawPlayerSprite(p) {
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.scale(p.facing, 1);

    if(p.charType === 'Gojo') {
        // 고죠 무하한 쉴드 효과
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.4)';
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(0, -10, 24, 0, Math.PI*2); ctx.stroke();

        // 도복 (검은 긴 옷)
        ctx.fillStyle = '#0b0b12';
        ctx.fillRect(-8, -12, 16, 26);
        // 안대
        ctx.fillStyle = '#111';
        ctx.fillRect(-6, -22, 12, 4);
        // 피부
        ctx.fillStyle = '#ffdfc4';
        ctx.fillRect(-6, -18, 12, 6);
        // 은발 (풍성한 픽셀 헤어)
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(-8, -27, 16, 7);
        ctx.fillRect(-10, -24, 4, 6); ctx.fillRect(6, -24, 4, 6);
    } else {
        // 유우지 도복 (후드 집업 + 검은 주술고전 바지)
        ctx.fillStyle = '#0f1016';
        ctx.fillRect(-8, -6, 16, 20); // 바지
        ctx.fillStyle = '#ff4757';
        ctx.fillRect(-8, -14, 16, 10); // 붉은 후드
        // 피부
        ctx.fillStyle = '#ffd3b6';
        ctx.fillRect(-6, -20, 12, 7);
        // 분홍 가시 머리
        ctx.fillStyle = '#ff7675';
        ctx.fillRect(-8, -26, 16, 7);
        ctx.fillRect(-6, -28, 12, 3);
    }

    ctx.restore();
}

function drawCurse(e) {
    ctx.save();
    ctx.translate(e.x, e.y);

    if(e.isElite) {
        // 특급 주령 픽셀
        ctx.fillStyle = '#2d3436';
        ctx.beginPath(); ctx.arc(0, 0, e.radius, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = '#a855f7';
        ctx.beginPath(); ctx.arc(0, 0, e.radius * 0.6, 0, Math.PI*2); ctx.fill();
        // 안구 렌더링
        ctx.fillStyle = '#ff0055';
        ctx.fillRect(-6, -4, 4, 4); ctx.fillRect(2, -4, 4, 4);
    } else {
        // 일반 주령
        ctx.fillStyle = '#102a1c';
        ctx.fillRect(-e.radius, -e.radius, e.radius*2, e.radius*2);
        ctx.fillStyle = '#2ecc71';
        ctx.fillRect(-e.radius/2, -e.radius/2, e.radius, e.radius);
    }

    ctx.restore();
}

function spawnCurse() {
    let x = Math.random() * WORLD_WIDTH;
    let y = Math.random() * WORLD_HEIGHT;

    // 플레이어와 너무 가까운 스폰 방지
    if(Math.hypot(x - player.x, y - player.y) < 400) return;

    let isElite = Math.random() < 0.15;
    enemies.push({
        x: x, y: y,
        radius: isElite ? 22 : 12,
        hp: isElite ? 220 : 40,
        maxHp: isElite ? 220 : 40,
        speed: isElite ? 2.2 : 3.0 + Math.random(),
        isElite: isElite
    });
}

// 자동 술식 발사
let attackTimer = 0;
function autoAttack() {
    if(enemies.length === 0) return;

    // 가장 가까운 적 찾기
    let nearest = null; let minDist = 9999;
    enemies.forEach(e => {
        let d = Math.hypot(e.x - player.x, e.y - player.y);
        if(d < minDist) { minDist = d; nearest = e; }
    });

    if(!nearest) return;
    let ang = Math.atan2(nearest.y - player.y, nearest.x - player.x);

    if(player.charType === 'Gojo') {
        // 아카 (혁) - 유도 붉은 구체
        projectiles.push({
            x: player.x, y: player.y,
            vx: Math.cos(ang) * 12, vy: Math.sin(ang) * 12,
            damage: 45, radius: 8, color: '#ff4757', type: 'aka'
        });
    } else {
        // 이타도리 - 흑섬 타격
        if(minDist < 160) {
            let isBlackFlash = Math.random() < 0.3;
            projectiles.push({
                x: player.x, y: player.y,
                vx: Math.cos(ang) * 15, vy: Math.sin(ang) * 15,
                damage: isBlackFlash ? 150 : 40,
                radius: isBlackFlash ? 18 : 10,
                color: isBlackFlash ? '#000000' : '#ff6b81',
                type: 'strike', isBlackFlash: isBlackFlash
            });
            if(isBlackFlash) screenShake = 12;
        }
    }
}

function update() {
    if(gameOver) return;

    if(screenShake > 0) screenShake--;

    // 플레이어 이동 로직
    let dx = 0, dy = 0;
    if(keys['a'] || keys['arrowleft']) { dx -= 1; player.facing = -1; }
    if(keys['d'] || keys['arrowright']) { dx += 1; player.facing = 1; }
    if(keys['w'] || keys['arrowup']) dy -= 1;
    if(keys['s'] || keys['arrowdown']) dy += 1;

    if(dx !== 0 && dy !== 0) { dx *= 0.7071; dy *= 0.7071; }

    player.x += dx * player.speed;
    player.y += dy * player.speed;

    // 맵 경계 제한
    player.x = Math.max(30, Math.min(WORLD_WIDTH - 30, player.x));
    player.y = Math.max(30, Math.min(WORLD_HEIGHT - 30, player.y));

    // 카메라 추적 (Smooth Lerp)
    camera.x += (player.x - canvas.width / 2 - camera.x) * 0.1;
    camera.y += (player.y - canvas.height / 2 - camera.y) * 0.1;

    // 공격 타이머
    attackTimer++;
    if(attackTimer > 15) { autoAttack(); attackTimer = 0; }

    // 적 스폰
    if(enemies.length < 120) spawnCurse();

    // 영역 전개 제어
    if(player.exp >= player.maxExp && !domainActive) {
        domainActive = true;
        domainTimer = 350;
        player.exp = 0;
        player.maxExp = Math.floor(player.maxExp * 1.4);
    }

    if(domainActive) {
        domainTimer--;
        if(domainTimer <= 0) domainActive = false;

        // 영역전개 지속 효과
        enemies.forEach(e => {
            if(player.charType === 'Gojo') {
                e.speed = 0.2; // 무량처처: 이동 마비
                e.hp -= 0.5;
            } else {
                // 복마어주자: 참격
                if(Math.random() < 0.2) {
                    e.hp -= 8;
                    slicedEffects.push({x: e.x, y: e.y, angle: Math.random()*Math.PI, life: 1.0});
                }
            }
        });
    }

    // 투사체 이동
    projectiles.forEach((p, pi) => {
        p.x += p.vx; p.y += p.vy;

        enemies.forEach((e, ei) => {
            if(Math.hypot(e.x - p.x, e.y - p.y) < e.radius + p.radius) {
                e.hp -= p.damage;
                projectiles.splice(pi, 1);

                if(e.hp <= 0) {
                    killCount++;
                    player.exp += e.isElite ? 25 : 8;
                    enemies.splice(ei, 1);
                }
            }
        });
    });

    // 적 이동 및 공격
    enemies.forEach(e => {
        if(!domainActive || player.charType !== 'Gojo') {
            let ang = Math.atan2(player.y - e.y, player.x - e.x);
            e.x += Math.cos(ang) * e.speed;
            e.y += Math.sin(ang) * e.speed;
        }

        if(Math.hypot(player.x - e.x, player.y - e.y) < e.radius + 12) {
            player.hp -= player.charType === 'Gojo' ? 0.1 : 0.4; // 고죠는 무하한 보호로 피해 감쇄
        }
    });

    // Sliced Effect update
    slicedEffects.forEach((s, si) => {
        s.life -= 0.1;
        if(s.life <= 0) slicedEffects.splice(si, 1);
    });

    // UI 업계
    document.getElementById('hp-bar').style.width = Math.max(0, (player.hp / player.maxHp * 100)) + '%';
    document.getElementById('exp-bar').style.width = Math.min(100, (player.exp / player.maxExp * 100)) + '%';
    document.getElementById('domain-status').innerText = domainActive ? (player.charType === 'Gojo' ? '☯️ 영역전개 「무량처처」' : '⛩️ 영역전개 「복마어주자」') : '영역 전개 준비 중';
    document.getElementById('kill-status').innerText = `제령한 특급 주령: ${killCount}마리`;
}

function draw() {
    ctx.save();
    
    // 화면 흔들림
    if(screenShake > 0) {
        ctx.translate((Math.random()-0.5)*screenShake, (Math.random()-0.5)*screenShake);
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // [카메라 오프셋 적용]
    ctx.translate(-camera.x, -camera.y);

    // 1. 대형 월드 네온 그리드 배경
    ctx.strokeStyle = domainActive ? (player.charType === 'Gojo' ? '#a855f7' : '#ff4757') : 'rgba(255,255,255,0.05)';
    ctx.lineWidth = 1;
    for(let x=0; x<WORLD_WIDTH; x+=80) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,WORLD_HEIGHT); ctx.stroke(); }
    for(let y=0; y<WORLD_HEIGHT; y+=80) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(WORLD_WIDTH,y); ctx.stroke(); }

    // 월드 경계선
    ctx.strokeStyle = '#a855f7';
    ctx.lineWidth = 4;
    ctx.strokeRect(0, 0, WORLD_WIDTH, WORLD_HEIGHT);

    // 2. 주령 (적)
    enemies.forEach(e => drawCurse(e));

    // 3. 투사체
    projectiles.forEach(p => {
        ctx.fillStyle = p.color;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
        if(p.isBlackFlash) {
            ctx.strokeStyle = '#ff0055'; ctx.lineWidth = 3; ctx.stroke();
        }
    });

    // 4. 슬라이스 잔상 (복마어주자 연출)
    slicedEffects.forEach(s => {
        ctx.save();
        ctx.translate(s.x, s.y);
        ctx.rotate(s.angle);
        ctx.strokeStyle = '#ff4757'; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.moveTo(-20, 0); ctx.lineTo(20, 0); ctx.stroke();
        ctx.restore();
    });

    // 5. 플레이어
    drawPlayerSprite(player);

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

components.html(game_html, height=1000)
