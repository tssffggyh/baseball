import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="주술회전: 허식 무라사키 연출 개정판")

st.markdown(
    """
    <style>
        .main .block-container { max-width: 100% !important; padding: 0rem !important; }
        iframe { width: 100% !important; border: none; }
        header, footer { visibility: hidden; }
    </style>
""",
    unsafe_allow_html=True,
)

game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background-color: #020204; color: #fff;
        font-family: 'Consolas', monospace;
        display: flex; justify-content: center; align-items: center;
        width: 100vw; height: 100vh; overflow: hidden;
    }
    #game-container {
        position: relative; width: 100vw; height: 100vh;
        overflow: hidden; background: #000;
    }
    canvas { display: block; cursor: crosshair; }
    
    #ui-layer {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; padding: 20px 30px;
        display: flex; flex-direction: column; justify-content: space-between; z-index: 10;
    }
    .hud-card {
        background: rgba(10, 10, 18, 0.85); backdrop-filter: blur(10px);
        padding: 15px 25px; border-radius: 12px;
        border: 1px solid rgba(168, 85, 247, 0.4); box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    }
    .bar-outer {
        width: 280px; height: 12px; background: rgba(255,255,255,0.1);
        border-radius: 6px; overflow: hidden; margin: 4px 0 10px 0;
    }
    .bar-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff4757, #ff6b81); transition: width 0.1s; }
    .bar-ult { width: 0%; height: 100%; background: linear-gradient(90deg, #a855f7, #e056fd); transition: width 0.1s; }
    
    #boss-hud {
        position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
        width: 580px; background: rgba(15, 5, 5, 0.9);
        border: 2px solid #ff4757; border-radius: 10px; padding: 12px 20px;
        text-align: center; display: none; z-index: 15;
    }
    .boss-bar-outer { width: 100%; height: 16px; background: rgba(255,255,255,0.1); border-radius: 8px; overflow: hidden; margin-top: 5px; }
    .boss-bar-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff4757, #e84118); transition: width 0.1s; }

    .skill-container { display: flex; gap: 8px; margin-top: 8px; }
    .skill-icon {
        position: relative; width: 50px; height: 50px; background: rgba(255,255,255,0.08);
        border: 1px solid #a855f7; border-radius: 10px;
        display: flex; flex-direction: column; justify-content: space-between; align-items: center;
        padding: 4px; font-size: 9px; font-weight: bold; color: #fff; overflow: hidden;
    }
    .skill-key { font-size: 12px; color: #e056fd; }
    .cooldown-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.75); color: #ff4757; font-size: 14px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; display: none;
    }

    #dialogue-box {
        position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%);
        background: rgba(5, 5, 12, 0.95); border: 2px solid #a855f7;
        border-radius: 12px; padding: 12px 30px; text-align: center;
        box-shadow: 0 0 30px rgba(168, 85, 247, 0.8);
        opacity: 0; transition: opacity 0.15s ease-in-out; pointer-events: none; z-index: 20;
    }
    #dialogue-text { font-size: 24px; font-weight: bold; color: #f3e8ff; letter-spacing: 3px; }

    #class-select, #game-over {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(3, 3, 6, 0.94); backdrop-filter: blur(15px);
        display: flex; flex-direction: column; justify-content: center; z-index: 100;
        align-items: center; pointer-events: auto;
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
    
    <div id="boss-hud">
        <div id="boss-name" style="color:#ff4757; font-weight:bold; font-size:16px;">[LV.1] 보스</div>
        <div class="boss-bar-outer"><div id="boss-hp-bar" class="boss-bar-hp"></div></div>
    </div>

    <div id="ui-layer">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div class="hud-card">
                <div id="char-name" style="color:#a855f7; font-weight:bold; font-size:16px;">주술사</div>
                <div style="font-size:10px; color:#aaa; margin-top:4px;">체력 (HP) <span style="color:#e056fd;">[영역전개 지속시간 대폭 연장]</span></div>
                <div class="bar-outer"><div id="hp-bar" class="bar-hp"></div></div>
                <div style="font-size:10px; color:#aaa;">궁극기 게이지 (ULT) [X]</div>
                <div class="bar-outer"><div id="ult-bar" class="bar-ult"></div></div>
                
                <div class="skill-container">
                    <div class="skill-icon" style="border-color:#3498db;">
                        <span class="skill-key" style="color:#3498db;">AUTO</span><span>오토에임</span>
                    </div>
                    <div class="skill-icon">
                        <span class="skill-key">Q</span><span id="sk-q">신속아오</span>
                        <div id="cd-q" class="cooldown-overlay">0</div>
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
                <div id="boss-status" style="font-size:14px; color:#ff4757; font-weight:bold;">보스 소환 대기 중...</div>
                <div id="kill-status" style="font-size:13px; color:#aaa; margin-top:6px;">처치한 보스: 0 / 100</div>
                <div id="mob-kill-status" style="font-size:13px; color:#a855f7; margin-top:2px; font-weight:bold;">처치한 일반 주령: 0마리</div>
            </div>
        </div>
    </div>

    <div id="dialogue-box">
        <div id="dialogue-text">무량공처</div>
    </div>

    <div id="class-select">
        <h1 style="color:#f3e8ff; font-size:48px; letter-spacing:2px; text-shadow:0 0 20px #a855f7;">JUJUTSU KAISEN</h1>
        <p style="color:#a1a1aa; margin-top:10px;">[고죠 울트라 하이퀄리티 스킨 + 초소형 아오 + 지연형 허식 무라사키 + 잔해 아카 연계 자폭]</p>
        <div class="card-group">
            <div class="card" id="card-gojo">
                <h2 style="color:#70a1ff;">👁️ 고죠 사토루</h2>
                <p>
                    • Q: 신속 아오 폭주 (무적 버프)<br>
                    • E: 술식반전 · 「赤」 (잔해 기폭 연계)<br>
                    • R: 술식순전 · 「蒼」 (초소형화)<br>
                    • T: 허식 「茈」 (지연형 팽창 ➔ 늦게 발사)<br>
                    • X: 무량공처
                </p>
            </div>
            <div class="card" id="card-sukuna">
                <h2 style="color:#ff4757;">👹 양면 스쿠나</h2>
                <p>
                    • Q: 신속 아오 폭주 (무적 버프)<br>
                    • E: 해(解) / R: 팔(捌)<br>
                    • T: 푸가(🔥) / X: 복마어주자
                </p>
            </div>
            <div class="card" id="card-megumi">
                <h2 style="color:#2ecc71;">🐺 후시구로 메구미</h2>
                <p>
                    • Q: 신속 아오 폭주 (무적 버프)<br>
                    • E: 누에 / R: 옥견<br>
                    • T: 그림자 속박 / X: 마허라
                </p>
            </div>
        </div>
    </div>

    <div id="game-over" style="display:none;">
        <h1 style="color:#ff4757; font-size:56px; letter-spacing:3px;">YOU DIED</h1>
        <p style="color:#aaa; margin-top:10px; font-size:18px;" id="final-stats">주령들의 공격으로 사망했습니다.</p>
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
purpleAudio.volume = 1.0;

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
let isGameOver = false;
let screenShake = 0;
let camera = { x: 0, y: 0 };
let dialogueTimeout = null;

let lastHitTime = Date.now();
let bossRespawnTimer = null;
let respawnCountdown = 0;
let gojoDomainCount = 0;

let limitlessTimer = 0;
let limitlessActive = false;
let limitlessDurationCounter = 0;

let speedAoActive = false;
let speedAoTimer = 0; 

let bloodSplatters = [];
let permanentCraters = []; 
let debrisList = []; 

let player = {
    x: WORLD_WIDTH / 2, y: WORLD_HEIGHT / 2,
    baseSpeed: 6.5, speed: 6.5, hp: 300, maxHp: 300,
    ultEnergy: 0, maxUlt: 100,
    charType: 'Gojo', facing: 1, lastAttack: 0
};

let cooldowns = { Q: 0, E: 0, R: 0, T: 0, X: 0 };
let maxCooldowns = {
    Gojo: { Q: 29, E: 5, R: 13, T: 16, X: 0 },
    Sukuna: { Q: 29, E: 7, R: 14, T: 21, X: 0 },
    Megumi: { Q: 29, E: 8, R: 15, T: 23, X: 0 }
};

let dialogues = {
    Gojo: { Q: '신속 아오 폭주 (무적)', E: '술식반전 · 「赤」', R: '술식순전 · 「蒼」', T: '허식 「茈」', X: '료이키텐카이 무량공처' },
    Sukuna: { Q: '신속 아오 폭주 (무적)', E: '참격 「해(解)」', R: '참격 「팔(捌)」', T: '「푸가(🔥)」', X: '영역전개 「복마어주자」' },
    Megumi: { Q: '신속 아오 폭주 (무적)', E: '십종영법술 「누에」', R: '십종영법술 「옥견」', T: '그림자 속박', X: '마허라 소환' }
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
let purpleProjectiles = []; 
let laserBeams = [];
let meleeAttacks = [];
let enemies = [];
let highQualityShots = []; 
let windTrails = [];      

const BOSS_COLORS = [
    { bg: '#e74c3c', aura: '#ff7675', spikes: 5 },
    { bg: '#8e44ad', aura: '#a855f7', spikes: 7 },
    { bg: '#2980b9', aura: '#3498db', spikes: 9 },
    { bg: '#d35400', aura: '#e67e22', spikes: 11 },
    { bg: '#27ae60', aura: '#2ecc71', spikes: 13 },
    { bg: '#f1c40f', aura: '#f39c12', spikes: 15 },
    { bg: '#2c3e50', aura: '#bdc3c7', spikes: 18 }
];

const BOSS_NAMES = ["화곤", "다라", "죠고", "하나미", "마히토", "두면사신", "바르바토스", "아스타로트", "루시퍼", "황혼의 주령"];

function getBossData(lvl) {
    let baseHp = 1800;
    let scaledHp = Math.floor(baseHp * Math.pow(lvl, 1.68));
    let nameIdx = (lvl - 1) % BOSS_NAMES.length;
    let colorStyle = BOSS_COLORS[(lvl - 1) % BOSS_COLORS.length];
    let title = lvl > 80 ? "신화급 주령" : (lvl > 50 ? "재앙급 주령" : (lvl > 20 ? "상급 특급주령" : "특급주령"));

    return {
        level: lvl, name: `${title} - ${BOSS_NAMES[nameIdx]} [${lvl}/100]`,
        hp: scaledHp, radius: Math.min(135, 55 + Math.floor(lvl * 0.75)),
        speed: Math.min(4.8, 2.2 + (lvl * 0.026)), dmg: 28 + Math.floor(lvl * 3.0),
        color: colorStyle.bg, aura: colorStyle.aura, spikes: colorStyle.spikes
    };
}

window.addEventListener('keydown', e => {
    initAudio();
    let k = e.key.toLowerCase();
    keys[k] = true;
    if(k === 'q') castSkill('Q');
    if(k === 'e') castSkill('E');
    if(k === 'r') castSkill('R');
    if(k === 't') castSkill('T');
    if(k === 'x') castSkill('X');
});
window.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

function addUlt(amount) { player.ultEnergy = Math.min(player.maxUlt, player.ultEnergy + (amount * 0.35 * 1.5)); }

function takeDamage(damage) {
    if(speedAoActive) return; 
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
    initAudio();
    player.charType = type;
    document.getElementById('class-select').style.display = 'none';
    
    let skNames = {
        'Gojo': ['신속아오', '아카', '아오', '무라사키', '무량공처'],
        'Sukuna': ['신속아오', '해(解)', '팔(捌)', '푸가', '복마어주자'],
        'Megumi': ['신속아오', '누에', '옥견', '그림자', '마허라']
    };
    
    document.getElementById('char-name').innerText = type === 'Gojo' ? '고죠 사토루' : (type === 'Sukuna' ? '양면 스쿠나' : '후시구로 메구미');
    document.getElementById('sk-q').innerText = skNames[type][0];
    document.getElementById('sk-e').innerText = skNames[type][1];
    document.getElementById('sk-r').innerText = skNames[type][2];
    document.getElementById('sk-t').innerText = skNames[type][3];

    for(let i=0; i<50; i++) spawnCurse();
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
    if(isGameOver) return;
    let now = Date.now();
    let attackInterval = (player.charType === 'Gojo') ? 700 : 600;
    if(now - player.lastAttack < attackInterval) return;
    player.lastAttack = now;

    let ang = getAutoAimAngle();

    addUlt(0.8);
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
        slashes.push({x: player.x + Math.cos(ang)*30, y: player.y + Math.sin(ang)*30, ang: ang, length: 80, life: 6, damage: 70});
    } else {
        projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang)*14, vy: Math.sin(ang)*14, damage: 60, radius: 8, color: '#2ecc71', type:'normal'});
    }
}

function castSkill(key) {
    if(isGameOver) return;
    if(cooldowns[key] > 0) return;
    if(key === 'X' && player.ultEnergy < player.maxUlt) return;

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

    if(key === 'Q') {
        cooldowns.Q = maxCooldowns[player.charType].Q;
        speedAoActive = true;
        speedAoTimer = 500;
        playVoiceAndSound('ao_voice');
        triggerVibration(25);
        addUlt(3.0);
    } else if(key === 'E') {
        cooldowns.E = maxCooldowns[player.charType].E;
        addUlt(2.5);
        
        if(player.charType === 'Gojo') {
            playVoiceAndSound('aka');
            triggerVibration(30);
            projectiles.push({
                x: player.x, y: player.y, 
                targetX: targetX, targetY: targetY,
                vx: Math.cos(ang)*18, vy: Math.sin(ang)*18,
                type: 'aka', damage: 3500, radius: 28, maxDist: 350, traveled: 0
            });
        } else if(player.charType === 'Sukuna') {
            for(let i=-2; i<=2; i++) {
                slashes.push({ x: player.x, y: player.y, ang: ang + i*0.2, length: 220, life: 14, damage: 1500 });
            }
        } else {
            explosions.push({x: targetX, y: targetY, radius: 70, maxRadius: 70, color: '#f1c40f', life: 15, damage: 1200});
        }
    } else if(key === 'R') {
        cooldowns.R = maxCooldowns[player.charType].R;
        addUlt(4.0);
        
        if(player.charType === 'Gojo') {
            playVoiceAndSound('ao_voice');
            triggerVibration(25);
            // 아오 크기를 훨씬 작게 축소 (반경 70으로 대폭 축소)
            blackHoles.push({
                orbitAngle: ang, orbitRadius: 80, radius: 140, life: 180, damage: 3000, x: player.x, y: player.y
            });
        } else if(player.charType === 'Sukuna') {
            for(let i=0; i<12; i++) {
                slashes.push({
                    x: targetX + (Math.random()-0.5)*200, y: targetY + (Math.random()-0.5)*200,
                    ang: Math.random()*Math.PI*2, length: 160, life: 12, damage: 1800
                });
            }
        } else {
            projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang)*15, vy: Math.sin(ang)*15, type:'normal', damage: 1500, radius: 10, color: '#2ecc71'});
        }
    } else if(key === 'T') {
        cooldowns.T = maxCooldowns[player.charType].T;
        if(player.charType === 'Gojo') {
            addUlt(6.0);
            playVoiceAndSound('purple_voice');
            triggerVibration(45);
            
            // 무라사키를 조금 더 늦게 나가게 타이머와 팽창 단계를 더 길게 설정 (팽창 타이머 80, 대기 30)
            purpleProjectiles.push({
                x: player.x + Math.cos(ang)*30, 
                y: player.y + Math.sin(ang)*30,
                vx: Math.cos(ang) * 13, 
                vy: Math.sin(ang) * 13,
                phase: 'expanding', 
                timer: 80, 
                currentRadius: 4,
                maxRadius: 140,
                life: 350, 
                damage: 9999, 
                ang: ang
            });
        } else if(player.charType === 'Sukuna') {
            addUlt(5.0);
            explosions.push({x: targetX, y: targetY, radius: 180, maxRadius: 180, color: '#e67e22', life: 30, damage: 4000});
        } else {
            addUlt(5.0);
            enemies.forEach(e => { if(Math.hypot(e.x - player.x, e.y - player.y) < 350) e.speed = 0.5; });
        }
    } else if(key === 'X') {
        player.ultEnergy = 0;
        if(player.charType === 'Gojo') {
            activeDomain = { type: 'Gojo', timer: 1200 };
        } else if(player.charType === 'Sukuna') {
            activeDomain = { type: 'Sukuna', timer: 1000 };
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
    enemies.push({
        x: x, y: y, radius: isRanged ? 18 : 22,
        hp: isRanged ? 100 : 150, maxHp: isRanged ? 100 : 150,
        speed: isRanged ? 2.0 : 2.8,
        isBoss: false, isRanged: isRanged, attackCd: 0
    });
}

function startBossRespawnTimer() {
    respawnCountdown = 5;
    let statusElem = document.getElementById('boss-status');
    statusElem.innerText = `다음 보스 소환까지: ${respawnCountdown}초`;

    bossRespawnTimer = setInterval(() => {
        respawnCountdown--;
        if(respawnCountdown > 0) {
            statusElem.innerText = `다음 보스 소환까지: ${respawnCountdown}초`;
        } else {
            clearInterval(bossRespawnTimer);
            bossRespawnTimer = null;
            statusElem.innerText = `⚠️ 보스 교전 중!`;
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
        color: cfg.color, aura: cfg.aura, spikes: cfg.spikes,
        isBoss: true, attackCd: 0, skillCd: 0, ultCd: 0
    };
    
    enemies.push(boss);
    document.getElementById('boss-status').innerText = `⚠️ 보스 교전 중!`;
    showDialogue(`⚠️ [LV.${cfg.level}] 보스 출현!`);
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
    ['Q', 'E', 'R', 'T', 'X'].forEach(k => {
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

    performAutoAttack();

    if(speedAoActive) {
        speedAoTimer--;
        player.speed = player.baseSpeed * 2.5; 
        
        windTrails.push({
            x: player.x, y: player.y, radius: Math.random() * 40 + 30, life: 15, alpha: 0.7
        });

        enemies.forEach(e => {
            let dist = Math.hypot(e.x - player.x, e.y - player.y);
            if(dist < e.radius + 30) {
                e.hp -= 120.0;
            }
        });

        if(speedAoTimer <= 0) {
            speedAoActive = false;
            player.speed = player.baseSpeed;
        }
    } else {
        player.speed = player.baseSpeed;
    }

    if(player.charType === 'Gojo') {
        limitlessTimer += 0.016; 
        if(!limitlessActive && limitlessTimer >= 7.0) {
            limitlessActive = true;
            limitlessDurationCounter = 180; 
        }
        if(limitlessActive) {
            limitlessDurationCounter--;
            if(limitlessDurationCounter <= 0) {
                limitlessActive = false;
                limitlessTimer = 0; 
            }
        }
    }

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

    if(enemies.filter(e => !e.isBoss).length < 80) spawnCurse();

    if(activeDomain) {
        activeDomain.timer--;
        triggerVibration(4);
        if(activeDomain.type === 'Gojo') {
            enemies.forEach(e => { e.speed = 0; });
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

    debrisList.forEach((d, di) => {
        d.life--;
        if(d.life <= 0) debrisList.splice(di, 1);
    });

    purpleProjectiles.forEach((pp, ppi) => {
        pp.life--;
        if(pp.phase === 'expanding') {
            pp.timer--;
            let progress = (80 - pp.timer) / 80;
            pp.currentRadius = 4 + (pp.maxRadius - 4) * progress;
            
            if(pp.timer <= 0) {
                pp.phase = 'charging';
                pp.timer = 25; 
                triggerVibration(20);
            }
        } else if(pp.phase === 'charging') {
            pp.timer--;
            if(pp.timer <= 0) {
                pp.phase = 'firing';
                triggerVibration(35);
                permanentCraters.push({ x: pp.x, y: pp.y, radius: pp.maxRadius });
            }
        } else if(pp.phase === 'firing') {
            pp.x += pp.vx * 2.5;
            pp.y += pp.vy * 2.5;

            enemies.forEach(e => {
                let dist = Math.hypot(e.x - pp.x, e.y - pp.y);
                if(dist < e.radius + pp.maxRadius) {
                    e.hp -= 4000;
                }
            });
        }

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

        if(bh.life <= 0) {
            blueOrbs.push({ x: bh.x, y: bh.y, radius: 90, life: 350 });
            explosions.push({x: bh.x, y: bh.y, radius: 150, maxRadius: 240, color: '#3742fa', life: 18, damage: bh.damage});
            blackHoles.splice(bhi, 1);
        }
    });

    blueOrbs.forEach((bo, boi) => {
        bo.life--;
        if(bo.life <= 0) blueOrbs.splice(boi, 1);
    });

    laserBeams.forEach((lb, lbi) => {
        lb.life--;
        if(lb.life <= 0) laserBeams.splice(lbi, 1);
    });

    enemyProjectiles.forEach((ep, epi) => {
        ep.x += ep.vx; ep.y += ep.vy;
        if(Math.hypot(player.x - ep.x, player.y - ep.y) < ep.radius + 15) {
            takeDamage(ep.damage);
            triggerVibration(8);
            enemyProjectiles.splice(epi, 1);
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
            p.traveled += Math.hypot(p.vx, p.vy);
            let reachedTarget = p.traveled >= p.maxDist;

            let hitDebrisIdx = -1;
            debrisList.forEach((deb, di) => {
                if(Math.hypot(deb.x - p.x, deb.y - p.y) < deb.radius + p.radius) {
                    hitDebrisIdx = di;
                }
            });

            if(hitDebrisIdx !== -1) {
                let deb = debrisList[hitDebrisIdx];
                debrisList.splice(hitDebrisIdx, 1);

                explosions.push({
                    x: deb.x, y: deb.y, radius: 20, maxRadius: 450, color: 'rgba(168, 85, 247, 0.95)', life: 30, damage: 15000
                });
                permanentCraters.push({ x: deb.x, y: deb.y, radius: 450 });
                triggerVibration(50);
                showDialogue('자폭 무라사키 발동!');

                player.hp = Math.max(1, player.hp * 0.5);

                projectiles.splice(pi, 1);
                return;
            }

            let hitEnemy = false;
            enemies.forEach(e => {
                if(Math.hypot(e.x - p.x, e.y - p.y) < e.radius + p.radius) {
                    hitEnemy = true;
                }
            });

            if(reachedTarget || hitEnemy) {
                explosions.push({
                    x: p.x, y: p.y, radius: 30, maxRadius: 320, color: 'rgba(255, 71, 87, 0.85)', life: 20, damage: p.damage
                });
                permanentCraters.push({ x: p.x, y: p.y, radius: 320 });
                projectiles.splice(pi, 1);
                triggerVibration(25);
            }
        } else {
            enemies.forEach(e => {
                if(Math.hypot(e.x - p.x, e.y - p.y) < e.radius + p.radius) {
                    e.hp -= p.damage;
                    projectiles.splice(pi, 1);
                }
            });
        }
    });

    slashes.forEach((s, si) => {
        s.life--;
        enemies.forEach(e => {
            if(Math.hypot(e.x - s.x, e.y - s.y) < e.radius + 30) {
                e.hp -= s.damage;
            }
        });
        if(s.life <= 0) slashes.splice(si, 1);
    });

    explosions.forEach((ex, exi) => {
        ex.radius += (ex.maxRadius - ex.radius) * 0.2;
        ex.life--;
        enemies.forEach(e => {
            if(Math.hypot(e.x - ex.x, e.y - ex.y) < ex.radius + e.radius) {
                e.hp -= (ex.damage / 10);
            }
        });
        if(ex.life <= 0) explosions.splice(exi, 1);
    });

    enemies.forEach((e, idx) => {
        if(activeDomain && activeDomain.type === 'Gojo') {
            // 정지
        } else {
            let distToPlayer = Math.hypot(player.x - e.x, player.y - e.y);
            let ang = Math.atan2(player.y - e.y, player.x - e.x);
            
            if(e.isBoss) {
                e.x += Math.cos(ang) * e.speed;
                e.y += Math.sin(ang) * e.speed;

                if(distToPlayer < 70) {
                    takeDamage(e.dmg * 0.1);
                }
            } else {
                e.x += Math.cos(ang) * e.speed;
                e.y += Math.sin(ang) * e.speed;
                if(distToPlayer < e.radius + 15) {
                    takeDamage(1.2);
                }
            }
        }

        if(e.hp <= 0) {
            for(let i=0; i<12; i++) {
                bloodSplatters.push({
                    x: e.x, y: e.y,
                    vx: (Math.random()-0.5)*8, vy: (Math.random()-0.5)*8,
                    radius: Math.random()*6+3, life: 60, color: e.isBoss ? '#ff4757' : '#a855f7'
                });
            }

            debrisList.push({
                x: e.x, y: e.y, radius: 18, life: 600 
            });

            if(e.isBoss) {
                defeatedBosses++;
                bossLevel++;
                document.getElementById('kill-status').innerText = `처치한 보스: ${defeatedBosses} / 100`;
                enemies.splice(idx, 1);

                if(bossLevel <= 100) {
                    startBossRespawnTimer();
                } else {
                    showDialogue('🎉 모든 주령을 토벌했습니다!');
                }
            } else {
                normalKillCount++;
                document.getElementById('mob-kill-status').innerText = `처치한 일반 주령: ${normalKillCount}마리`;
                addUlt(2.0);
                enemies.splice(idx, 1);
            }
        }
    });

    let hpPct = Math.max(0, (player.hp / player.maxHp) * 100);
    let ultPct = Math.max(0, (player.ultEnergy / player.maxUlt) * 100);
    document.getElementById('hp-bar').style.width = hpPct + '%';
    document.getElementById('ult-bar').style.width = ultPct + '%';
}

function draw() {
    ctx.fillStyle = '#020204';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.save();
    let shakeX = (Math.random() - 0.5) * screenShake;
    let shakeY = (Math.random() - 0.5) * screenShake;
    ctx.translate(Math.floor(-camera.x + shakeX), Math.floor(-camera.y + shakeY));

    ctx.strokeStyle = 'rgba(168, 85, 247, 0.08)';
    ctx.lineWidth = 1;
    let gridSize = 120;
    for(let x=0; x<=WORLD_WIDTH; x+=gridSize) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, WORLD_HEIGHT); ctx.stroke();
    }
    for(let y=0; y<=WORLD_HEIGHT; y+=gridSize) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(WORLD_WIDTH, y); ctx.stroke();
    }

    permanentCraters.forEach(cr => {
        ctx.save();
        ctx.fillStyle = 'rgba(5, 2, 10, 0.65)';
        ctx.beginPath(); ctx.arc(cr.x, cr.y, cr.radius * 0.85, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = 'rgba(168, 85, 247, 0.35)';
        ctx.lineWidth = 4;
        ctx.stroke();
        ctx.restore();
    });

    debrisList.forEach(deb => {
        ctx.save();
        ctx.fillStyle = '#4b4b65';
        ctx.beginPath(); ctx.arc(deb.x, deb.y, deb.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#a855f7'; ctx.lineWidth = 2; ctx.stroke();
        ctx.fillStyle = '#e056fd'; ctx.font = '9px Consolas'; ctx.textAlign = 'center';
        ctx.fillText('잔해', deb.x, deb.y - deb.radius - 4);
        ctx.restore();
    });

    bloodSplatters.forEach(bs => {
        ctx.fillStyle = bs.color;
        ctx.beginPath(); ctx.arc(bs.x, bs.y, bs.radius, 0, Math.PI*2); ctx.fill();
    });

    windTrails.forEach(wt => {
        ctx.save();
        ctx.strokeStyle = `rgba(112, 161, 255, ${wt.alpha})`;
        ctx.lineWidth = 3;
        ctx.beginPath(); ctx.arc(wt.x, wt.y, wt.radius, 0, Math.PI*2); ctx.stroke();
        ctx.restore();
    });

    blueOrbs.forEach(bo => {
        ctx.save();
        ctx.fillStyle = 'rgba(55, 66, 250, 0.18)';
        ctx.beginPath(); ctx.arc(bo.x, bo.y, bo.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#3742fa'; ctx.lineWidth = 2; ctx.stroke();
        ctx.restore();
    });

    blackHoles.forEach(bh => {
        ctx.save();
        ctx.fillStyle = 'rgba(10, 10, 30, 0.85)';
        ctx.beginPath(); ctx.arc(bh.x, bh.y, bh.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#a855f7'; ctx.lineWidth = 4; ctx.stroke();
        ctx.restore();
    });

    purpleProjectiles.forEach(pp => {
        ctx.save();
        if(pp.phase === 'expanding') {
            ctx.fillStyle = 'rgba(168, 85, 247, 0.75)';
            ctx.beginPath(); ctx.arc(pp.x, pp.y, pp.currentRadius, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#d290ff'; ctx.lineWidth = 3; ctx.stroke();
            ctx.shadowBlur = 25; ctx.shadowColor = '#a855f7';
        } else if(pp.phase === 'charging') {
            let isFlash = Math.floor(Date.now() / 40) % 2 === 0;
            ctx.fillStyle = isFlash ? 'rgba(255, 255, 255, 0.95)' : 'rgba(224, 86, 253, 0.95)';
            ctx.beginPath(); ctx.arc(pp.x, pp.y, pp.maxRadius, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#ffffff'; ctx.lineWidth = isFlash ? 8 : 4; ctx.stroke();
            ctx.shadowBlur = 60; ctx.shadowColor = '#ffffff';
        } else if(pp.phase === 'firing') {
            ctx.fillStyle = '#e056fd';
            ctx.beginPath(); ctx.arc(pp.x, pp.y, pp.maxRadius, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#fff'; ctx.lineWidth = 6; ctx.stroke();
            ctx.shadowBlur = 70; ctx.shadowColor = '#a855f7';
        }
        ctx.restore();
    });

    explosions.forEach(ex => {
        ctx.save();
        ctx.fillStyle = ex.color;
        ctx.beginPath(); ctx.arc(ex.x, ex.y, ex.radius, 0, Math.PI*2); ctx.fill();
        ctx.restore();
    });

    highQualityShots.forEach(hs => {
        ctx.fillStyle = hs.color;
        ctx.beginPath(); ctx.arc(hs.x, hs.y, hs.radius, 0, Math.PI*2); ctx.fill();
    });

    projectiles.forEach(p => {
        ctx.fillStyle = p.color;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
    });

    enemyProjectiles.forEach(ep => {
        ctx.fillStyle = ep.color;
        ctx.beginPath(); ctx.arc(ep.x, ep.y, ep.radius, 0, Math.PI*2); ctx.fill();
    });

    slashes.forEach(s => {
        ctx.save();
        ctx.strokeStyle = '#ff4757'; ctx.lineWidth = 5;
        ctx.beginPath();
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(s.x + Math.cos(s.ang)*s.length, s.y + Math.sin(s.ang)*s.length);
        ctx.stroke();
        ctx.restore();
    });

    enemies.forEach(e => {
        ctx.save();
        ctx.fillStyle = e.color;
        ctx.beginPath(); ctx.arc(e.x, e.y, e.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = e.aura; ctx.lineWidth = e.isBoss ? 5 : 2; ctx.stroke();

        let barW = e.radius * 2;
        ctx.fillStyle = 'rgba(0,0,0,0.6)';
        ctx.fillRect(e.x - barW/2, e.y - e.radius - 14, barW, 6);
        ctx.fillStyle = e.isBoss ? '#ff4757' : '#a855f7';
        ctx.fillRect(e.x - barW/2, e.y - e.radius - 14, barW * (e.hp / e.maxHp), 6);

        ctx.fillStyle = '#fff'; ctx.font = '11px Consolas'; ctx.textAlign = 'center';
        ctx.fillText(e.name || '주령', e.x, e.y - e.radius - 18);
        ctx.restore();
    });

    if(mahoraga) {
        ctx.save();
        ctx.fillStyle = '#f1c40f';
        ctx.beginPath(); ctx.arc(mahoraga.x, mahoraga.y, 35, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.stroke();
        ctx.fillStyle = '#000'; ctx.font = 'bold 12px Consolas'; ctx.textAlign = 'center';
        ctx.fillText('마허라', mahoraga.x, mahoraga.y - 40);
        ctx.restore();
    }

    // [고죠 울트라 하이퀄리티 스킨 렌더링 - 더 디테일한 무하한 오라 및 복장 연출]
    ctx.save();
    if(player.charType === 'Gojo') {
        let pulse = Math.sin(Date.now() / 120) * 6;
        
        // 외곽 무하한 결계 링 2중 효과
        ctx.strokeStyle = 'rgba(0, 210, 255, 0.6)';
        ctx.lineWidth = 2.5;
        ctx.beginPath(); ctx.arc(player.x, player.y, 34 + pulse, 0, Math.PI*2); ctx.stroke();

        ctx.strokeStyle = 'rgba(112, 161, 255, 0.35)';
        ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(player.x, player.y, 44 - pulse, 0, Math.PI*2); ctx.stroke();

        // 고죠 캐릭터 본체 (하이퀄리티 디자인)
        ctx.fillStyle = '#0652dd';
        ctx.beginPath(); ctx.arc(player.x, player.y, 23, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#00d2ff'; ctx.lineWidth = 4; ctx.stroke();

        // 눈가 안대 디자인 및 푸른 안광 디테일
        ctx.fillStyle = '#1e272e';
        ctx.beginPath(); ctx.rect(player.x - 14, player.y - 7, 28, 6); ctx.fill();
        ctx.strokeStyle = '#00d2ff'; ctx.lineWidth = 1; ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.beginPath(); ctx.arc(player.x + player.facing * 5, player.y - 4, 3.5, 0, Math.PI*2); ctx.fill();
    } else {
        ctx.fillStyle = player.charType === 'Sukuna' ? '#ff4757' : '#2ecc71';
        ctx.beginPath(); ctx.arc(player.x, player.y, 22, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.stroke();
    }

    if(limitlessActive) {
        ctx.strokeStyle = 'rgba(112, 161, 255, 0.75)';
        ctx.lineWidth = 4;
        ctx.beginPath(); ctx.arc(player.x, player.y, 48, 0, Math.PI*2); ctx.stroke();
    }

    ctx.fillStyle = '#fff'; ctx.font = 'bold 13px Consolas'; ctx.textAlign = 'center';
    ctx.fillText(player.charType === 'Gojo' ? '고죠 사토루' : (player.charType === 'Sukuna' ? '스쿠나' : '메구미'), player.x, player.y - 40);
    ctx.restore();

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
