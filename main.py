import streamlit as str_lit
import streamlit.components.v1 as components

str_lit.set_page_config(layout="wide", page_title="주술회전: 캐릭터 선택 전투 시스템")

str_lit.markdown("""
    <style>
        .main .block-container { max-width: 100% !important; padding: 0rem !important; overflow: hidden !important; }
        iframe { width: 100% !important; height: 100vh !important; border: none; display: block; }
        header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background-color: #020204; color: #fff;
        font-family: 'Consolas', monospace;
        width: 100vw; height: 100vh; overflow: hidden;
    }
    #game-container {
        position: relative; width: 100vw; height: 100vh;
        overflow: hidden; background: #000;
    }
    canvas { display: block; cursor: crosshair; width: 100%; height: 100%; }
    
    #ui-layer {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; padding: 15px 25px;
        display: flex; flex-direction: column; justify-content: space-between; z-index: 10;
        display: none;
    }
    .hud-card {
        background: rgba(10, 10, 20, 0.85); backdrop-filter: blur(10px);
        padding: 10px 18px; border-radius: 12px;
        border: 1px solid rgba(0, 243, 255, 0.4); box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    }
    .bar-outer {
        width: 240px; height: 10px; background: rgba(255,255,255,0.1);
        border-radius: 5px; overflow: hidden; margin: 3px 0 8px 0;
    }
    .bar-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #00f3ff, #0066ff); transition: width 0.1s; }
    .bar-ult { width: 0%; height: 100%; background: linear-gradient(90deg, #a855f7, #ec4899); transition: width 0.1s; }
    
    #boss-hud {
        position: absolute; top: 15px; left: 50%; transform: translateX(-50%);
        width: 480px; background: rgba(10, 10, 20, 0.9);
        border: 2px solid #00f3ff; border-radius: 10px; padding: 8px 15px;
        text-align: center; display: none; z-index: 15;
    }
    .boss-bar-outer { width: 100%; height: 12px; background: rgba(255,255,255,0.1); border-radius: 6px; overflow: hidden; margin-top: 4px; }
    .boss-bar-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff4757, #e84118); transition: width 0.1s; }

    .skill-container { display: flex; gap: 6px; margin-top: 6px; }
    .skill-icon {
        position: relative; width: 44px; height: 44px; background: rgba(255,255,255,0.08);
        border: 1px solid #00f3ff; border-radius: 8px;
        display: flex; flex-direction: column; justify-content: space-between; align-items: center;
        padding: 3px; font-size: 8px; font-weight: bold; color: #fff; overflow: hidden;
    }
    .skill-key { font-size: 11px; color: #00f3ff; }
    .cooldown-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.75); color: #00f3ff; font-size: 13px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; display: none;
    }

    #dialogue-box {
        position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%);
        background: rgba(10, 10, 25, 0.95); border: 2px solid #00f3ff;
        border-radius: 12px; padding: 10px 25px; text-align: center;
        box-shadow: 0 0 30px rgba(0, 243, 255, 0.5);
        opacity: 0; transition: opacity 0.15s ease-in-out; pointer-events: none; z-index: 20;
    }
    #dialogue-text { font-size: 20px; font-weight: bold; color: #00f3ff; letter-spacing: 2px; }

    #domain-kanji-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        pointer-events: none; z-index: 50; opacity: 0; transition: opacity 0.3s ease;
    }
    .kanji-line {
        font-size: 64px; font-weight: 900; color: #00f3ff;
        text-shadow: 0 0 30px #00f3ff, 0 0 60px #0066ff, 0 0 10px #fff;
        letter-spacing: 8px; margin: 5px 0;
    }

    #class-select, #game-over {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(5, 5, 10, 0.95); backdrop-filter: blur(15px);
        display: flex; flex-direction: column; justify-content: center; z-index: 100;
        align-items: center; pointer-events: auto;
    }
    .card-group { display: flex; gap: 25px; margin-top: 30px; }
    .card {
        background: rgba(20, 20, 35, 0.8); border: 2px solid rgba(0, 243, 255, 0.3);
        border-radius: 16px; padding: 25px 20px; width: 280px;
        text-align: center; cursor: pointer; transition: all 0.3s ease;
    }
    .card:hover {
        transform: translateY(-8px); border-color: #00f3ff;
        box-shadow: 0 15px 35px rgba(0, 243, 255, 0.4); background: rgba(30, 30, 50, 0.95);
    }
    .card.sukuna:hover {
        border-color: #ff4757; box-shadow: 0 15px 35px rgba(255, 71, 87, 0.4);
    }
    .card h2 { margin-bottom: 10px; font-size: 22px; }
    .card p { font-size: 11px; color: #a1a1aa; line-height: 1.5; text-align: left; }
    
    .restart-btn {
        margin-top: 25px; padding: 12px 35px; font-size: 18px; font-weight: bold;
        color: #fff; background: linear-gradient(90deg, #00f3ff, #0066ff);
        border: none; border-radius: 10px; cursor: pointer; transition: 0.2s;
    }
    .restart-btn:hover { transform: scale(1.05); }
</style>
</head>
<body>

<div id="game-container">
    <canvas id="gameCanvas"></canvas>
    
    <div id="domain-kanji-overlay">
        <div class="kanji-line" id="kanji-1">영역전개</div>
        <div class="kanji-line" id="kanji-2">무량공처</div>
    </div>

    <div id="boss-hud">
        <div id="boss-name" style="color:#ff4757; font-weight:bold; font-size:14px;">[LV.1] 토벌 대상</div>
        <div class="boss-bar-outer"><div id="boss-hp-bar" class="boss-bar-hp"></div></div>
    </div>

    <div id="ui-layer">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div class="hud-card" id="hud-card-main">
                <div id="char-name" style="color:#00f3ff; font-weight:bold; font-size:15px;">고죠 사토루</div>
                <div style="font-size:9px; color:#aaa; margin-top:3px;">체력 (HP)</div>
                <div class="bar-outer"><div id="hp-bar" class="bar-hp"></div></div>
                <div style="font-size:9px; color:#aaa;">주력 게이지 (ULT) [X]</div>
                <div class="bar-outer"><div id="ult-bar" class="bar-ult"></div></div>
                
                <div class="skill-container">
                    <div class="skill-icon" id="auto-icon" style="border-color:#3498db;">
                        <span class="skill-key" style="color:#3498db;" id="lbl-auto-key">AUTO</span><span id="lbl-auto-name">평타</span>
                    </div>
                    <div class="skill-icon" id="icon-e">
                        <span class="skill-key" id="key-e">E</span><span id="sk-e">아카</span>
                        <div id="cd-e" class="cooldown-overlay">0</div>
                    </div>
                    <div class="skill-icon" id="icon-r">
                        <span class="skill-key" id="key-r">R</span><span id="sk-r">아오</span>
                        <div id="cd-r" class="cooldown-overlay">0</div>
                    </div>
                    <div class="skill-icon" id="icon-t">
                        <span class="skill-key" id="key-t">T</span><span id="sk-t">무라사키</span>
                        <div id="cd-t" class="cooldown-overlay">0</div>
                    </div>
                    <div class="skill-icon" id="icon-x" style="border-color:#a855f7;">
                        <span class="skill-key" style="color:#a855f7;" id="key-x">X</span><span id="sk-x">무량공처</span>
                        <div id="cd-x" class="cooldown-overlay">0</div>
                    </div>
                </div>
            </div>
            
            <div class="hud-card" style="text-align:right;">
                <div id="boss-status" style="font-size:13px; color:#ff4757; font-weight:bold;">전투 대기 중...</div>
                <div id="kill-status" style="font-size:12px; color:#aaa; margin-top:4px;">처치한 보스: 0 / 100</div>
                <div id="mob-kill-status" style="font-size:12px; color:#00f3ff; margin-top:2px; font-weight:bold;">처치한 적: 0마리</div>
            </div>
        </div>
    </div>

    <div id="dialogue-box">
        <div id="dialogue-text">영역전개</div>
    </div>

    <div id="class-select">
        <h1 style="color:#00f3ff; font-size:42px; letter-spacing:2px; text-shadow:0 0 20px #00f3ff;">JUJUTSU KAISEN</h1>
        <p style="color:#a1a1aa; margin-top:8px; font-size:13px;">플레이할 캐릭터를 선택하세요</p>
        <div class="card-group">
            <div class="card" id="card-gojo" onclick="selectCharacter('Gojo')">
                <h2 style="color:#00f3ff;">⚡ 고죠 사토루</h2>
                <p>
                    • E: 반전술식 「아카(赤)」<br>
                    • R: 술식순반 「아오(蒼)」<br>
                    • T: 허식 「무라사키(紫)」<br>
                    • X: 영역전개 「무량공처」
                </p>
            </div>
            <div class="card sukuna" id="card-sukuna" onclick="selectCharacter('Sukuna')">
                <h2 style="color:#ff4757;">👹 양면 스쿠나</h2>
                <p>
                    • E: 참격 「해(解)」<br>
                    • R: 난도질 「팔(捌)」<br>
                    • T: 화염술 「푸가(🔥)」<br>
                    • X: 영역전개 「복마어주자」
                </p>
            </div>
        </div>
    </div>

    <div id="game-over" style="display:none;">
        <h1 style="color:#ff4757; font-size:48px; letter-spacing:3px;">YOU DIED</h1>
        <p style="color:#aaa; margin-top:10px; font-size:16px;" id="final-stats">사망하셨습니다.</p>
        <button class="restart-btn" id="restart-btn">다시 도전하기</button>
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

let selectedChar = 'Gojo';

function selectCharacter(charType) {
    selectedChar = charType;
    document.getElementById('class-select').style.display = 'none';
    document.getElementById('ui-layer').style.display = 'flex';
    
    if(selectedChar === 'Sukuna') {
        player.maxHp = 600; player.hp = 600;
        document.getElementById('char-name').innerText = "양면 스쿠나";
        document.getElementById('hud-card-main').style.borderColor = "#ff4757";
        document.getElementById('sk-e').innerText = "해(解)";
        document.getElementById('sk-r').innerText = "팔(捌)";
        document.getElementById('sk-t').innerText = "푸가";
        document.getElementById('sk-x').innerText = "복마어주자";
        document.getElementById('lbl-auto-name').innerText = "참격";
        document.getElementById('mob-kill-status').style.color = "#ff4757";
    } else {
        player.maxHp = 500; player.hp = 500;
        document.getElementById('char-name').innerText = "고죠 사토루";
        document.getElementById('hud-card-main').style.borderColor = "#00f3ff";
        document.getElementById('sk-e').innerText = "아카";
        document.getElementById('sk-r').innerText = "아오";
        document.getElementById('sk-t').innerText = "무라사키";
        document.getElementById('sk-x').innerText = "무량공처";
        document.getElementById('lbl-auto-name').innerText = "평타";
        document.getElementById('mob-kill-status').style.color = "#00f3ff";
    }
    
    for(let i=0; i<35; i++) spawnCurse();
    spawnBoss();
    gameLoop();
}

const WORLD_WIDTH = 7200;
const WORLD_HEIGHT = 5400;

let bossLevel = 1;
let defeatedBosses = 0;
let normalKillCount = 0;
let isGameOver = false;
let screenShake = 0;
let camera = { x: 0, y: 0 };
let dialogueTimeout = null;
let lastHitTime = Date.now();
let bossRespawnTimer = null;
let respawnCountdown = 0;

let bloodSplatters = [];
let projectiles = [];
let enemyProjectiles = [];
let slashes = [];
let explosions = [];
let enemies = [];

let player = {
    x: WORLD_WIDTH / 2, y: WORLD_HEIGHT / 2,
    speed: 7.0, hp: 500, maxHp: 500,
    ultEnergy: 0, maxUlt: 100, facing: 1, lastAttack: 0
};

let cooldowns = { E: 0, R: 0, T: 0, X: 0 };
let maxCooldowns = { E: 5, R: 7, T: 12, X: 0 };

let keys = {};
window.addEventListener('keydown', e => {
    let k = e.key.toLowerCase();
    keys[k] = true;
    if(k === 'e') castSkill('E');
    if(k === 'r') castSkill('R');
    if(k === 't') castSkill('T');
    if(k === 'x') castSkill('X');
});
window.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

function addUlt(amount) { player.ultEnergy = Math.min(player.maxUlt, player.ultEnergy + amount); }
function takeDamage(damage) {
    if(selectedChar === 'Gojo' && Math.random() < 0.25) return; // 무하한 패시브 회피
    player.hp -= damage; 
    lastHitTime = Date.now();
}

function showDialogue(text) {
    let box = document.getElementById('dialogue-box');
    let elem = document.getElementById('dialogue-text');
    elem.innerText = text;
    box.style.opacity = '1';
    if(dialogueTimeout) clearTimeout(dialogueTimeout);
    dialogueTimeout = setTimeout(() => box.style.opacity = '0', 1600);
}

function triggerVibration(intensity) { screenShake = intensity; }

document.getElementById('restart-btn').addEventListener('click', () => location.reload());

function getAutoAimAngle() {
    if(enemies.length === 0) return 0;
    let closestEnemy = null;
    let minDist = Infinity;
    enemies.forEach(e => {
        let dist = Math.hypot(e.x - player.x, e.y - player.y);
        if(dist < minDist) { minDist = dist; closestEnemy = e; }
    });
    if(closestEnemy) return Math.atan2(closestEnemy.y - player.y, closestEnemy.x - player.x);
    return 0;
}

function performAutoAttack() {
    if(isGameOver) return;
    let now = Date.now();
    if(now - player.lastAttack < 350) return;
    player.lastAttack = now;
    let ang = getAutoAimAngle();
    addUlt(1.2);
    player.facing = Math.cos(ang) >= 0 ? 1 : -1;

    if(selectedChar === 'Sukuna') {
        slashes.push({ x: player.x + Math.cos(ang)*25, y: player.y + Math.sin(ang)*25, ang: ang, length: 70, life: 7, damage: 120 });
    } else {
        projectiles.push({ x: player.x, y: player.y, vx: Math.cos(ang)*16, vy: Math.sin(ang)*16, radius: 8, damage: 100, color: '#00f3ff' });
    }
}

let activeDomain = null;

function castSkill(key) {
    if(isGameOver) return;
    if(cooldowns[key] > 0) return;
    if(key === 'X' && player.ultEnergy < player.maxUlt) return;

    let ang = getAutoAimAngle();
    let targetX = player.x + Math.cos(ang) * 220;
    let targetY = player.y + Math.sin(ang) * 220;

    if(selectedChar === 'Sukuna') {
        if(key === 'E') {
            cooldowns.E = maxCooldowns.E; addUlt(3.0); triggerVibration(20);
            showDialogue('참격 「해(解)」');
            for(let i=-1; i<=1; i++) slashes.push({ x: player.x, y: player.y, ang: ang + i*0.1, length: 320, life: 12, damage: 1200 });
        } else if(key === 'R') {
            cooldowns.R = maxCooldowns.R; addUlt(4.5); triggerVibration(25);
            showDialogue('참격 「팔(捌)」');
            for(let i=0; i<10; i++) slashes.push({ x: targetX + (Math.random()-0.5)*180, y: targetY + (Math.random()-0.5)*180, ang: Math.random()*Math.PI*2, length: 150, life: 10, damage: 800 });
        } else if(key === 'T') {
            cooldowns.T = maxCooldowns.T; addUlt(7.0); triggerVibration(35);
            showDialogue('「푸가(🔥)」');
            explosions.push({ x: targetX, y: targetY, radius: 20, maxRadius: 280, color: 'rgba(255, 107, 53, 0.9)', life: 25, damage: 3500 });
        } else if(key === 'X') {
            player.ultEnergy = 0; triggerVibration(45);
            showDialogue('영역전개 「복마어주자」');
            activeDomain = { type: 'Sukuna', timer: 900 };
            document.getElementById('kanji-1').innerText = "영역전개";
            document.getElementById('kanji-2').innerText = "伏魔御廚子";
            triggerDomainKanji();
        }
    } else {
        if(key === 'E') {
            cooldowns.E = maxCooldowns.E; addUlt(3.0); triggerVibration(25);
            showDialogue('반전술식 「아카(赤)」');
            explosions.push({ x: targetX, y: targetY, radius: 10, maxRadius: 180, color: 'rgba(255, 50, 50, 0.85)', life: 20, damage: 1400 });
        } else if(key === 'R') {
            cooldowns.R = maxCooldowns.R; addUlt(4.5); triggerVibration(20);
            showDialogue('술식순반 「아오(蒼)」');
            enemies.forEach(e => { if(Math.hypot(e.x - targetX, e.y - targetY) < 250) { e.x += (targetX - e.x)*0.5; e.y += (targetY - e.y)*0.5; e.hp -= 900; } });
        } else if(key === 'T') {
            cooldowns.T = maxCooldowns.T; addUlt(7.0); triggerVibration(40);
            showDialogue('허식 「무라사키(紫)」');
            projectiles.push({ x: player.x, y: player.y, vx: Math.cos(ang)*12, vy: Math.sin(ang)*12, radius: 45, damage: 4500, color: '#a855f7', isPurple: true });
        } else if(key === 'X') {
            player.ultEnergy = 0; triggerVibration(50);
            showDialogue('영역전개 「무량공처」');
            activeDomain = { type: 'Gojo', timer: 900 };
            document.getElementById('kanji-1').innerText = "영역전개";
            document.getElementById('kanji-2').innerText = "무량공처";
            triggerDomainKanji();
            enemies.forEach(e => { e.stunTimer = 600; });
        }
    }
}

function triggerDomainKanji() {
    let kanjiEl = document.getElementById('domain-kanji-overlay');
    kanjiEl.style.opacity = '1';
    setTimeout(() => { kanjiEl.style.opacity = '0'; }, 3000);
}

const BOSS_TITLES = ["특급 주술사", "오천 년 전의 주술사", "반역의 주령사", "특급 가상원령", "저주의 왕의 적수"];

function getBossData(lvl) {
    let baseHp = 2500;
    let scaledHp = Math.floor(baseHp * Math.pow(lvl, 1.6));
    let nameIdx = (lvl - 1) % BOSS_TITLES.length;
    return {
        level: lvl, name: `${BOSS_TITLES[nameIdx]} [${lvl}/100]`,
        hp: scaledHp, radius: 30, speed: Math.min(4.8, 2.5 + (lvl * 0.023)),
        dmg: 30 + Math.floor(lvl * 3.0), color: '#ff4757', aura: '#ff6b81'
    };
}

function spawnCurse() {
    let x = Math.random() * WORLD_WIDTH;
    let y = Math.random() * WORLD_HEIGHT;
    if(Math.hypot(x - player.x, y - player.y) < 500) return;
    let isRanged = Math.random() < 0.35;
    enemies.push({
        x: x, y: y, radius: isRanged ? 18 : 22,
        hp: isRanged ? 120 : 180, maxHp: isRanged ? 120 : 180,
        speed: isRanged ? 2.2 : 3.0, isBoss: false, isRanged: isRanged, attackCd: 0, stunTimer: 0
    });
}

function startBossRespawnTimer() {
    respawnCountdown = 4;
    let statusElem = document.getElementById('boss-status');
    statusElem.innerText = `다음 대상 등장까지: ${respawnCountdown}초`;
    bossRespawnTimer = setInterval(() => {
        respawnCountdown--;
        if(respawnCountdown > 0) {
            statusElem.innerText = `다음 대상 등장까지: ${respawnCountdown}초`;
        } else {
            clearInterval(bossRespawnTimer);
            bossRespawnTimer = null;
            statusElem.innerText = `⚠️ 강적과 교전 중!`;
            spawnBoss();
        }
    }, 1000);
}

function spawnBoss() {
    if(bossLevel > 100) return;
    let cfg = getBossData(bossLevel);
    let spawnAngle = Math.random() * Math.PI * 2;
    let bx = Math.max(200, Math.min(WORLD_WIDTH - 200, player.x + Math.cos(spawnAngle) * 1000));
    let by = Math.max(200, Math.min(WORLD_HEIGHT - 200, player.y + Math.sin(spawnAngle) * 1000));

    enemies.push({
        x: bx, y: by, level: cfg.level, name: cfg.name,
        hp: cfg.hp, maxHp: cfg.hp, radius: cfg.radius, speed: cfg.speed, dmg: cfg.dmg,
        color: cfg.color, aura: cfg.aura, isBoss: true, attackCd: 0, skillCd: 0, stunTimer: 0, facing: 1
    });
    document.getElementById('boss-status').innerText = `⚠️ 강적과 교전 중!`;
    showDialogue(`⚠️ [LV.${cfg.level}] ${cfg.name} 출현!`);
    triggerVibration(25);
}

setInterval(() => {
    ['E', 'R', 'T', 'X'].forEach(k => {
        if(cooldowns[k] > 0) cooldowns[k] = Math.max(0, cooldowns[k] - 0.1);
        let elem = document.getElementById('cd-' + k.toLowerCase());
        if(elem) {
            if(cooldowns[k] > 0) { elem.style.display = 'flex'; elem.innerText = cooldowns[k].toFixed(1); }
            else elem.style.display = 'none';
        }
    });

    if(!isGameOver && Date.now() - lastHitTime >= 3000) {
        if(player.hp < player.maxHp) player.hp = Math.min(player.maxHp, player.hp + (player.maxHp * 0.02));
    }
}, 100);

function update() {
    if(isGameOver) return;
    if(screenShake > 0) screenShake--;
    if(player.hp <= 0) {
        isGameOver = true;
        if(bossRespawnTimer) clearInterval(bossRespawnTimer);
        document.getElementById('ui-layer').style.display = 'none';
        document.getElementById('game-over').style.display = 'flex';
        document.getElementById('final-stats').innerText = `도달 보스 레벨: Lv.${bossLevel} | 처치한 보스: ${defeatedBosses}마리 | 처치한 적: ${normalKillCount}마리`;
        return;
    }

    performAutoAttack();

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

    if(enemies.filter(e => !e.isBoss).length < 70) spawnCurse();

    if(activeDomain) {
        activeDomain.timer--;
        triggerVibration(5);
        if(activeDomain.type === 'Sukuna' && Math.random() < 0.6) {
            let target = enemies[Math.floor(Math.random() * enemies.length)];
            if(target) { target.hp -= 150; slashes.push({x: target.x, y: target.y, ang: Math.random()*Math.PI, length: 90, life: 5, damage: 200}); }
        } else if(activeDomain.type === 'Gojo') {
            enemies.forEach(e => { e.hp -= 40; });
        }
        if(activeDomain.timer <= 0) activeDomain = null;
    }

    let activeBosses = enemies.filter(e => e.isBoss);
    let bossHud = document.getElementById('boss-hud');
    if(activeBosses.length > 0) {
        let topBoss = activeBosses[0];
        bossHud.style.display = 'block';
        document.getElementById('boss-name').innerText = `[LV.${topBoss.level}] ${topBoss.name}`;
        document.getElementById('boss-hp-bar').style.width = Math.max(0, (topBoss.hp / topBoss.maxHp * 100)) + '%';
    } else {
        bossHud.style.display = 'none';
    }

    bloodSplatters.forEach((bs, bsi) => {
        bs.life--; bs.x += bs.vx; bs.y += bs.vy;
        if(bs.life <= 0) bloodSplatters.splice(bsi, 1);
    });

    projectiles.forEach((p, pi) => {
        p.x += p.vx; p.y += p.vy;
        enemies.forEach(e => {
            if(Math.hypot(e.x - p.x, e.y - p.y) < e.radius + p.radius) {
                e.hp -= p.damage;
                if(p.isPurple) {
                    explosions.push({ x: p.x, y: p.y, radius: 10, maxRadius: 150, color: 'rgba(168, 85, 247, 0.8)', life: 15, damage: 1500 });
                }
                projectiles.splice(pi, 1);
            }
        });
    });

    enemyProjectiles.forEach((ep, epi) => {
        ep.x += ep.vx; ep.y += ep.vy;
        if(Math.hypot(player.x - ep.x, player.y - ep.y) < ep.radius + 15) {
            takeDamage(ep.damage);
            enemyProjectiles.splice(epi, 1);
        }
    });

    explosions.forEach((ex, exi) => {
        ex.life--;
        if(ex.radius < ex.maxRadius) ex.radius += (ex.maxRadius - ex.radius) * 0.2;
        enemies.forEach(e => { if(Math.hypot(e.x - ex.x, e.y - ex.y) < ex.radius) e.hp -= ex.damage / 15; });
        if(ex.life <= 0) explosions.splice(exi, 1);
    });

    slashes.forEach((s, si) => {
        s.life--;
        enemies.forEach(e => { if(Math.hypot(e.x - s.x, e.y - s.y) < s.length / 2) e.hp -= s.damage / 5; });
        if(s.life <= 0) slashes.splice(si, 1);
    });

    enemies.forEach((e, ei) => {
        if(e.stunTimer > 0) { e.stunTimer--; return; }
        let ang = Math.atan2(player.y - e.y, player.x - e.x);
        let dist = Math.hypot(player.x - e.x, player.y - e.y);
        e.facing = Math.cos(ang) >= 0 ? 1 : -1;

        if(e.isRanged && dist < 320) {
            e.x -= Math.cos(ang) * e.speed; e.y -= Math.sin(ang) * e.speed;
        } else {
            e.x += Math.cos(ang) * e.speed; e.y += Math.sin(ang) * e.speed;
        }

        e.attackCd = (e.attackCd || 0) + 1;
        e.skillCd = (e.skillCd || 0) + 1;

        if(e.isRanged && e.attackCd >= 70 && dist < 500) {
            e.attackCd = 0;
            enemyProjectiles.push({ x: e.x, y: e.y, vx: Math.cos(ang)*7, vy: Math.sin(ang)*7, damage: 15, radius: 6 });
        }

        if(e.isBoss && e.skillCd >= 70) {
            e.skillCd = 0;
            explosions.push({ x: e.x, y: e.y, radius: 15, maxRadius: 140, color: 'rgba(255, 71, 87, 0.4)', life: 15, damage: e.dmg * 0.8 });
        }

        if(!e.isRanged && dist < e.radius + 28) {
            if(e.attackCd >= (e.isBoss ? 25 : 45)) {
                e.attackCd = 0;
                takeDamage(e.isBoss ? e.dmg : 12);
            }
        }

        if(e.hp <= 0) {
            if(e.isBoss) {
                defeatedBosses++; bossLevel++; addUlt(15.0);
                enemies.splice(ei, 1);
                if(bossLevel <= 100) startBossRespawnTimer();
            } else {
                for(let b=0; b<8; b++) {
                    let bAng = Math.random() * Math.PI * 2;
                    let bSpd = Math.random() * 4 + 1;
                    bloodSplatters.push({ x: e.x, y: e.y, vx: Math.cos(bAng)*bSpd, vy: Math.sin(bAng)*bSpd, radius: Math.random()*3+2, life: 25 });
                }
                normalKillCount++; addUlt(0.8);
                enemies.splice(ei, 1);
            }
        }
    });

    document.getElementById('hp-bar').style.width = Math.max(0, (player.hp / player.maxHp * 100)) + '%';
    document.getElementById('ult-bar').style.width = Math.min(100, (player.ultEnergy / player.maxUlt * 100)) + '%';
    document.getElementById('kill-status').innerText = `처치한 보스: ${defeatedBosses} / 100`;
    document.getElementById('mob-kill-status').innerText = `처치한 적: ${normalKillCount}마리`;
}

function drawPlayerSprite(p) {
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.scale(p.facing, 1);

    if(selectedChar === 'Sukuna') {
        ctx.shadowBlur = 20; ctx.shadowColor = '#ff4757';
        ctx.fillStyle = '#111'; ctx.fillRect(-10, -16, 20, 32);
        ctx.fillStyle = '#ff7675'; ctx.fillRect(-9, -32, 18, 10);
        ctx.fillStyle = '#ff4757'; ctx.fillRect(-6, -26, 12, 3);
    } else {
        ctx.shadowBlur = 20; ctx.shadowColor = '#00f3ff';
        ctx.fillStyle = '#222'; ctx.fillRect(-10, -16, 20, 32);
        ctx.fillStyle = '#ffffff'; ctx.fillRect(-9, -32, 18, 10);
        ctx.fillStyle = '#00f3ff'; ctx.fillRect(-5, -28, 10, 4);
    }
    ctx.shadowBlur = 0;
    ctx.restore();
}

function drawEnemySprite(e) {
    ctx.save();
    ctx.translate(e.x, e.y);
    ctx.scale(e.facing || 1, 1);

    if(e.isBoss) {
        ctx.shadowBlur = 20; ctx.shadowColor = e.aura;
        ctx.fillStyle = '#2d132c'; ctx.fillRect(-12, -18, 24, 36);
        ctx.fillStyle = '#ff7675'; ctx.fillRect(-10, -36, 20, 16);
        ctx.strokeStyle = e.aura; ctx.lineWidth = 2; ctx.strokeRect(-14, -40, 28, 58);
        ctx.shadowBlur = 0;
        ctx.fillStyle = '#ff4757'; ctx.font = 'bold 14px Consolas'; ctx.textAlign = 'center';
        ctx.fillText(`[LV.${e.level}]`, 0, -48);
    } else {
        ctx.fillStyle = e.isRanged ? '#8e44ad' : '#2c2c54';
        ctx.beginPath(); ctx.arc(0, 0, e.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#ff4757'; ctx.lineWidth = 2; ctx.stroke();
    }
    ctx.restore();
}

function draw() {
    ctx.save();
    if(screenShake > 0) ctx.translate((Math.random()-0.5)*screenShake, (Math.random()-0.5)*screenShake);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.translate(-camera.x, -camera.y);

    if(activeDomain) {
        ctx.fillStyle = selectedChar === 'Sukuna' ? 'rgba(50, 5, 5, 0.8)' : 'rgba(5, 5, 40, 0.8)';
        ctx.fillRect(camera.x, camera.y, canvas.width, canvas.height);
        ctx.strokeStyle = selectedChar === 'Sukuna' ? '#ff4757' : '#00f3ff';
        ctx.lineWidth = 8;
        ctx.strokeRect(player.x - 600, player.y - 600, 1200, 1200);
    }

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)'; ctx.lineWidth = 1;
    for(let x=0; x<WORLD_WIDTH; x+=100) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, WORLD_HEIGHT); ctx.stroke(); }
    for(let y=0; y<WORLD_HEIGHT; y+=100) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(WORLD_WIDTH, y); ctx.stroke(); }

    bloodSplatters.forEach(bs => {
        ctx.fillStyle = '#c0392b';
        ctx.beginPath(); ctx.arc(bs.x, bs.y, bs.radius, 0, Math.PI * 2); ctx.fill();
    });

    enemies.forEach(e => drawEnemySprite(e));

    projectiles.forEach(p => {
        ctx.fillStyle = p.color;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
    });

    enemyProjectiles.forEach(ep => {
        ctx.fillStyle = '#ff4757';
        ctx.beginPath(); ctx.arc(ep.x, ep.y, ep.radius, 0, Math.PI*2); ctx.fill();
    });

    slashes.forEach(s => {
        ctx.strokeStyle = '#ff4757'; ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(s.x - Math.cos(s.ang)*s.length/2, s.y - Math.sin(s.ang)*s.length/2);
        ctx.lineTo(s.x + Math.cos(s.ang)*s.length/2, s.y + Math.sin(s.ang)*s.length/2);
        ctx.stroke();
    });

    explosions.forEach(ex => {
        ctx.fillStyle = ex.color;
        ctx.beginPath(); ctx.arc(ex.x, ex.y, ex.radius, 0, Math.PI*2); ctx.fill();
    });

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

components.html(game_html, height=850, scrolling=False)
