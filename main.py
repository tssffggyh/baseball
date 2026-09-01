import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="주술회전: 스킬 쿨타임 & 대사 연출")

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
        overflow: hidden; background: #000;
    }
    canvas { display: block; }
    
    #ui-layer {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; padding: 20px 30px;
        display: flex; flex-direction: column; justify-content: space-between;
        z-index: 10;
    }
    
    .hud-card {
        background: rgba(10, 10, 18, 0.85);
        backdrop-filter: blur(10px);
        padding: 15px 25px; border-radius: 12px;
        border: 1px solid rgba(168, 85, 247, 0.4);
        box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    }
    
    .bar-outer {
        width: 280px; height: 12px; background: rgba(255,255,255,0.1);
        border-radius: 6px; overflow: hidden; margin: 4px 0 10px 0;
    }
    .bar-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff4757, #ff6b81); transition: width 0.1s; }
    .bar-ult { width: 0%; height: 100%; background: linear-gradient(90deg, #a855f7, #e056fd); transition: width 0.1s; }
    
    .skill-container { display: flex; gap: 12px; margin-top: 8px; }
    .skill-icon {
        position: relative;
        width: 60px; height: 60px; background: rgba(255,255,255,0.08);
        border: 1px solid #a855f7; border-radius: 10px;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        font-size: 11px; font-weight: bold; color: #fff; overflow: hidden;
    }
    .skill-key { font-size: 14px; color: #e056fd; }
    .cooldown-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.75); color: #ff4757; font-size: 16px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; display: none;
    }

    #dialogue-box {
        position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%);
        background: rgba(5, 5, 12, 0.9); border: 2px solid #a855f7;
        border-radius: 12px; padding: 12px 30px; text-align: center;
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.6);
        opacity: 0; transition: opacity 0.2s ease-in-out; pointer-events: none;
        z-index: 20;
    }
    #dialogue-text { font-size: 22px; font-weight: bold; color: #f3e8ff; letter-spacing: 2px; }

    #class-select, #game-over {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(3, 3, 6, 0.94); backdrop-filter: blur(15px);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        z-index: 100;
    }
    .card-group { display: flex; gap: 30px; margin-top: 40px; }
    .card {
        background: rgba(20, 20, 35, 0.7); border: 2px solid rgba(168, 85, 247, 0.3);
        border-radius: 20px; padding: 30px 20px; width: 290px;
        text-align: center; cursor: pointer; transition: all 0.3s ease;
    }
    .card:hover {
        transform: translateY(-10px); border-color: #a855f7;
        box-shadow: 0 15px 35px rgba(168, 85, 247, 0.4); background: rgba(30, 30, 50, 0.9);
    }
    .card h2 { margin-bottom: 12px; font-size: 24px; }
    .card p { font-size: 12px; color: #a1a1aa; line-height: 1.6; text-align: left; }
    
    .restart-btn {
        margin-top: 30px; padding: 15px 40px; font-size: 20px; font-weight: bold;
        color: #fff; background: linear-gradient(90deg, #ff4757, #a855f7);
        border: none; border-radius: 10px; cursor: pointer; transition: 0.2s;
    }
    .restart-btn:hover { transform: scale(1.05); }
</style>
</head>
<body>

<div id="game-container">
    <canvas id="gameCanvas"></canvas>
    
    <div id="ui-layer">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div class="hud-card">
                <div id="char-name" style="color:#a855f7; font-weight:bold; font-size:16px;">주술사</div>
                <div style="font-size:10px; color:#aaa; margin-top:4px;">주력 체력 (HP)</div>
                <div class="bar-outer"><div id="hp-bar" class="bar-hp"></div></div>
                <div style="font-size:10px; color:#aaa;">궁극기 게이지 (ULT) [X]</div>
                <div class="bar-outer"><div id="ult-bar" class="bar-ult"></div></div>
                
                <div class="skill-container">
                    <div class="skill-icon">
                        <span class="skill-key">E</span><span id="sk-e">스킬1</span>
                        <div id="cd-e" class="cooldown-overlay">0</div>
                    </div>
                    <div class="skill-icon">
                        <span class="skill-key">R</span><span id="sk-r">스킬2</span>
                        <div id="cd-r" class="cooldown-overlay">0</div>
                    </div>
                    <div class="skill-icon">
                        <span class="skill-key">T</span><span id="sk-t">스킬3</span>
                        <div id="cd-t" class="cooldown-overlay">0</div>
                    </div>
                    <div class="skill-icon" style="border-color:#ff4757;">
                        <span class="skill-key" style="color:#ff4757;">X</span><span>궁극기</span>
                        <div id="cd-x" class="cooldown-overlay">0</div>
                    </div>
                </div>
            </div>
            
            <div class="hud-card" style="text-align:right;">
                <div style="font-size:16px; font-weight:bold; color:#a855f7;">🎮 WASD 이동 | E,R,T,X 스킬</div>
                <div id="kill-status" style="font-size:14px; color:#aaa; margin-top:6px;">제령한 주령: 0마리</div>
            </div>
        </div>
    </div>

    <!-- 기술 대사 출력 팝업 -->
    <div id="dialogue-box">
        <div id="dialogue-text">술식 반전 「아카」</div>
    </div>

    <div id="class-select">
        <h1 style="color:#f3e8ff; font-size:48px; letter-spacing:2px; text-shadow:0 0 20px #a855f7;">JUJUTSU KAISEN</h1>
        <p style="color:#a1a1aa; margin-top:10px;">주술사를 선택하여 주령을 제령하십시오.</p>
        <div class="card-group">
            <div class="card" onclick="selectChar('Gojo')">
                <h2 style="color:#70a1ff;">👁️ 고죠 사토루</h2>
                <p>
                    • E: 술식 반전 「아카」 (유도 붉은 탄환)<br>
                    • R: 술식 순전 「아오」 (인력 흡입)<br>
                    • T: 무하한 결계 (충격파 밀쳐내기)<br>
                    • <strong>X [궁극기]: 허식 「무라사키」</strong>
                </p>
            </div>
            <div class="card" onclick="selectChar('Yuji')">
                <h2 style="color:#ff4757;">👊 이타도리 유우지</h2>
                <p>
                    • E: 경정권 (타격 충격파)<br>
                    • R: 흑섬! (칠흑 크리티컬 타격)<br>
                    • T: 순보 (순간 대시)<br>
                    • <strong>X [궁극기]: 영역전개 「복마어주자」</strong>
                </p>
            </div>
            <div class="card" onclick="selectChar('Megumi')">
                <h2 style="color:#2ecc71;">🐺 후시구로 메구미</h2>
                <p>
                    • E: 십종영법술 「누에」 (전방 뇌격)<br>
                    • R: 십종영법술 「옥견」 (추적 돌진)<br>
                    • T: 그림자 속박 (적 이속 저하)<br>
                    • <strong>X [궁극기]: 강대마허라 소환</strong>
                </p>
            </div>
        </div>
    </div>

    <div id="game-over" style="display:none;">
        <h1 style="color:#ff4757; font-size:56px; letter-spacing:3px;">YOU DIED</h1>
        <p style="color:#aaa; margin-top:10px; font-size:18px;" id="final-stats">주령들의 공격으로 사망했습니다.</p>
        <button class="restart-btn" onclick="location.reload()">다시 도전하기</button>
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

const WORLD_WIDTH = 3200;
const WORLD_HEIGHT = 2400;

let killCount = 0;
let isGameOver = false;
let screenShake = 0;
let camera = { x: 0, y: 0 };
let dialogueTimeout = null;

let player = {
    x: WORLD_WIDTH / 2, y: WORLD_HEIGHT / 2,
    speed: 5.8, hp: 200, maxHp: 200,
    ultEnergy: 0, maxUlt: 100,
    charType: 'Gojo', facing: 1
};

// 스킬 쿨타임 (초 단위)
let cooldowns = {
    E: 0, R: 0, T: 0, X: 0
};

let maxCooldowns = {
    Gojo: { E: 3, R: 6, T: 8, X: 0 },
    Yuji: { E: 2, R: 5, T: 4, X: 0 },
    Megumi: { E: 3, R: 5, T: 6, X: 0 }
};

// 기술 대사
let dialogues = {
    Gojo: {
        E: '술식 반전 「아카」',
        R: '술식 순전 「아오」',
        T: '무하한',
        X: '허식 「무라사키」'
    },
    Yuji: {
        E: '경정권!',
        R: '흑섬!',
        T: '순보',
        X: '영역전개 「복마어주자」'
    },
    Megumi: {
        E: '십종영법술 「누에」',
        R: '십종영법술 「옥견」',
        T: '그림자 속박',
        X: '팔지검 이계신장 강대마허라'
    }
};

let mahoraga = null;
let keys = {};
let projectiles = [];
let enemyProjectiles = [];
let poisonPools = [];
let enemies = [];

window.addEventListener('keydown', e => {
    let k = e.key.toLowerCase();
    keys[k] = true;
    if(k === 'e') castSkill('E');
    if(k === 'r') castSkill('R');
    if(k === 't') castSkill('T');
    if(k === 'x') castSkill('X');
});
window.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

function showDialogue(text) {
    let box = document.getElementById('dialogue-box');
    let elem = document.getElementById('dialogue-text');
    elem.innerText = text;
    box.style.opacity = '1';

    if(dialogueTimeout) clearTimeout(dialogueTimeout);
    dialogueTimeout = setTimeout(() => {
        box.style.opacity = '0';
    }, 1500);
}

function triggerVibration(intensity) {
    screenShake = intensity;
    if (navigator.vibrate) {
        navigator.vibrate(intensity * 15);
    }
}

function selectChar(type) {
    player.charType = type;
    document.getElementById('class-select').style.display = 'none';
    
    let skNames = {
        'Gojo': ['아카', '아오', '무하한', '무라사키'],
        'Yuji': ['경정권', '흑섬', '순보', '복마어주자'],
        'Megumi': ['누에', '옥견', '그림자', '마허라']
    };
    
    document.getElementById('char-name').innerText = type;
    document.getElementById('sk-e').innerText = skNames[type][0];
    document.getElementById('sk-r').innerText = skNames[type][1];
    document.getElementById('sk-t').innerText = skNames[type][2];

    for(let i=0; i<45; i++) spawnCurse();
    gameLoop();
}

function castSkill(key) {
    if(isGameOver) return;
    if(cooldowns[key] > 0) return; // 쿨타임 중일 경우 사용 불가

    if(key === 'X' && player.ultEnergy < player.maxUlt) return; // 궁극기 게이지 부족

    let nearest = null; let minDist = 9999;
    enemies.forEach(e => {
        let d = Math.hypot(e.x - player.x, e.y - player.y);
        if(d < minDist) { minDist = d; nearest = e; }
    });
    let ang = nearest ? Math.atan2(nearest.y - player.y, nearest.x - player.x) : 0;

    // 대사 출력 및 진동
    showDialogue(dialogues[player.charType][key]);

    if(key === 'E') {
        cooldowns.E = maxCooldowns[player.charType].E;
        triggerVibration(8);

        if(player.charType === 'Gojo') {
            projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang)*15, vy: Math.sin(ang)*15, damage: 80, radius: 10, color: '#ff4757'});
        } else if(player.charType === 'Yuji') {
            if(nearest && minDist < 160) nearest.hp -= 110;
        } else {
            projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang)*16, vy: Math.sin(ang)*16, damage: 85, radius: 12, color: '#f1c40f'});
        }
    } else if(key === 'R') {
        cooldowns.R = maxCooldowns[player.charType].R;
        triggerVibration(12);

        if(player.charType === 'Gojo') {
            enemies.forEach(e => {
                if(Math.hypot(e.x - player.x, e.y - player.y) < 350) {
                    e.x = player.x + Math.cos(ang)*60; e.y = player.y + Math.sin(ang)*60; e.hp -= 60;
                }
            });
        } else if(player.charType === 'Yuji') {
            if(nearest && minDist < 180) { nearest.hp -= 260; }
        } else {
            for(let i=0; i<3; i++) projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang + (i-1)*0.2)*13, vy: Math.sin(ang + (i-1)*0.2)*13, damage: 70, radius: 8, color: '#2ecc71'});
        }
    } else if(key === 'T') {
        cooldowns.T = maxCooldowns[player.charType].T;
        triggerVibration(10);

        if(player.charType === 'Gojo') {
            enemies.forEach(e => {
                if(Math.hypot(e.x - player.x, e.y - player.y) < 250) { e.x += Math.cos(Math.atan2(e.y-player.y, e.x-player.x))*180; e.hp -= 40; }
            });
        } else if(player.charType === 'Yuji') {
            player.x += Math.cos(ang) * 220; player.y += Math.sin(ang) * 220;
        } else {
            enemies.forEach(e => { if(Math.hypot(e.x - player.x, e.y - player.y) < 300) e.speed = 0.5; });
        }
    } else if(key === 'X') {
        player.ultEnergy = 0;
        triggerVibration(22);

        if(player.charType === 'Gojo') {
            projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang)*22, vy: Math.sin(ang)*22, damage: 700, radius: 50, color: '#a855f7'});
        } else if(player.charType === 'Yuji') {
            enemies.forEach(e => { e.hp -= 400; });
        } else {
            mahoraga = { x: player.x, y: player.y - 50, life: 600 };
        }
    }
}

function spawnCurse() {
    let x = Math.random() * WORLD_WIDTH;
    let y = Math.random() * WORLD_HEIGHT;
    if(Math.hypot(x - player.x, y - player.y) < 400) return;

    let types = ['normal', 'charger', 'spitter', 'poison'];
    let type = types[Math.floor(Math.random() * types.length)];

    enemies.push({
        x: x, y: y, type: type,
        radius: type === 'charger' ? 18 : (type === 'spitter' ? 14 : 12),
        hp: type === 'charger' ? 220 : 70, maxHp: type === 'charger' ? 220 : 70,
        speed: type === 'charger' ? 1.8 : (type === 'poison' ? 2.2 : 2.8),
        attackCd: 0, chargeTimer: 0
    });
}

function triggerGameOver() {
    isGameOver = true;
    document.getElementById('ui-layer').style.display = 'none';
    document.getElementById('game-over').style.display = 'flex';
    document.getElementById('final-stats').innerText = `제령한 주령 수: ${killCount}마리`;
}

// 쿨타임 스케줄러 (매 100ms 마다 감쇠)
setInterval(() => {
    ['E', 'R', 'T', 'X'].forEach(k => {
        if(cooldowns[k] > 0) {
            cooldowns[k] = Math.max(0, cooldowns[k] - 0.1);
        }
        let elem = document.getElementById('cd-' + k.toLowerCase());
        if(elem) {
            if(cooldowns[k] > 0) {
                elem.style.display = 'flex';
                elem.innerText = cooldowns[k].toFixed(1);
            } else {
                elem.style.display = 'none';
            }
        }
    });
}, 100);

function update() {
    if(isGameOver) return;
    if(screenShake > 0) screenShake--;

    if(player.hp <= 0) { triggerGameOver(); return; }

    let dx = 0, dy = 0;
    if(keys['a']) { dx -= 1; player.facing = -1; }
    if(keys['d']) { dx += 1; player.facing = 1; }
    if(keys['w']) dy -= 1;
    if(keys['s']) dy += 1;
    if(dx !== 0 && dy !== 0) { dx *= 0.7071; dy *= 0.7071; }

    player.x = Math.max(30, Math.min(WORLD_WIDTH - 30, player.x + dx * player.speed));
    player.y = Math.max(30, Math.min(WORLD_HEIGHT - 30, player.y + dy * player.speed));

    camera.x += (player.x - canvas.width / 2 - camera.x) * 0.1;
    camera.y += (player.y - canvas.height / 2 - camera.y) * 0.1;

    if(enemies.length < 60) spawnCurse();

    // 마허라 AI
    if(mahoraga) {
        mahoraga.life--;
        let nearest = null; let minDist = 9999;
        enemies.forEach(e => {
            let d = Math.hypot(e.x - mahoraga.x, e.y - mahoraga.y);
            if(d < minDist) { minDist = d; nearest = e; }
        });
        if(nearest) {
            let ang = Math.atan2(nearest.y - mahoraga.y, nearest.x - mahoraga.x);
            mahoraga.x += Math.cos(ang) * 5; mahoraga.y += Math.sin(ang) * 5;
            if(minDist < 60) nearest.hp -= 25;
        }
        if(mahoraga.life <= 0) mahoraga = null;
    }

    // 적 투사체
    enemyProjectiles.forEach((ep, epi) => {
        ep.x += ep.vx; ep.y += ep.vy;
        if(Math.hypot(player.x - ep.x, player.y - ep.y) < ep.radius + 10) {
            player.hp -= ep.damage;
            enemyProjectiles.splice(epi, 1);
        }
    });

    // 독장판
    poisonPools.forEach((p, pi) => {
        p.life--;
        if(Math.hypot(player.x - p.x, player.y - p.y) < p.radius) {
            player.hp -= 0.4;
        }
        if(p.life <= 0) poisonPools.splice(pi, 1);
    });

    // 투사체
    projectiles.forEach((p, pi) => {
        p.x += p.vx; p.y += p.vy;
        enemies.forEach((e, ei) => {
            if(Math.hypot(e.x - p.x, e.y - p.y) < e.radius + p.radius) {
                e.hp -= p.damage;
                if(e.hp <= 0) {
                    killCount++;
                    player.ultEnergy = Math.min(player.maxUlt, player.ultEnergy + 10);
                    enemies.splice(ei, 1);
                }
            }
        });
    });

    // 주령 AI
    enemies.forEach((e, ei) => {
        let ang = Math.atan2(player.y - e.y, player.x - e.x);
        let dist = Math.hypot(player.x - e.x, player.y - e.y);

        if(e.type === 'charger') {
            e.chargeTimer++;
            if(e.chargeTimer > 100) {
                e.x += Math.cos(ang) * 9; e.y += Math.sin(ang) * 9;
                if(e.chargeTimer > 140) e.chargeTimer = 0;
            } else {
                e.x += Math.cos(ang) * e.speed; e.y += Math.sin(ang) * e.speed;
            }
        } else if(e.type === 'spitter') {
            if(dist > 250) { e.x += Math.cos(ang) * e.speed; e.y += Math.sin(ang) * e.speed; }
            e.attackCd++;
            if(e.attackCd > 90) {
                enemyProjectiles.push({x: e.x, y: e.y, vx: Math.cos(ang)*7, vy: Math.sin(ang)*7, damage: 15, radius: 6});
                e.attackCd = 0;
            }
        } else if(e.type === 'poison') {
            e.x += Math.cos(ang) * e.speed; e.y += Math.sin(ang) * e.speed;
            if(Math.random() < 0.015) poisonPools.push({x: e.x, y: e.y, radius: 25, life: 200});
        } else {
            e.x += Math.cos(ang) * e.speed; e.y += Math.sin(ang) * e.speed;
        }

        if(dist < e.radius + 12) {
            player.hp -= (e.type === 'charger' ? 1.2 : 0.5);
        }
    });

    // UI 게이지
    document.getElementById('hp-bar').style.width = Math.max(0, (player.hp / player.maxHp * 100)) + '%';
    document.getElementById('ult-bar').style.width = Math.min(100, (player.ultEnergy / player.maxUlt * 100)) + '%';
    document.getElementById('kill-status').innerText = `제령한 주령: ${killCount}마리`;
}

function drawPlayerSprite(p) {
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.scale(p.facing, 1);

    if(p.charType === 'Gojo') {
        ctx.fillStyle = '#111'; ctx.fillRect(-8, -12, 16, 26);
        ctx.fillStyle = '#ffdfc4'; ctx.fillRect(-6, -18, 12, 6);
        ctx.fillStyle = '#fff'; ctx.fillRect(-8, -26, 16, 7);
    } else if(p.charType === 'Yuji') {
        ctx.fillStyle = '#111'; ctx.fillRect(-8, -6, 16, 20);
        ctx.fillStyle = '#ff4757'; ctx.fillRect(-8, -14, 16, 10);
        ctx.fillStyle = '#ff7675'; ctx.fillRect(-8, -26, 16, 7);
    } else {
        ctx.fillStyle = '#0a192f'; ctx.fillRect(-8, -12, 16, 26);
        ctx.fillStyle = '#ffdfc4'; ctx.fillRect(-6, -18, 12, 6);
        ctx.fillStyle = '#1e272e'; ctx.fillRect(-10, -28, 20, 10);
    }
    ctx.restore();
}

function drawMahoraga(m) {
    ctx.save();
    ctx.translate(m.x, m.y);
    ctx.strokeStyle = '#f1c40f'; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.arc(0, -30, 25, 0, Math.PI*2); ctx.stroke();
    ctx.fillStyle = '#ffffff'; ctx.fillRect(-16, -20, 32, 45);
    ctx.fillStyle = '#f1c40f'; ctx.fillRect(16, -35, 8, 50);
    ctx.restore();
}

function draw() {
    ctx.save();
    if(screenShake > 0) ctx.translate((Math.random()-0.5)*screenShake, (Math.random()-0.5)*screenShake);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.translate(-camera.x, -camera.y);

    // Grid
    ctx.strokeStyle = 'rgba(168, 85, 247, 0.06)'; ctx.lineWidth = 1;
    for(let x=0; x<WORLD_WIDTH; x+=100) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,WORLD_HEIGHT); ctx.stroke(); }
    for(let y=0; y<WORLD_HEIGHT; y+=100) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(WORLD_WIDTH,y); ctx.stroke(); }

    // 독장판
    poisonPools.forEach(p => {
        ctx.fillStyle = 'rgba(46, 204, 113, 0.25)';
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
    });

    // 주령
    enemies.forEach(e => {
        if(e.type === 'charger') ctx.fillStyle = '#ff4757';
        else if(e.type === 'spitter') ctx.fillStyle = '#9b59b6';
        else if(e.type === 'poison') ctx.fillStyle = '#2ecc71';
        else ctx.fillStyle = '#718093';

        ctx.beginPath(); ctx.arc(e.x, e.y, e.radius, 0, Math.PI*2); ctx.fill();
    });

    // 투사체
    enemyProjectiles.forEach(ep => {
        ctx.fillStyle = '#e056fd';
        ctx.beginPath(); ctx.arc(ep.x, ep.y, ep.radius, 0, Math.PI*2); ctx.fill();
    });

    projectiles.forEach(p => {
        ctx.fillStyle = p.color;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
    });

    if(mahoraga) drawMahoraga(mahoraga);
    drawPlayerSprite(player);

    ctx.restore();
}

function gameLoop() {
    update();
    draw();
    if(!isGameOver) requestAnimationFrame(gameLoop);
}
</script>
</body>
</html>
"""

components.html(game_html, height=1000)
