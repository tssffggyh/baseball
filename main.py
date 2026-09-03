import streamlit as str_lit
import streamlit.components.v1 as components

str_lit.set_page_config(layout="wide", page_title="주술회전: 인간형 보스 개정판")

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
    }
    .hud-card {
        background: rgba(10, 10, 18, 0.85); backdrop-filter: blur(10px);
        padding: 10px 18px; border-radius: 12px;
        border: 1px solid rgba(168, 85, 247, 0.4); box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    }
    .bar-outer {
        width: 240px; height: 10px; background: rgba(255,255,255,0.1);
        border-radius: 5px; overflow: hidden; margin: 3px 0 8px 0;
    }
    .bar-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff4757, #ff6b81); transition: width 0.1s; }
    .bar-ult { width: 0%; height: 100%; background: linear-gradient(90deg, #a855f7, #e056fd); transition: width 0.1s; }
    
    #boss-hud {
        position: absolute; top: 15px; left: 50%; transform: translateX(-50%);
        width: 480px; background: rgba(15, 5, 5, 0.9);
        border: 2px solid #ff4757; border-radius: 10px; padding: 8px 15px;
        text-align: center; display: none; z-index: 15;
    }
    .boss-bar-outer { width: 100%; height: 12px; background: rgba(255,255,255,0.1); border-radius: 6px; overflow: hidden; margin-top: 4px; }
    .boss-bar-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff4757, #e84118); transition: width 0.1s; }

    .skill-container { display: flex; gap: 6px; margin-top: 6px; }
    .skill-icon {
        position: relative; width: 44px; height: 44px; background: rgba(255,255,255,0.08);
        border: 1px solid #a855f7; border-radius: 8px;
        display: flex; flex-direction: column; justify-content: space-between; align-items: center;
        padding: 3px; font-size: 8px; font-weight: bold; color: #fff; overflow: hidden;
    }
    .skill-key { font-size: 11px; color: #e056fd; }
    .cooldown-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.75); color: #ff4757; font-size: 13px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; display: none;
    }

    #dialogue-box {
        position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%);
        background: rgba(5, 5, 12, 0.95); border: 2px solid #a855f7;
        border-radius: 12px; padding: 10px 25px; text-align: center;
        box-shadow: 0 0 30px rgba(168, 85, 247, 0.8);
        opacity: 0; transition: opacity 0.15s ease-in-out; pointer-events: none; z-index: 20;
    }
    #dialogue-text { font-size: 20px; font-weight: bold; color: #f3e8ff; letter-spacing: 2px; }

    #domain-kanji-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        pointer-events: none; z-index: 50; opacity: 0; transition: opacity 0.3s ease;
    }
    .kanji-line {
        font-size: 64px; font-weight: 900; color: #70a1ff;
        text-shadow: 0 0 30px #00d2ff, 0 0 60px #70a1ff, 0 0 10px #fff;
        letter-spacing: 8px; margin: 5px 0;
    }

    #class-select, #game-over {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(3, 3, 6, 0.94); backdrop-filter: blur(15px);
        display: flex; flex-direction: column; justify-content: center; z-index: 100;
        align-items: center; pointer-events: auto;
    }
    .card-group { display: flex; gap: 20px; margin-top: 30px; }
    .card {
        background: rgba(20, 20, 35, 0.7); border: 2px solid rgba(168, 85, 247, 0.3);
        border-radius: 16px; padding: 25px 15px; width: 260px;
        text-align: center; cursor: pointer; transition: all 0.3s ease;
    }
    .card:hover {
        transform: translateY(-8px); border-color: #a855f7;
        box-shadow: 0 15px 35px rgba(168, 85, 247, 0.4); background: rgba(30, 30, 50, 0.9);
    }
    .card h2 { margin-bottom: 10px; font-size: 22px; }
    .card p { font-size: 11px; color: #a1a1aa; line-height: 1.5; text-align: left; }
    
    .restart-btn {
        margin-top: 25px; padding: 12px 35px; font-size: 18px; font-weight: bold;
        color: #fff; background: linear-gradient(90deg, #ff4757, #a855f7);
        border: none; border-radius: 10px; cursor: pointer; transition: 0.2s;
    }
    .restart-btn:hover { transform: scale(1.05); }
</style>
</head>
<body>

<div id="game-container">
    <canvas id="gameCanvas"></canvas>
    
    <div id="domain-kanji-overlay">
        <div class="kanji-line">領域展開</div>
        <div class="kanji-line">無량공처</div>
    </div>

    <div id="boss-hud">
        <div id="boss-name" style="color:#ff4757; font-weight:bold; font-size:14px;">[LV.1] 인간형 보스</div>
        <div class="boss-bar-outer"><div id="boss-hp-bar" class="boss-bar-hp"></div></div>
    </div>

    <div id="ui-layer">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div class="hud-card">
                <div id="char-name" style="color:#a855f7; font-weight:bold; font-size:15px;">주술사</div>
                <div style="font-size:9px; color:#aaa; margin-top:3px;">체력 (HP)</div>
                <div class="bar-outer"><div id="hp-bar" class="bar-hp"></div></div>
                <div style="font-size:9px; color:#aaa;">궁극기 게이지 (ULT) [X]</div>
                <div class="bar-outer"><div id="ult-bar" class="bar-ult"></div></div>
                
                <div class="skill-container">
                    <div class="skill-icon" style="border-color:#3498db;">
                        <span class="skill-key" style="color:#3498db;">AUTO</span><span>오토에임</span>
                    </div>
                    <div class="skill-icon">
                        <span class="skill-key">E</span><span id="sk-e">아카</span>
                        <div id="cd-e" class="cooldown-overlay">0</div>
                    </div>
                    <div class="skill-icon">
                        <span class="skill-key">R</span><span id="sk-r">아오</span>
                        <div id="cd-r" class="cooldown-overlay">0</div>
                    </div>
                    <div class="skill-icon">
                        <span class="skill-key">T</span><span id="sk-t">무라사키</span>
                        <div id="cd-t" class="cooldown-overlay">0</div>
                    </div>
                    <div class="skill-icon" style="border-color:#ff4757;">
                        <span class="skill-key" style="color:#ff4757;">X</span><span>영역전개</span>
                        <div id="cd-x" class="cooldown-overlay">0</div>
                    </div>
                </div>
            </div>
            
            <div class="hud-card" style="text-align:right;">
                <div id="boss-status" style="font-size:13px; color:#ff4757; font-weight:bold;">보스 소환 대기 중...</div>
                <div id="kill-status" style="font-size:12px; color:#aaa; margin-top:4px;">처치한 보스: 0 / 100</div>
                <div id="mob-kill-status" style="font-size:12px; color:#a855f7; margin-top:2px; font-weight:bold;">처치한 일반 주령: 0마리</div>
            </div>
        </div>
    </div>

    <div id="dialogue-box">
        <div id="dialogue-text">무라사키 발동</div>
    </div>

    <div id="class-select">
        <h1 style="color:#f3e8ff; font-size:42px; letter-spacing:2px; text-shadow:0 0 20px #a855f7;">JUJUTSU KAISEN</h1>
        <p style="color:#a1a1aa; margin-top:8px; font-size:13px;">[인간형 보스 시스템 도입 - 지능형 전투 및 고유 스킬 구사]</p>
        <div class="card-group">
            <div class="card" id="card-gojo">
                <h2 style="color:#70a1ff;">👁️ 고죠 사토루</h2>
                <p>
                    • E: 술식반전 · 「赤」<br>
                    • R: 술식순전 · 「蒼」<br>
                    • T: 허식 「茈」 (2초 차징)<br>
                    • X: 무량공처
                </p>
            </div>
            <div class="card" id="card-sukuna">
                <h2 style="color:#ff4757;">👹 양면 스쿠나</h2>
                <p>
                    • E: 해(解) / R: 팔(捌)<br>
                    • T: 푸가(🔥)<br>
                    • X: 복마어주자
                </p>
            </div>
            <div class="card" id="card-megumi">
                <h2 style="color:#2ecc71;">🐺 후시구로 메구미</h2>
                <p>
                    • E: 누에 / R: 옥견<br>
                    • T: 그림자 폭발<br>
                    • X: 마허라
                </p>
            </div>
        </div>
    </div>

    <div id="game-over" style="display:none;">
        <h1 style="color:#ff4757; font-size:48px; letter-spacing:3px;">YOU DIED</h1>
        <p style="color:#aaa; margin-top:10px; font-size:16px;" id="final-stats">주령들의 공격으로 사망했습니다.</p>
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

const aoAudio = new Audio('https://www.myinstants.com/media/sounds/jujutsu-kaisen-gojo-blue-ao.mp3');
aoAudio.volume = 1.0;

const purpleAudio = new Audio('https://www.myinstants.com/media/sounds/hollow-purple.mp3');
purpleAudio.volume = 0.3;

let audioCtx = null;
function initAudio() {
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    [aoAudio, purpleAudio].forEach(audio => {
        if(audio.paused) {
            audio.play().catch(() => {});
            audio.pause();
            audio.currentTime = 0;
        }
    });
}

function playVoiceAndSound(type) {
    initAudio();
    if(type === 'ao_voice') { aoAudio.currentTime = 0; aoAudio.play().catch(err => {}); return; }
    if(type === 'purple_voice') { purpleAudio.currentTime = 0; purpleAudio.play().catch(err => {}); return; }
    if(!audioCtx) return;
    let now = audioCtx.currentTime;
    let osc = audioCtx.createOscillator();
    let gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    if(type === 'aka') {
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(440, now);
        osc.frequency.exponentialRampToValueAtTime(110, now + 0.35);
        gain.gain.setValueAtTime(0.4, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
        osc.start(now); osc.stop(now + 0.35);
    }
}

const WORLD_WIDTH = 7200;
const WORLD_HEIGHT = 5400;

let bossLevel = 1;
let defeatedBosses = 0;
let normalKillCount = 0;
let totalKillCount = 0;
let isGameOver = false;
let screenShake = 0;
let camera = { x: 0, y: 0 };
let dialogueTimeout = null;
let lastHitTime = Date.now();
let bossRespawnTimer = null;
let respawnCountdown = 0;
let gojoDomainCount = 0;
let playerStunTimer = 0;

let bloodSplatters = [];

let player = {
    x: WORLD_WIDTH / 2, y: WORLD_HEIGHT / 2,
    baseSpeed: 6.5, speed: 6.5, hp: 300, maxHp: 300,
    ultEnergy: 0, maxUlt: 100,
    charType: 'Gojo', facing: 1, lastAttack: 0
};

let cooldowns = { E: 0, R: 0, T: 0, X: 0 };
let maxCooldowns = {
    Gojo: { E: 8, R: 7, T: 16, X: 0 },
    Sukuna: { E: 7, R: 7, T: 14, X: 0 },
    Megumi: { E: 8, R: 7, T: 15, X: 0 }
};

let dialogues = {
    Gojo: { E: '술식반전 · 「赤」', R: '술식순전 · 「蒼」', T: '허식 「茈」', X: '료이키텐카이 무량공처' },
    Sukuna: { E: '참격 「해(解)」', R: '참격 「팔(捌)」', T: '「푸가(🔥)」', X: '영역전개 「복마어주자」' },
    Megumi: { E: '십종영법술 「누에」', R: '십종영법술 「옥견」', T: '그림자 폭발', X: '마허라 소환' }
};

let activeDomain = null;
let mahoraga = null;
let keys = {};
let projectiles = [];
let enemyProjectiles = [];
let slashes = [];
let explosions = [];
let blackHoles = [];     
let blueOrbs = [];       
let purpleEffects = [];   
let purpleProjectiles = []; 
let chargingPurples = [];   
let laserBeams = [];
let meleeAttacks = [];
let enemies = [];
let highQualityShots = []; 
let windTrails = [];      
let sukunaFlames = [];
let worldSlashes = [];
let domainSlashes = [];
let sukunaFlash = 0;
let sukunaPassiveTimer = 0;
let gojoInfinityTimer = 0;


const HUMAN_BOSS_TITLES = ["특급 주술사 켄자쿠", "빙관의 주술사 우라우메", "타락한 천재 주술사", "저주받은 왕 스쿠나 분신", "피의 지배자 아바타"];

function getBossData(lvl) {
    let baseHp = 2200;
    let scaledHp = Math.floor(baseHp * Math.pow(lvl, 1.68));
    let nameIdx = (lvl - 1) % HUMAN_BOSS_TITLES.length;
    let title = lvl > 80 ? "신화급 인간형 주술사" : (lvl > 50 ? "재앙급 특급 인간" : "인간형 강적");

    return {
        level: lvl, name: `${title} - ${HUMAN_BOSS_TITLES[nameIdx]} [${lvl}/100]`,
        hp: scaledHp, radius: 28, 
        speed: Math.min(5.2, 2.6 + (lvl * 0.026)), dmg: 32 + Math.floor(lvl * 3.2),
        color: '#ff4757', aura: '#e84118'
    };
}

window.addEventListener('keydown', e => {
    initAudio();
    let k = e.key.toLowerCase();
    keys[k] = true;
    if(k === 'e') castSkill('E');
    if(k === 'r') castSkill('R');
    if(k === 't') castSkill('T');
    if(k === 'x') castSkill('X');
});
window.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

function addUltFromKill() {
    totalKillCount++;
    // 궁극기 사용 중에는 처치해도 궁 게이지가 오르지 않음.
    if(activeDomain) return;
    player.ultEnergy = Math.min(player.maxUlt, (totalKillCount % 60) * (player.maxUlt / 60));
    if(totalKillCount % 60 === 0) player.ultEnergy = player.maxUlt;
}

function takeDamage(damage) {
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

function triggerVibration(intensity) {
    screenShake = intensity;
    if (navigator.vibrate) navigator.vibrate(intensity * 15);
}

function selectChar(type) {
    sukunaPassiveTimer = 0;
    gojoInfinityTimer = 0;
    initAudio();
    player.charType = type;
    document.getElementById('class-select').style.display = 'none';
    
    let skNames = {
        'Gojo': ['아카', '아오', '무라사키', '무량공처'],
        'Sukuna': ['해(解)', '팔(捌)', '푸가', '복마어주자'],
        'Megumi': ['누에', '옥견', '그림자', '마허라']
    };
    
    document.getElementById('char-name').innerText = type === 'Gojo' ? '고죠 사토루' : (type === 'Sukuna' ? '양면 스쿠나' : '후시구로 메구미');
    document.getElementById('sk-e').innerText = skNames[type][0];
    document.getElementById('sk-r').innerText = skNames[type][1];
    document.getElementById('sk-t').innerText = skNames[type][2];

    for(let i=0; i<40; i++) spawnCurse();
    spawnBoss();
    gameLoop();
}

document.getElementById('card-gojo').addEventListener('click', () => selectChar('Gojo'));
document.getElementById('card-sukuna').addEventListener('click', () => selectChar('Sukuna'));
document.getElementById('card-megumi').addEventListener('click', () => selectChar('Megumi'));
document.getElementById('restart-btn').addEventListener('click', () => location.reload());

function getAutoAimAngle() {
    if(enemies.length === 0) return 0;
    let closestEnemy = null;
    let minDist = Infinity;
    
    enemies.forEach(e => {
        let dist = Math.hypot(e.x - player.x, e.y - player.y);
        if(dist < minDist) {
            minDist = dist;
            closestEnemy = e;
        }
    });

    if(closestEnemy) {
        return Math.atan2(closestEnemy.y - player.y, closestEnemy.x - player.x);
    }
    return 0;
}

function performAutoAttack() {
    if(isGameOver || playerStunTimer > 0) return;
    let now = Date.now();
    let attackInterval = (player.charType === 'Gojo') ? 700 : 600;
    if(now - player.lastAttack < attackInterval) return;
    player.lastAttack = now;

    let ang = getAutoAimAngle();
    player.facing = Math.cos(ang) >= 0 ? 1 : -1;

    if(player.charType === 'Gojo') {
        let shotX = player.x + Math.cos(ang) * 20;
        let shotY = player.y + Math.sin(ang) * 20;
        projectiles.push({
            x: shotX, y: shotY, vx: Math.cos(ang)*16, vy: Math.sin(ang)*16,
            damage: 80, radius: 14, color: '#00d2ff', type:'gojo_hq_basic', trailTimer: 25
        });
        for(let i=0; i<8; i++) {
            highQualityShots.push({
                x: shotX, y: shotY, vx: Math.cos(ang + (Math.random()-0.5)*0.5)*(Math.random()*6+3), vy: Math.sin(ang + (Math.random()-0.5)*0.5)*(Math.random()*6+3),
                radius: Math.random()*5+2, life: 18, color: '#70a1ff'
            });
        }
    } else if(player.charType === 'Sukuna') {
        // 스쿠나 평타: 2초 연사 → 2초 쿨타임
        if(!player.sukunaBasicTimer || player.sukunaBasicTimer <= 0) {
            if(player.sukunaBasicCooldown && player.sukunaBasicCooldown > 0) return;
            player.sukunaBasicTimer = 120;
            player.sukunaBasicCooldown = 120;
            player.sukunaBasicShotTimer = 0;
        }
    } else {
        projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang)*14, vy: Math.sin(ang)*14, damage: 60, radius: 8, color: '#2ecc71', type:'normal'});
    }
}

function castSkill(key) {
    if(isGameOver) return;
    if(cooldowns[key] > 0) return;
    if(key === 'X' && player.ultEnergy < player.maxUlt) return;
    if(key !== 'X' && playerStunTimer > 0) return;

    let ang = getAutoAimAngle();
    let targetX = player.x + Math.cos(ang) * 200;
    let targetY = player.y + Math.sin(ang) * 200;

    if(key === 'X' && player.charType === 'Gojo') {
        gojoDomainCount++;
        if(gojoDomainCount >= 4) {
            showDialogue('더 이상 쓸 수가 없어...');
            cooldowns.X = 24;
            player.ultEnergy = 0;
            gojoDomainCount = 0;
            triggerVibration(40);
            return;
        }
    }

    showDialogue(dialogues[player.charType][key]);

    if(key === 'E') {
        cooldowns.E = maxCooldowns[player.charType].E;
        
        if(player.charType === 'Gojo') {
            playVoiceAndSound('aka');
            triggerVibration(30);
            
            let targetOrb = blueOrbs.length > 0 ? blueOrbs[0] : null;
            let finalVx = Math.cos(ang)*18;
            let finalVy = Math.sin(ang)*18;
            let targetXPos = targetX;
            let targetYPos = targetY;

            if(targetOrb) {
                let orbAng = Math.atan2(targetOrb.y - player.y, targetOrb.x - player.x);
                finalVx = Math.cos(orbAng) * 22;
                finalVy = Math.sin(orbAng) * 22;
                targetXPos = targetOrb.x;
                targetYPos = targetOrb.y;
            }

            projectiles.push({
                x: player.x, y: player.y, 
                targetX: targetXPos, targetY: targetYPos,
                vx: finalVx, vy: finalVy,
                type: 'aka', damage: 3500, radius: 28,
                maxDist: targetOrb ? Math.hypot(targetOrb.x - player.x, targetOrb.y - player.y) : 350, 
                traveled: 0, targetOrb: targetOrb
            });
        } else if(player.charType === 'Sukuna') {
            // 해(解): 전방에 넓고 날카로운 고품질 참격을 부채꼴로 연속 생성
            for(let i=-3; i<=3; i++) {
                let a = ang + i*0.105;
                slashes.push({
                    x: player.x + Math.cos(a) * 55,
                    y: player.y + Math.sin(a) * 55,
                    ang: a,
                    length: 270,
                    curve: -28,
                    life: 20,
                    damage: 2300,
                    width: 9,
                    color: '#000000',
                    outline: '#ffffff',
                    speed: 19,
                    ranged: true
                });
            }
            sukunaFlash = 12;
            sukunaFlash = 8;
            triggerVibration(28);
        } else {
            explosions.push({x: targetX, y: targetY, radius: 70, maxRadius: 70, color: '#f1c40f', life: 15, damage: 1200});
        }
    } else if(key === 'R') {
        cooldowns.R = maxCooldowns[player.charType].R;
        
        if(player.charType === 'Gojo') {
            playVoiceAndSound('ao_voice');
            triggerVibration(25);
            blackHoles.push({
                orbitAngle: ang, orbitRadius: 260, radius: 420, life: 180, damage: 3000, x: player.x, y: player.y
            });
        } else if(player.charType === 'Sukuna') {
            // 팔(捌): 멀리 있는 적들의 '현재 위치'에만 대량의 참격 생성
            let targets = enemies
                .filter(e => Math.hypot(e.x - player.x, e.y - player.y) < 1000)
                .slice(0, 12);

            targets.forEach(e => {
                for(let i=0; i<3; i++) {
                    domainSlashes.push({
                        x: e.x,
                        y: e.y,
                        ang: Math.random() * Math.PI * 2,
                        length: 210 + Math.random() * 100,
                        life: 20,
                        damage: 2100,
                        width: 7 + Math.random() * 3,
                        color: '#000000',
                        outline: '#ffffff'
                    });
                }
            });
            sukunaFlash = 14;
            sukunaFlash = 12;
            triggerVibration(34);
        } else {
            projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang)*15, vy: Math.sin(ang)*15, type:'normal', damage: 1500, radius: 10, color: '#2ecc71'});
        }
    } else if(key === 'T') {
        cooldowns.T = maxCooldowns[player.charType].T;
        triggerVibration(35);

        if(player.charType === 'Sukuna') {
            // 푸가: 두꺼운 붉은 화살이 날아가다 폭발
            let domainBoost = activeDomain && activeDomain.type === 'Sukuna';
            sukunaFlames.push({
                x: player.x, y: player.y,
                vx: Math.cos(ang) * (domainBoost ? 11 : 8.5),
                vy: Math.sin(ang) * (domainBoost ? 11 : 8.5),
                radius: domainBoost ? 38 : 24,
                maxRadius: domainBoost ? 420 : 180,
                life: domainBoost ? 90 : 75,
                damage: domainBoost ? 11000 : 6500,
                type: 'fuga'
            });
            sukunaFlash = 18;
        } else {
            purpleAudio.currentTime = 0;
            purpleAudio.play().catch(() => {});

            // 움직이는 위치를 따라가도록 등록
            chargingPurples.push({
                ang: ang,
                radius: 5,       
                maxRadius: 130,   
                chargeTimer: 120,  
                damage: 9999
            });
        }
    } else if(key === 'X') {
        player.ultEnergy = 0;
        if(player.charType === 'Gojo') {
            activeDomain = { type: 'Gojo', timer: 1200 };
            playerStunTimer = 180;
            
            enemies.forEach(e => {
                e.stunTimer = 1200;
            });

            let kanjiEl = document.getElementById('domain-kanji-overlay');
            kanjiEl.style.opacity = '1';
            setTimeout(() => {
                kanjiEl.style.opacity = '0';
            }, 3000);

        } else if(player.charType === 'Sukuna') {
            // 복마어주자: 넓은 영역에 지속적으로 참격이 생성됨
            activeDomain = { type: 'Sukuna', timer: 2400, radius: 760 };
            player.sukunaUltKills = 0;
            player.ultEnergy = 0;
            sukunaFlash = 35;
            for(let i=0; i<55; i++) {
                let a = Math.random() * Math.PI * 2;
                let r = Math.sqrt(Math.random()) * 760;
                domainSlashes.push({
                    x: player.x + Math.cos(a) * r,
                    y: player.y + Math.sin(a) * r,
                    ang: Math.random() * Math.PI * 2,
                    length: 100 + Math.random() * 170,
                    life: 24 + Math.random() * 10,
                    damage: 2200,
                    width: 4 + Math.random() * 3
                });
            }
        } else {
            mahoraga = { x: player.x, y: player.y - 50, life: 1500 };
        }
        triggerVibration(40);
    }
}

function spawnCurse() {
    let x = Math.random() * WORLD_WIDTH;
    let y = Math.random() * WORLD_HEIGHT;
    if(Math.hypot(x - player.x, y - player.y) < 500) return;

    let isRanged = Math.random() < 0.4;
    let newEnemy = {
        x: x, y: y, radius: isRanged ? 18 : 22,
        hp: isRanged ? 100 : 150, maxHp: isRanged ? 100 : 150,
        speed: isRanged ? 2.0 : 2.8,
        isBoss: false, isRanged: isRanged, attackCd: 0, stunTimer: 0
    };
    if(activeDomain && activeDomain.type === 'Gojo') {
        newEnemy.stunTimer = activeDomain.timer;
    }
    enemies.push(newEnemy);
}

function startBossRespawnTimer() {
    respawnCountdown = 5;
    let statusElem = document.getElementById('boss-status');
    statusElem.innerText = `다음 인간형 보스 소환까지: ${respawnCountdown}초`;

    bossRespawnTimer = setInterval(() => {
        respawnCountdown--;
        if(respawnCountdown > 0) {
            statusElem.innerText = `다음 인간형 보스 소환까지: ${respawnCountdown}초`;
        } else {
            clearInterval(bossRespawnTimer);
            bossRespawnTimer = null;
            statusElem.innerText = `⚠️ 인간형 보스와 교전 중!`;
            spawnBoss();
        }
    }, 1000);
}

function spawnBoss() {
    if(bossLevel > 100) return;
    let cfg = getBossData(bossLevel);

    let spawnAngle = Math.random() * Math.PI * 2;
    let spawnDist = 900 + Math.random() * 300;
    let bx = player.x + Math.cos(spawnAngle) * spawnDist;
    let by = player.y + Math.sin(spawnAngle) * spawnDist;

    bx = Math.max(200, Math.min(WORLD_WIDTH - 200, bx));
    by = Math.max(200, Math.min(WORLD_HEIGHT - 200, by));

    let boss = {
        x: bx, y: by, level: cfg.level, name: cfg.name,
        hp: cfg.hp, maxHp: cfg.hp, radius: cfg.radius, speed: cfg.speed, dmg: cfg.dmg,
        color: cfg.color, aura: cfg.aura,
        isBoss: true, attackCd: 0, skillCd: 0, ultCd: 0, stunTimer: 0, facing: 1
    };
    
    if(activeDomain && activeDomain.type === 'Gojo') {
        boss.stunTimer = activeDomain.timer;
    }

    enemies.push(boss);
    document.getElementById('boss-status').innerText = `⚠️ 인간형 보스와 교전 중!`;
    showDialogue(`⚠️ [LV.${cfg.level}] 인간형 강적 출현!`);
    triggerVibration(25);
}

function triggerGameOver() {
    isGameOver = true;
    if(bossRespawnTimer) clearInterval(bossRespawnTimer);
    document.getElementById('ui-layer').style.display = 'none';
    document.getElementById('game-over').style.display = 'flex';
    document.getElementById('final-stats').innerText = `도달한 보스 레벨: Lv.${bossLevel} | 처치한 보스: ${defeatedBosses}마리 | 처치한 일반 주령: ${normalKillCount}마리`;
}

setInterval(() => {
    ['E', 'R', 'T', 'X'].forEach(k => {
        if(cooldowns[k] > 0) cooldowns[k] = Math.max(0, cooldowns[k] - 0.1);
        let elem = document.getElementById('cd-' + k.toLowerCase());
        if(elem) {
            if(cooldowns[k] > 0) {
                elem.style.display = 'flex'; elem.innerText = cooldowns[k].toFixed(1);
            } else elem.style.display = 'none';
        }
    });

    if(!isGameOver && Date.now() - lastHitTime >= 3000) {
        if(player.hp < player.maxHp) {
            player.hp = Math.min(player.maxHp, player.hp + (player.maxHp * 0.015));
        }
    }
}, 100);

function update() {
    if(isGameOver) return;
    if(screenShake > 0) screenShake--;
    if(player.hp <= 0) { triggerGameOver(); return; }

    if(playerStunTimer > 0) {
        playerStunTimer--;
    }

    performAutoAttack();

    let dx = 0, dy = 0;
    if(playerStunTimer <= 0) {
        if(keys['a']) { dx -= 1; player.facing = -1; }
        if(keys['d']) { dx += 1; player.facing = 1; }
        if(keys['w']) dy -= 1;
        if(keys['s']) dy += 1;
        if(dx !== 0 && dy !== 0) { dx *= 0.7071; dy *= 0.7071; }

        player.x = Math.max(30, Math.min(WORLD_WIDTH - 30, player.x + dx * player.speed));
        player.y = Math.max(30, Math.min(WORLD_HEIGHT - 30, player.y + dy * player.speed));
    }

    camera.x += (player.x - canvas.width / 2 - camera.x) * 0.1;
    camera.y += (player.y - canvas.height / 2 - camera.y) * 0.1;

    if(enemies.filter(e => !e.isBoss).length < 80) spawnCurse();

    // 고죠 무하한 패시브: 8초마다 3초간 발동
    gojoInfinityTimer = (gojoInfinityTimer + 1) % 480;
    let gojoInfinityActive = player.charType === 'Gojo' && gojoInfinityTimer < 180;
    
    if(sukunaFlash > 0) sukunaFlash--;

    // 스쿠나 푸가 화염
    sukunaFlames.forEach((f, fi) => {
        f.x += f.vx;
        f.y += f.vy;
        f.life--;
        f.radius = Math.min(f.maxRadius, f.radius + 1.8);

        enemies.forEach(e => {
            if(Math.hypot(e.x - f.x, e.y - f.y) < e.radius + f.radius) {
                e.hp -= f.damage / 8;
            }
        });

        if(f.life <= 0 || f.x < 0 || f.x > WORLD_WIDTH || f.y < 0 || f.y > WORLD_HEIGHT) {
            explosions.push({
                x: f.x, y: f.y, radius: 35, maxRadius: 280,
                color: 'rgba(255, 90, 30, 0.75)', life: 24, damage: f.damage
            });
            sukunaFlames.splice(fi, 1);
        }
    });

    if(activeDomain) {
        activeDomain.timer--;
        triggerVibration(4);

        if(activeDomain.type === 'Sukuna') {
            // 복마어주자 안에서는 주기적으로 무작위 참격 생성
            if(activeDomain.timer % 6 === 0) {
                for(let i=0; i<4; i++) {
                    let a = Math.random() * Math.PI * 2;
                    let r = Math.sqrt(Math.random()) * activeDomain.radius;
                    domainSlashes.push({
                        x: player.x + Math.cos(a) * r,
                        y: player.y + Math.sin(a) * r,
                        ang: Math.random() * Math.PI * 2,
                        length: 110 + Math.random() * 160,
                        life: 18, damage: 1500,
                        width: 4 + Math.random() * 3
                    });
                }
            }
            enemies.forEach(e => {
                if(Math.hypot(e.x - player.x, e.y - player.y) < activeDomain.radius) {
                    e.hp -= 38;
                }
            });
        }
        if(activeDomain.type === 'Gojo') {
            enemies.forEach(e => { 
                if(e.stunTimer <= 0) e.speed = 0; 
            });
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

    if(mahoraga) {
        mahoraga.life--;
        let bossTarget = activeBosses[0] || enemies[0];
        if(bossTarget) {
            let ang = Math.atan2(bossTarget.y - mahoraga.y, bossTarget.x - mahoraga.x);
            mahoraga.x += Math.cos(ang) * 4.5; mahoraga.y += Math.sin(ang) * 4.5;
        }
        if(mahoraga.life <= 0) mahoraga = null;
    }

    windTrails.forEach((wt, wti) => {
        wt.life--;
        wt.radius += 1.5;
        if(wt.life <= 0) windTrails.splice(wti, 1);
    });

    bloodSplatters.forEach((bs, bsi) => {
        bs.life--;
        bs.x += bs.vx;
        bs.y += bs.vy;
        if(bs.life <= 0) bloodSplatters.splice(bsi, 1);
    });

    chargingPurples.forEach((cp, cpi) => {
        cp.chargeTimer--;
        if(cp.radius < cp.maxRadius) {
            cp.radius += (cp.maxRadius - cp.radius) * 0.02;
        }

        if(cp.chargeTimer <= 0) {
            // 발사 순간 플레이어의 현재 위치에서 투사체 생성
            purpleProjectiles.push({
                x: player.x, y: player.y,
                vx: Math.cos(cp.ang) * 14, vy: Math.sin(cp.ang) * 14,
                radius: cp.maxRadius, maxLife: 300, life: 300, damage: cp.damage, hitEnemies: new Set()
            });
            triggerVibration(30);
            chargingPurples.splice(cpi, 1);
        }
    });

    purpleProjectiles.forEach((pp, ppi) => {
        pp.x += pp.vx;
        pp.y += pp.vy;
        pp.life--;

        enemies.forEach((e, ei) => {
            let dist = Math.hypot(e.x - pp.x, e.y - pp.y);
            if(dist < e.radius + pp.radius) {
                e.hp -= 800;
                purpleEffects.push({
                    x: e.x + (Math.random()-0.5)*30, y: e.y + (Math.random()-0.5)*30,
                    vx: (Math.random()-0.5)*4, vy: (Math.random()-0.5)*4,
                    radius: Math.random()*8+4, life: 15, color: '#e056fd'
                });
            }
        });

        if(pp.life <= 0 || pp.x < 0 || pp.x > WORLD_WIDTH || pp.y < 0 || pp.y > WORLD_HEIGHT) {
            purpleProjectiles.splice(ppi, 1);
        }
    });

    blackHoles.forEach((bh, bhi) => {
        bh.life--;
        bh.orbitAngle += 0.06;
        bh.x = player.x + Math.cos(bh.orbitAngle) * bh.orbitRadius;
        bh.y = player.y + Math.sin(bh.orbitAngle) * bh.orbitRadius;

        enemies.forEach(e => {
            let d = Math.hypot(bh.x - e.x, bh.y - e.y);
            if(d < bh.radius) {
                let pullAng = Math.atan2(bh.y - e.y, bh.x - e.x);
                e.x += Math.cos(pullAng) * 15;
                e.y += Math.sin(pullAng) * 15;
            }
        });

        enemyProjectiles.forEach((ep, epi) => {
            if(Math.hypot(bh.x - ep.x, bh.y - ep.y) < bh.radius) {
                enemyProjectiles.splice(epi, 1);
            }
        });

        if(bh.life <= 0) {
            blueOrbs.push({ x: bh.x, y: bh.y, radius: 100, life: 350 });
            explosions.push({x: bh.x, y: bh.y, radius: 180, maxRadius: 280, color: '#3742fa', life: 18, damage: bh.damage});
            blackHoles.splice(bhi, 1);
        }
    });

    blueOrbs.forEach((bo, boi) => {
        bo.life--;
        enemyProjectiles.forEach((ep, epi) => {
            if(Math.hypot(bo.x - ep.x, bo.y - ep.y) < bo.radius) {
                enemyProjectiles.splice(epi, 1);
            }
        });
        if(bo.life <= 0) blueOrbs.splice(boi, 1);
    });

    laserBeams.forEach((lb, lbi) => {
        lb.life--;
        if(lb.life <= 0) laserBeams.splice(lbi, 1);
    });

    enemyProjectiles.forEach((ep, epi) => {
        ep.x += ep.vx; ep.y += ep.vy;

        if(Math.hypot(player.x - ep.x, player.y - ep.y) < ep.radius + 15) {
            if(gojoInfinityActive) {
                enemyProjectiles.splice(epi, 1);
            } else {
                takeDamage(ep.damage);
                triggerVibration(8);
                enemyProjectiles.splice(epi, 1);
            }
        }
    });

    meleeAttacks.forEach((ma, mai) => {
        ma.life--;
        if(ma.life <= 0) meleeAttacks.splice(mai, 1);
    });

    highQualityShots.forEach((hs, hsi) => {
        hs.x += hs.vx; hs.y += hs.vy; hs.life--;
        if(hs.life <= 0) highQualityShots.splice(hsi, 1);
    });

    projectiles.forEach((p, pi) => {
        p.x += p.vx; p.y += p.vy;

        if(p.type === 'aka') {
            if(p.targetOrb) {
                let orbExists = blueOrbs.includes(p.targetOrb);
                if(orbExists) {
                    let reAng = Math.atan2(p.targetOrb.y - p.y, p.targetOrb.x - p.x);
                    p.vx = Math.cos(reAng) * 22;
                    p.vy = Math.sin(reAng) * 22;
                }
            }

            p.traveled += Math.hypot(p.vx, p.vy);
            let reachedTarget = p.traveled >= p.maxDist;
            let hitOrb = false;

            blueOrbs.forEach((bo, boi) => {
                if(Math.hypot(bo.x - p.x, bo.y - p.y) < bo.radius + p.radius) {
                    hitOrb = true;
                    blueOrbs.splice(boi, 1);
                }
            });

            let hitEnemy = false;
            enemies.forEach(e => {
                if(Math.hypot(e.x - p.x, e.y - p.y) < e.radius + p.radius) {
                    hitEnemy = true;
                }
            });

            if(reachedTarget || hitEnemy || hitOrb) {
                if(hitOrb || (p.targetOrb && Math.hypot(p.x - p.targetOrb.x, p.y - p.targetOrb.y) < 120)) {
                    showDialogue('「자폭 허식 · 茈」');
                    triggerVibration(50);

                    explosions.push({
                        x: p.x, y: p.y, radius: 40, maxRadius: 1100, color: 'rgba(168, 85, 247, 0.95)', life: 40, damage: 10000
                    });

                    enemies.forEach(e => {
                        e.hp -= 10000;
                        e.hp -= e.maxHp * 0.5;
                    });
                } else {
                    explosions.push({
                        x: p.x, y: p.y, radius: 30, maxRadius: 320, color: 'rgba(255, 71, 87, 0.85)', life: 20, damage: p.damage
                    });
                    triggerVibration(25);
                    enemies.forEach(e => {
                        if(Math.hypot(e.x - p.x, e.y - p.y) < 320) {
                            e.hp -= p.damage;
                        }
                    });
                }

                projectiles.splice(pi, 1);
                return;
            }
        }

        if(p.type === 'gojo_hq_basic') {
            p.trailTimer--;
            if(p.trailTimer <= 0) {
                p.trailTimer = 3;
                highQualityShots.push({ x: p.x, y: p.y, vx: 0, vy: 0, radius: 4, life: 10, color: '#00d2ff' });
            }
        }

        enemies.forEach((e) => {
            if(p.type !== 'aka' && Math.hypot(e.x - p.x, e.y - p.y) < e.radius + p.radius) {
                e.hp -= p.damage;
                if(p.type === 'normal' || p.type === 'gojo_hq_basic') {
                    for(let i=0; i<5; i++) {
                        highQualityShots.push({
                            x: p.x, y: p.y, vx: (Math.random()-0.5)*5, vy: (Math.random()-0.5)*5,
                            radius: Math.random()*3+2, life: 12, color: '#ffffff'
                        });
                    }
                    projectiles.splice(pi, 1);
                }
            }
        });
    });

    purpleEffects.forEach((pe, pei) => {
        pe.x += pe.vx; pe.y += pe.vy; pe.life--;
        if(pe.life <= 0) purpleEffects.splice(pei, 1);
    });

    explosions.forEach((ex, exi) => {
        ex.life--;
        if(ex.radius < ex.maxRadius) ex.radius += (ex.maxRadius - ex.radius) * 0.2;
        enemies.forEach(e => { if(Math.hypot(e.x - ex.x, e.y - ex.y) < ex.radius) e.hp -= ex.damage / 15; });
        if(ex.life <= 0) explosions.splice(exi, 1);
    });

    // 스쿠나 평타 쿨타임
    if(player.charType === 'Sukuna' && player.sukunaBasicTimer <= 0 &&
       player.sukunaBasicCooldown > 0) {
        player.sukunaBasicCooldown--;
    }

    // 스쿠나 평타 연사: 2초 동안 약 0.1초마다 긴 U자 참격
    if(player.charType === 'Sukuna' && player.sukunaBasicTimer > 0) {
        player.sukunaBasicTimer--;
        player.sukunaBasicShotTimer = (player.sukunaBasicShotTimer || 0) - 1;

        if(player.sukunaBasicShotTimer <= 0) {
            player.sukunaBasicShotTimer = 12;
            let a = getAutoAimAngle();
            slashes.push({
                x: player.x + Math.cos(a) * 55,
                y: player.y + Math.sin(a) * 55,
                ang: a,
                length: 300,
                curve: -32,
                life: 24,
                damage: 55,
                width: 9,
                color: '#000000',
                outline: '#ffffff',
                speed: 18,
                ranged: true
            });
        }
    }

    // 스쿠나 패시브: 8초 주기로 3초 동안 주변 적을 자동 참격
    sukunaPassiveTimer = (sukunaPassiveTimer + 1) % 480;
    if(player.charType === 'Sukuna' && sukunaPassiveTimer < 180) {
        if(sukunaPassiveTimer % 8 === 0) {
            enemies.forEach(e => {
                if(Math.hypot(e.x - player.x, e.y - player.y) < 230) {
                    let a = Math.atan2(e.y - player.y, e.x - player.x);
                    slashes.push({
                        x: e.x, y: e.y,
                        ang: a,
                        length: 120,
                        curve: -24,
                        life: 10,
                        damage: 700,
                        width: 6,
                        color: '#000000',
                        outline: '#ffffff'
                    });
                }
            });
        }
    }

    slashes.forEach((s, si) => {
        s.life--;
        if(s.ranged) {
            s.x += Math.cos(s.ang) * (s.speed || 18);
            s.y += Math.sin(s.ang) * (s.speed || 18);
        }
        enemies.forEach(e => {
            if(Math.hypot(e.x - s.x, e.y - s.y) < s.length / 2 + e.radius) {
                e.hp -= s.damage / 4;
            }
        });
        if(s.life <= 0) slashes.splice(si, 1);
    });

    domainSlashes.forEach((s, si) => {
        s.life--;
        enemies.forEach(e => {
            if(Math.hypot(e.x - s.x, e.y - s.y) < s.length / 2 + e.radius) {
                e.hp -= s.damage / 5;
            }
        });
        if(s.life <= 0) domainSlashes.splice(si, 1);
    });

    enemies.forEach((e, ei) => {
        if(e.stunTimer > 0) {
            e.stunTimer--;
            e.speed = 0;
        } else {
            e.speed = e.isBoss ? e.speed : (e.isRanged ? 2.0 : 2.8);

            let ang = Math.atan2(player.y - e.y, player.x - e.x);
            let dist = Math.hypot(player.x - e.x, player.y - e.y);
            e.facing = Math.cos(ang) >= 0 ? 1 : -1;

            if(e.isRanged && dist < 300) {
                e.x -= Math.cos(ang) * e.speed;
                e.y -= Math.sin(ang) * e.speed;
            } else {
                e.x += Math.cos(ang) * e.speed;
                e.y += Math.sin(ang) * e.speed;
            }

            e.attackCd = (e.attackCd || 0) + 1;
            e.skillCd = (e.skillCd || 0) + 1;

            if(e.isRanged && e.attackCd >= 80 && dist < 550 && e.speed > 0) {
                e.attackCd = 0;
                enemyProjectiles.push({
                    x: e.x, y: e.y, vx: Math.cos(ang)*8, vy: Math.sin(ang)*8,
                    damage: 18, radius: 6
                });
            }

            if(e.isBoss && e.speed > 0) {
                if(e.skillCd >= 60) {
                    e.skillCd = 0;
                    let patternType = Math.floor(Math.random() * 3);
                    if(patternType === 0) {
                        for(let i=-2; i<=2; i++) {
                            slashes.push({
                                x: e.x + Math.cos(ang+i*0.25)*40, y: e.y + Math.sin(ang+i*0.25)*40,
                                ang: ang + i*0.25, length: 120, life: 10, damage: e.dmg * 0.6
                            });
                        }
                    } else if(patternType === 1) {
                        explosions.push({
                            x: e.x, y: e.y,
                            radius: 20, maxRadius: 180, color: 'rgba(255, 71, 87, 0.55)', life: 20, damage: e.dmg * 1.0
                        });
                    } else {
                        for(let i=0; i<6; i++) {
                            let spreadAng = ang + (i - 2.5) * 0.2;
                            enemyProjectiles.push({
                                x: e.x, y: e.y, vx: Math.cos(spreadAng)*9, vy: Math.sin(spreadAng)*9,
                                damage: e.dmg * 0.7, radius: 7
                            });
                        }
                    }
                }
            }

            if(!e.isRanged && dist < e.radius + 30 && e.speed > 0) {
                if(e.attackCd >= (e.isBoss ? 20 : 40)) {
                    e.attackCd = 0;
                    let dmg = e.isBoss ? e.dmg : 14;
                    takeDamage(dmg);
                    triggerVibration(e.isBoss ? 15 : 6);
                    meleeAttacks.push({
                        x: (e.x + player.x) / 2, y: (e.y + player.y) / 2,
                        ang: ang, radius: e.isBoss ? e.radius + 10 : 25, life: 10, isBoss: e.isBoss
                    });
                }
            }
        }

        if(e.hp <= 0) {
            if(e.isBoss) {
                defeatedBosses++;
                bossLevel++;
                addUltFromKill();
                enemies.splice(ei, 1);
                if(bossLevel <= 100) {
                    startBossRespawnTimer();
                } else {
                    document.getElementById('boss-status').innerText = `🏆 모든 인간형 보스 정복 완료!`;
                    showDialogue(`🎉 축하합니다! 100단계 인간형 보스 정복!`);
                }
            } else {
                for(let b=0; b<12; b++) {
                    let bAng = Math.random() * Math.PI * 2;
                    let bSpd = Math.random() * 5 + 2;
                    bloodSplatters.push({
                        x: e.x, y: e.y,
                        vx: Math.cos(bAng) * bSpd, vy: Math.sin(bAng) * bSpd,
                        radius: Math.random() * 4 + 2, life: Math.random() * 30 + 20
                    });
                }
                normalKillCount++;
                addUltFromKill();
                enemies.splice(ei, 1);
            }
        }
    });

    document.getElementById('hp-bar').style.width = Math.max(0, (player.hp / player.maxHp * 100)) + '%';
    document.getElementById('ult-bar').style.width = Math.min(100, (player.ultEnergy / player.maxUlt * 100)) + '%';
    document.getElementById('kill-status').innerText = `처치한 보스: ${defeatedBosses} / 100`;
    document.getElementById('mob-kill-status').innerText = `처치한 일반 주령: ${normalKillCount}마리`;
}

function drawPlayerSprite(p) {
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.scale(p.facing, 1);

    if(p.charType === 'Gojo') {
        ctx.shadowBlur = 20; ctx.shadowColor = '#70a1ff';
        ctx.fillStyle = '#0a0a14'; ctx.fillRect(-10, -16, 20, 32);
        ctx.fillStyle = '#ffffff'; ctx.fillRect(-9, -32, 18, 12);
        ctx.fillStyle = '#70a1ff'; ctx.fillRect(-7, -24, 14, 4);
        ctx.shadowBlur = 0;
    } else if(p.charType === 'Sukuna') {
        ctx.shadowBlur = 24; ctx.shadowColor = '#dcaaff';
        ctx.fillStyle = '#111'; ctx.fillRect(-11, -17, 22, 34);
        ctx.fillStyle = '#ff7675'; ctx.fillRect(-10, -33, 20, 11);
        ctx.fillStyle = '#ff4757'; ctx.fillRect(-7, -24, 14, 3);
        // 얼굴의 특징적인 문양
        ctx.strokeStyle = '#8b0000'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(-7,-28); ctx.lineTo(-2,-26); ctx.moveTo(7,-28); ctx.lineTo(2,-26); ctx.stroke();
        ctx.shadowBlur = 0;
    } else {
        ctx.fillStyle = '#0f172a'; ctx.fillRect(-10, -16, 20, 32);
        ctx.fillStyle = '#1e293b'; ctx.fillRect(-11, -34, 22, 12);
    }
    ctx.restore();
}

function drawEnemySprite(e) {
    ctx.save();
    ctx.translate(e.x, e.y);
    ctx.scale(e.facing || 1, 1);

    if(e.isBoss) {
        ctx.shadowBlur = 20; ctx.shadowColor = e.aura;
        ctx.fillStyle = '#2d132c'; ctx.fillRect(-12, -18, 24, 36);
        ctx.fillStyle = e.stunTimer > 0 ? '#34495e' : '#ff7675'; 
        ctx.fillRect(-10, -36, 20, 16);
        ctx.fillStyle = '#ff4757';
        ctx.fillRect(-6, -30, 4, 3);
        ctx.fillRect(2, -30, 4, 3);
        ctx.strokeStyle = e.aura; ctx.lineWidth = 2;
        ctx.strokeRect(-14, -40, 28, 58);
        ctx.shadowBlur = 0;

        ctx.fillStyle = '#ff4757';
        ctx.font = 'bold 14px Consolas';
        ctx.textAlign = 'center';
        ctx.fillText(`[LV.${e.level}]`, 0, -48);
    } else {
        if(e.isRanged) {
            ctx.fillStyle = e.stunTimer > 0 ? '#34495e' : '#8e44ad';
            ctx.beginPath();
            ctx.moveTo(0, -e.radius);
            ctx.lineTo(e.radius, 0);
            ctx.lineTo(0, e.radius);
            ctx.lineTo(-e.radius, 0);
            ctx.closePath();
            ctx.fill();
            ctx.strokeStyle = '#e056fd'; ctx.lineWidth = 2; ctx.stroke();
        } else {
            ctx.fillStyle = e.stunTimer > 0 ? '#34495e' : '#1e272e';
            ctx.beginPath(); ctx.arc(0, 0, e.radius, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#57606f'; ctx.lineWidth = 2; ctx.stroke();
            
            ctx.fillStyle = '#e74c3c';
            ctx.beginPath(); ctx.arc(-6, -4, 4, 0, Math.PI*2); ctx.fill();
            ctx.beginPath(); ctx.arc(6, -4, 4, 0, Math.PI*2); ctx.fill();
        }
    }
    ctx.restore();
}

function draw() {
    ctx.save();
    if(screenShake > 0) ctx.translate((Math.random()-0.5)*screenShake, (Math.random()-0.5)*screenShake);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // 월드 경계만 흰색으로 표시 (화면 전체를 덮지 않음)
    ctx.save();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 24;
    ctx.strokeRect(12, 12, WORLD_WIDTH - 24, WORLD_HEIGHT - 24);
    ctx.restore();

if(sukunaFlash > 0 && player.charType === 'Sukuna') {
        ctx.fillStyle = `rgba(255, 30, 55, ${Math.min(0.16, sukunaFlash / 220)})`;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    ctx.translate(-camera.x, -camera.y);

    windTrails.forEach(wt => {
        let alpha = wt.life / 15;
        ctx.save();
        ctx.strokeStyle = `rgba(180, 230, 255, ${alpha})`;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(wt.x, wt.y, wt.radius, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
    });

    if(activeDomain) {
        if(activeDomain.type === 'Gojo') {
            ctx.fillStyle = 'rgba(5, 5, 20, 0.85)';
            ctx.fillRect(camera.x, camera.y, canvas.width, canvas.height);
            ctx.fillStyle = '#70a1ff';
            for(let i=0; i<30; i++) {
                let sx = camera.x + (Math.sin(i * 99 + Date.now()*0.002) * 0.5 + 0.5) * canvas.width;
                let sy = camera.y + (Math.cos(i * 33 + Date.now()*0.002) * 0.5 + 0.5) * canvas.height;
                ctx.beginPath(); ctx.arc(sx, sy, 3, 0, Math.PI*2); ctx.fill();
            }
        } else {
            ctx.fillStyle = 'rgba(45, 12, 65, 0.28)';
            ctx.fillRect(camera.x, camera.y, canvas.width, canvas.height);

            // 복마어주자 영역 테두리
            ctx.save();
            ctx.strokeStyle = 'rgba(220, 170, 255, 0.55)';
            ctx.lineWidth = 5;
            ctx.shadowBlur = 30;
            ctx.shadowColor = '#dcaaff';
            ctx.beginPath();
            ctx.arc(player.x, player.y, activeDomain.radius || 760, 0, Math.PI * 2);
            ctx.stroke();
            ctx.restore();
        }
    }

    ctx.strokeStyle = 'rgba(168, 85, 247, 0.06)'; ctx.lineWidth = 1;
    for(let x=0; x<WORLD_WIDTH; x+=100) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, WORLD_HEIGHT); ctx.stroke(); }
    for(let y=0; y<WORLD_HEIGHT; y+=100) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(WORLD_WIDTH, y); ctx.stroke(); }

    bloodSplatters.forEach(bs => {
        ctx.fillStyle = '#c0392b';
        ctx.beginPath();
        ctx.arc(bs.x, bs.y, bs.radius, 0, Math.PI * 2);
        ctx.fill();
    });

    blackHoles.forEach(bh => {
        ctx.shadowBlur = 40; ctx.shadowColor = '#3742fa';
        ctx.fillStyle = 'rgba(10, 10, 50, 0.9)';
        ctx.beginPath(); ctx.arc(bh.x, bh.y, 95, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#70a1ff'; ctx.lineWidth = 6; ctx.stroke();
        ctx.shadowBlur = 0;
    });

    blueOrbs.forEach(bo => {
        let alpha = bo.life / 350;
        ctx.shadowBlur = 40; ctx.shadowColor = '#0026ff';
        ctx.fillStyle = `rgba(0, 38, 255, ${alpha})`;
        ctx.beginPath(); ctx.arc(bo.x, bo.y, bo.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = `rgba(100, 200, 255, ${alpha})`; ctx.lineWidth = 7; ctx.stroke();
        ctx.shadowBlur = 0;
    });

    // 차징 중인 무라사키가 플레이어의 현재 위치(player.x, player.y)를 따라다니도록 렌더링
    chargingPurples.forEach(cp => {
        ctx.save();
        ctx.shadowBlur = 40;
        ctx.shadowColor = '#a855f7';
        ctx.fillStyle = '#7000ff';
        ctx.beginPath();
        ctx.arc(player.x, player.y, cp.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#e056fd';
        ctx.lineWidth = 6;
        ctx.stroke();
        ctx.restore();
    });

    purpleProjectiles.forEach(pp => {
        ctx.save();
        ctx.shadowBlur = 90;
        ctx.shadowColor = '#a855f7';
        ctx.fillStyle = '#7000ff';
        ctx.beginPath();
        ctx.arc(pp.x, pp.y, pp.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#e056fd';
        ctx.lineWidth = 14;
        ctx.stroke();
        ctx.restore();
    });

    if(mahoraga) {
        ctx.fillStyle = '#ffffff';
        ctx.beginPath(); ctx.arc(mahoraga.x, mahoraga.y, 30, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#f1c40f'; ctx.lineWidth = 4; ctx.stroke();
    }

    enemies.forEach(e => drawEnemySprite(e));

    enemyProjectiles.forEach(ep => {
        ctx.fillStyle = '#ff4757';
        ctx.beginPath(); ctx.arc(ep.x, ep.y, ep.radius, 0, Math.PI*2); ctx.fill();
    });

    meleeAttacks.forEach(ma => {
        ctx.save();
        ctx.translate(ma.x, ma.y);
        ctx.rotate(ma.ang);
        ctx.strokeStyle = ma.isBoss ? '#ff4757' : '#ff6b81';
        ctx.lineWidth = ma.isBoss ? 6 : 4;
        ctx.beginPath();
        ctx.arc(0, 0, ma.radius, -Math.PI/3, Math.PI/3);
        ctx.stroke();
        ctx.restore();
    });

    // 일반 참격: 가운데가 밝고 양끝이 날카로운 스쿠나식 참격
    slashes.forEach(s => {
        ctx.save();
        ctx.translate(s.x, s.y);
        ctx.rotate(s.ang);
        ctx.shadowBlur = 18;
        ctx.shadowColor = '#ff334d';
        ctx.strokeStyle = s.color || '#ff4757';
        ctx.lineWidth = s.width || 5;
        ctx.beginPath();
        ctx.moveTo(-s.length/2, 0);
        ctx.quadraticCurveTo(0, -10, s.length/2, 0);
        ctx.stroke();
        ctx.strokeStyle = 'rgba(255,255,255,0.9)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(-s.length/2 + 8, 0);
        ctx.lineTo(s.length/2 - 8, 0);
        ctx.stroke();
        ctx.restore();
    });

    domainSlashes.forEach(s => {
        let alpha = Math.max(0, Math.min(1, s.life / 18));
        ctx.save();
        ctx.translate(s.x, s.y);
        ctx.rotate(s.ang);
        ctx.shadowBlur = 22;
        ctx.shadowColor = '#ff1744';
        ctx.strokeStyle = `rgba(255, 71, 87, ${alpha})`;
        ctx.lineWidth = s.width || 5;
        ctx.beginPath();
        ctx.moveTo(-s.length/2, 0);
        ctx.quadraticCurveTo(0, -14, s.length/2, 0);
        ctx.stroke();
        ctx.strokeStyle = `rgba(255,255,255,${alpha * 0.8})`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(-s.length/2 + 10, 0);
        ctx.lineTo(s.length/2 - 10, 0);
        ctx.stroke();
        ctx.restore();
    });

    // 푸가: 두꺼운 붉은 화살 + 밝은 중심
    sukunaFlames.forEach(f => {
        ctx.save();
        ctx.translate(f.x, f.y);
        ctx.rotate(Math.atan2(f.vy, f.vx));
        ctx.shadowBlur = 30;
        ctx.shadowColor = '#ff1f3d';

        // 화살 몸통
        ctx.fillStyle = '#8b0000';
        ctx.beginPath();
        ctx.moveTo(-55, -f.radius * 0.48);
        ctx.lineTo(28, -f.radius * 0.48);
        ctx.lineTo(28, -f.radius);
        ctx.lineTo(75, 0);
        ctx.lineTo(28, f.radius);
        ctx.lineTo(28, f.radius * 0.48);
        ctx.lineTo(-55, f.radius * 0.48);
        ctx.closePath();
        ctx.fill();

        ctx.fillStyle = '#ff334d';
        ctx.beginPath();
        ctx.moveTo(-48, -f.radius * 0.28);
        ctx.lineTo(25, -f.radius * 0.28);
        ctx.lineTo(25, -f.radius * 0.65);
        ctx.lineTo(58, 0);
        ctx.lineTo(25, f.radius * 0.65);
        ctx.lineTo(25, f.radius * 0.28);
        ctx.lineTo(-48, f.radius * 0.28);
        ctx.closePath();
        ctx.fill();

        // 뒤쪽 화염 꼬리
        ctx.fillStyle = 'rgba(255,90,20,0.75)';
        ctx.beginPath();
        ctx.moveTo(-55, -f.radius*0.35);
        ctx.lineTo(-110, 0);
        ctx.lineTo(-55, f.radius*0.35);
        ctx.closePath();
        ctx.fill();

        ctx.restore();
    });

    highQualityShots.forEach(hs => {
        ctx.fillStyle = hs.color;
        ctx.beginPath(); ctx.arc(hs.x, hs.y, hs.radius, 0, Math.PI*2); ctx.fill();
    });

    purpleEffects.forEach(pe => {
        ctx.fillStyle = pe.color;
        ctx.beginPath(); ctx.arc(pe.x, pe.y, pe.radius, 0, Math.PI*2); ctx.fill();
    });

    explosions.forEach(ex => {
        ctx.fillStyle = ex.color;
        ctx.beginPath(); ctx.arc(ex.x, ex.y, ex.radius, 0, Math.PI*2); ctx.fill();
    });

    projectiles.forEach(p => {
        ctx.save();
        if(p.type === 'gojo_hq_basic') {
            ctx.shadowBlur = 20; ctx.shadowColor = '#00d2ff';
            ctx.fillStyle = '#ffffff';
            ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#00d2ff'; ctx.lineWidth = 4; ctx.stroke();
        } else if(p.type === 'aka') {
            ctx.shadowBlur = 35; ctx.shadowColor = '#ff4757';
            ctx.fillStyle = '#ff6b81';
            ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 4; ctx.stroke();
        } else {
            ctx.shadowBlur = 10; ctx.shadowColor = '#70a1ff';
            ctx.fillStyle = p.color || '#3742fa';
            ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
        }
        ctx.restore();
    });

    if(gojoInfinityActive) {
        ctx.save();
        ctx.strokeStyle = 'rgba(112, 161, 255, 0.85)';
        ctx.lineWidth = 5;
        ctx.shadowBlur = 28;
        ctx.shadowColor = '#70a1ff';
        ctx.beginPath();
        ctx.arc(player.x, player.y, 42 + Math.sin(Date.now()*0.01)*3, 0, Math.PI*2);
        ctx.stroke();
        ctx.strokeStyle = 'rgba(255,255,255,0.65)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(player.x, player.y, 50, 0, Math.PI*2);
        ctx.stroke();
        ctx.restore();
    }

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
