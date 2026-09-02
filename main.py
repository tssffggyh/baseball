import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="주술회전: 무라사키 투사체 패치")

st.markdown("""
    <style>
        .main .block-container { max-width: 100% !important; padding: 0rem !important; }
        iframe { width: 100% !important; border: none; }
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

    .skill-container { display: flex; gap: 10px; margin-top: 8px; }
    .skill-icon {
        position: relative; width: 55px; height: 55px; background: rgba(255,255,255,0.08);
        border: 1px solid #a855f7; border-radius: 10px;
        display: flex; flex-direction: column; justify-content: space-between; align-items: center;
        padding: 5px; font-size: 10px; font-weight: bold; color: #fff; overflow: hidden;
    }
    .skill-key { font-size: 13px; color: #e056fd; }
    .cooldown-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.75); color: #ff4757; font-size: 15px; font-weight: bold;
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
        align-items: center;
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
                <div style="font-size:10px; color:#aaa; margin-top:4px;">체력 (HP) <span style="color:#2ecc71;">[3초 미피격 회복]</span></div>
                <div class="bar-outer"><div id="hp-bar" class="bar-hp"></div></div>
                <div style="font-size:10px; color:#aaa;">궁극기 게이지 (ULT) [X]</div>
                <div class="bar-outer"><div id="ult-bar" class="bar-ult"></div></div>
                
                <div class="skill-container">
                    <div class="skill-icon" style="border-color:#3498db;">
                        <span class="skill-key" style="color:#3498db;">AUTO</span><span>오토평타</span>
                    </div>
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
                        <span class="skill-key" style="color:#ff4757;">X</span><span>영역전개</span>
                        <div id="cd-x" class="cooldown-overlay">0</div>
                    </div>
                </div>
            </div>
            
            <div class="hud-card" style="text-align:right;">
                <div style="font-size:16px; font-weight:bold; color:#a855f7;">🛡️ 무하한 패시브 적용 (7초 주기 / 2초 지속)</div>
                <div id="boss-status" style="font-size:14px; color:#ff4757; margin-top:6px; font-weight:bold;">보스 소환 대기 중...</div>
                <div id="kill-status" style="font-size:13px; color:#aaa; margin-top:2px;">처치한 보스: 0 / 100</div>
            </div>
        </div>
    </div>

    <div id="dialogue-box">
        <div id="dialogue-text">무량공처</div>
    </div>

    <div id="class-select">
        <h1 style="color:#f3e8ff; font-size:48px; letter-spacing:2px; text-shadow:0 0 20px #a855f7;">JUJUTSU KAISEN</h1>
        <p style="color:#a1a1aa; margin-top:10px;">플레이할 주술사를 선택하십시오.</p>
        <div class="card-group">
            <div class="card" onclick="selectChar('Gojo')">
                <h2 style="color:#70a1ff;">👁️ 고죠 사토루</h2>
                <p>
                    • 패시브: <strong>무하한 (7초마다 2초간 밀어내기)</strong><br>
                    • E: 아카 「赤」<br>
                    • R: 아오 「蒼」<br>
                    • T: 허식 「茈」 (원형 투사체 발사)<br>
                    • X: 영역전개
                </p>
            </div>
            <div class="card" onclick="selectChar('Sukuna')">
                <h2 style="color:#ff4757;">👹 양면 스쿠나</h2>
                <p>
                    • 기본공격: 자동 참격<br>
                    • E: 해(解) / R: 팔(捌)<br>
                    • T: 푸가(🔥) / X: 복마어주자
                </p>
            </div>
            <div class="card" onclick="selectChar('Megumi')">
                <h2 style="color:#2ecc71;">🐺 후시구로 메구미</h2>
                <p>
                    • 기본공격: 자동 투사체<br>
                    • E: 누에 / R: 옥견<br>
                    • T: 그림자 속박 / X: 마허라
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

const yowaimoAudio = new Audio('https://www.myinstants.com/media/sounds/yowai-mo-gojo-77212.mp3');
yowaimoAudio.volume = 0.8;

const aoAudio = new Audio('https://www.myinstants.com/media/sounds/jujutsu-kaisen-gojo-blue-ao.mp3');
aoAudio.volume = 1.0;

const purpleAudio = new Audio('https://www.myinstants.com/media/sounds/hollow-purple.mp3');
purpleAudio.volume = 1.0;

let audioCtx = null;
function initAudio() {
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    [yowaimoAudio, aoAudio, purpleAudio].forEach(audio => {
        if(audio.paused) {
            audio.play().catch(() => {});
            audio.pause();
            audio.currentTime = 0;
        }
    });
}

function playVoiceAndSound(type) {
    initAudio();
    if(type === 'yowaimo') { yowaimoAudio.currentTime = 0; yowaimoAudio.play().catch(err => {}); return; }
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

let player = {
    x: WORLD_WIDTH / 2, y: WORLD_HEIGHT / 2,
    speed: 6.5, hp: 300, maxHp: 300,
    ultEnergy: 0, maxUlt: 100,
    charType: 'Gojo', facing: 1, lastAttack: 0
};

let cooldowns = { E: 0, R: 0, T: 0, X: 0 };
let maxCooldowns = {
    Gojo: { E: 5, R: 10, T: 16, X: 0 },
    Sukuna: { E: 4, R: 9, T: 14, X: 0 },
    Megumi: { E: 5, R: 10, T: 15, X: 0 }
};

let dialogues = {
    Gojo: { E: '술식 순전 · 「赤」', R: '술식 반전 · 「蒼」', T: '허식 「茈」', X: '료이키텐카이 무량공처' },
    Sukuna: { E: '참격 「해(解)」', R: '참격 「팔(捌)」', T: '「푸가(🔥)」', X: '영역전개 「복마어주자」' },
    Megumi: { E: '십종영법술 「누에」', R: '십종영법술 「옥견」', T: '그림자 속박', X: '마허라 소환' }
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
let purpleProjectiles = []; // 무라사키 전용 투사체 배열 추가
let laserBeams = [];
let meleeAttacks = [];
let enemies = [];

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

function getAutoAimTarget() {
    if(enemies.length === 0) return { x: player.x + player.facing * 100, y: player.y, angle: player.facing > 0 ? 0 : Math.PI, dist: 9999 };
    let closest = enemies[0];
    let minDist = Math.hypot(closest.x - player.x, closest.y - player.y);
    for(let i = 1; i < enemies.length; i++) {
        let dist = Math.hypot(enemies[i].x - player.x, enemies[i].y - player.y);
        if(dist < minDist) { minDist = dist; closest = enemies[i]; }
    }
    let angle = Math.atan2(closest.y - player.y, closest.x - player.x);
    return { x: closest.x, y: closest.y, angle: angle, dist: minDist };
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

function addUlt(amount) { player.ultEnergy = Math.min(player.maxUlt, player.ultEnergy + amount); }
function takeDamage(damage) { player.hp -= damage; lastHitTime = Date.now(); }

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
        'Gojo': ['아카', '아오', '무라사키', '무량공처'],
        'Sukuna': ['해(解)', '팔(捌)', '푸가', '복마어주자'],
        'Megumi': ['누에', '옥견', '그림자', '마허라']
    };
    
    document.getElementById('char-name').innerText = type === 'Gojo' ? '고죠 사토루' : (type === 'Sukuna' ? '양면 스쿠나' : '후시구로 메구미');
    document.getElementById('sk-e').innerText = skNames[type][0];
    document.getElementById('sk-r').innerText = skNames[type][1];
    document.getElementById('sk-t').innerText = skNames[type][2];

    for(let i=0; i<30; i++) spawnCurse();
    spawnBoss();
    gameLoop();
}

function basicAttack() {
    if(isGameOver) return;
    let now = Date.now();
    if(now - player.lastAttack < 550) return;
    player.lastAttack = now;

    addUlt(3.5);
    let target = getAutoAimTarget();
    let ang = target.angle;
    player.facing = Math.cos(ang) >= 0 ? 1 : -1;

    if(player.charType === 'Gojo' && Math.random() < 0.35) {
        playVoiceAndSound('yowaimo');
        showDialogue('「약하니까요」');
    }

    if(player.charType === 'Gojo') {
        projectiles.push({
            x: player.x, y: player.y, vx: Math.cos(ang)*18, vy: Math.sin(ang)*18,
            damage: 65, radius: 11, color: '#70a1ff', type:'gojo_basic'
        });
    } else if(player.charType === 'Sukuna') {
        slashes.push({x: player.x + Math.cos(ang)*30, y: player.y + Math.sin(ang)*30, ang: ang, length: 80, life: 6, damage: 60});
    } else {
        projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang)*14, vy: Math.sin(ang)*14, damage: 45, radius: 8, color: '#2ecc71', type:'normal'});
    }
}

function castSkill(key) {
    if(isGameOver) return;
    if(cooldowns[key] > 0) return;
    if(key === 'X' && player.ultEnergy < player.maxUlt) return;

    let target = getAutoAimTarget();
    let targetX = target.x;
    let targetY = target.y;
    let ang = target.angle;
    player.facing = Math.cos(ang) >= 0 ? 1 : -1;

    if(key === 'X' && player.charType === 'Gojo') {
        gojoDomainCount++;
        if(gojoDomainCount >= 3) {
            showDialogue('더 이상 쓸 수가 없어...');
            cooldowns.X = 20;
            player.ultEnergy = 0;
            gojoDomainCount = 0;
            triggerVibration(40);
            return;
        }
    }

    showDialogue(dialogues[player.charType][key]);

    if(key === 'E') {
        cooldowns.E = maxCooldowns[player.charType].E;
        addUlt(8.0);
        
        if(player.charType === 'Gojo') {
            playVoiceAndSound('aka');
            triggerVibration(20);
            projectiles.push({
                x: player.x, y: player.y, targetX: targetX, targetY: targetY,
                vx: Math.cos(ang)*22, vy: Math.sin(ang)*22,
                type: 'aka', damage: 500, radius: 18
            });
        } else if(player.charType === 'Sukuna') {
            for(let i=-2; i<=2; i++) {
                slashes.push({ x: player.x, y: player.y, ang: ang + i*0.2, length: 220, life: 14, damage: 95 });
            }
        } else {
            explosions.push({x: targetX, y: targetY, radius: 70, maxRadius: 70, color: '#f1c40f', life: 15, damage: 120});
        }
    } else if(key === 'R') {
        cooldowns.R = maxCooldowns[player.charType].R;
        addUlt(12.0);
        
        if(player.charType === 'Gojo') {
            playVoiceAndSound('ao_voice');
            triggerVibration(20);
            blackHoles.push({
                orbitAngle: ang, orbitRadius: 240, radius: 400, life: 180, damage: 220, x: player.x, y: player.y
            });
        } else if(player.charType === 'Sukuna') {
            for(let i=0; i<12; i++) {
                slashes.push({
                    x: targetX + (Math.random()-0.5)*200, y: targetY + (Math.random()-0.5)*200,
                    ang: Math.random()*Math.PI*2, length: 160, life: 12, damage: 130
                });
            }
        } else {
            projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang)*15, vy: Math.sin(ang)*15, type:'normal', damage: 100, radius: 10, color: '#2ecc71'});
        }
    } else if(key === 'T') {
        cooldowns.T = maxCooldowns[player.charType].T;
        if(player.charType === 'Gojo') {
            addUlt(20.0);
            playVoiceAndSound('purple_voice');
            triggerVibration(45);
            // 허식 무라사키를 원형 투사체로 발사 (날아가는 투사체 등록)
            purpleProjectiles.push({
                x: player.x, y: player.y,
                vx: Math.cos(ang) * 14, vy: Math.sin(ang) * 14,
                radius: 45, maxLife: 150, life: 150, damage: 2500
            });
        } else if(player.charType === 'Sukuna') {
            addUlt(15.0);
            explosions.push({x: targetX, y: targetY, radius: 180, maxRadius: 180, color: '#e67e22', life: 30, damage: 300});
        } else {
            addUlt(15.0);
            enemies.forEach(e => { if(Math.hypot(e.x - player.x, e.y - player.y) < 350) e.speed = 0.5; });
        }
    } else if(key === 'X') {
        player.ultEnergy = 0;
        if(player.charType === 'Gojo') {
            activeDomain = { type: 'Gojo', timer: 280 };
        } else if(player.charType === 'Sukuna') {
            activeDomain = { type: 'Sukuna', timer: 220 };
        } else {
            mahoraga = { x: player.x, y: player.y - 50, life: 600 };
        }
        triggerVibration(40);
    }
}

function triggerPurpleExplosion(x, y, boIndex) {
    playVoiceAndSound('purple_voice');
    showDialogue('허식 「무라사키」 대폭발!');
    triggerVibration(80);

    if(boIndex !== undefined && boIndex !== null && boIndex >= 0 && boIndex < blueOrbs.length) {
        blueOrbs.splice(boIndex, 1);
    }

    for (let i = 0; i < 150; i++) {
        let pAng = Math.random() * Math.PI * 2;
        let pDist = Math.random() * 500 + 50;
        let pSpeed = Math.random() * 15 + 8;
        purpleEffects.push({
            x: x + Math.cos(pAng) * pDist, y: y + Math.sin(pAng) * pDist,
            targetX: x, targetY: y,
            vx: -Math.cos(pAng) * pSpeed, vy: -Math.sin(pAng) * pSpeed,
            radius: Math.random() * 10 + 5, life: 50, color: i % 2 === 0 ? '#a855f7' : '#e056fd'
        });
    }

    explosions.push({
        x: x, y: y, radius: 600, maxRadius: 600,
        color: 'rgba(168, 85, 247, 0.95)', life: 40, damage: 4500
    });
    enemies.forEach(e => { if(Math.hypot(e.x - x, e.y - y) < 600) e.hp -= 4500; });
}

function spawnCurse() {
    let x = Math.random() * WORLD_WIDTH;
    let y = Math.random() * WORLD_HEIGHT;
    if(Math.hypot(x - player.x, y - player.y) < 500) return;

    let isRanged = Math.random() < 0.4;
    enemies.push({
        x: x, y: y, radius: isRanged ? 18 : 22,
        hp: isRanged ? 120 : 180, maxHp: isRanged ? 120 : 180,
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
    document.getElementById('final-stats').innerText = `도달한 보스 레벨: Lv.${bossLevel} | 처치한 보스: ${defeatedBosses}마리`;
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
            player.hp = Math.min(player.maxHp, player.hp + (player.maxHp * 0.005)); 
        }
    }
}, 100);

function update() {
    if(isGameOver) return;
    if(screenShake > 0) screenShake--;
    if(player.hp <= 0) { triggerGameOver(); return; }

    if(player.charType === 'Gojo') {
        limitlessTimer += 0.016; 
        if(!limitlessActive && limitlessTimer >= 7.0) {
            limitlessActive = true;
            limitlessDurationCounter = 120; 
            showDialogue('「무하한」 발동!');
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

    let target = getAutoAimTarget();
    if(target.dist < 850) {
        basicAttack();
    }

    if(enemies.filter(e => !e.isBoss).length < 35) spawnCurse();

    if(activeDomain) {
        activeDomain.timer--;
        triggerVibration(4);
        if(activeDomain.type === 'Gojo') {
            enemies.forEach(e => { e.speed = 0; e.hp -= 2.5; });
        } else if(activeDomain.type === 'Sukuna') {
            if(activeDomain.timer % 3 === 0) {
                slashes.push({
                    x: player.x + (Math.random()-0.5)*600, y: player.y + (Math.random()-0.5)*600,
                    ang: Math.random()*Math.PI*2, length: 220, life: 6, damage: 50
                });
            }
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
            if(Math.hypot(bossTarget.x - mahoraga.x, bossTarget.y - mahoraga.y) < 60) bossTarget.hp -= 25;
        }
        if(mahoraga.life <= 0) mahoraga = null;
    }

    // 허식 무라사키 투사체 업데이트 및 충돌 처리
    purpleProjectiles.forEach((pp, ppi) => {
        pp.x += pp.vx;
        pp.y += pp.vy;
        pp.life--;

        // 적들과 충돌 검사
        enemies.forEach(e => {
            if(Math.hypot(e.x - pp.x, e.y - pp.y) < e.radius + pp.radius) {
                e.hp -= pp.damage;
            }
        });

        // 수명이 다하거나 맵 끝에 도달하면 대폭발 일으키고 소멸
        if(pp.life <= 0 || pp.x < 0 || pp.x > WORLD_WIDTH || pp.y < 0 || pp.y > WORLD_HEIGHT) {
            triggerPurpleExplosion(pp.x, pp.y);
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
                e.x += Math.cos(pullAng) * 13;
                e.y += Math.sin(pullAng) * 13;
                e.hp -= 4.0;
            }
        });

        enemyProjectiles.forEach((ep, epi) => {
            let d = Math.hypot(bh.x - ep.x, bh.y - ep.y);
            if(d < bh.radius) {
                let pullAng = Math.atan2(bh.y - ep.y, bh.x - ep.x);
                ep.vx = Math.cos(pullAng) * 14;
                ep.vy = Math.sin(pullAng) * 14;
                if(d < 40) enemyProjectiles.splice(epi, 1);
            }
        });

        if(bh.life <= 0) {
            blueOrbs.push({ x: bh.x, y: bh.y, radius: 95, life: 350 });
            explosions.push({x: bh.x, y: bh.y, radius: 260, maxRadius: 260, color: '#3742fa', life: 18, damage: bh.damage});
            blackHoles.splice(bhi, 1);
        }
    });

    blueOrbs.forEach((bo, boi) => {
        bo.life--;
        enemyProjectiles.forEach((ep, epi) => {
            let d = Math.hypot(bo.x - ep.x, bo.y - ep.y);
            if(d < bo.radius) {
                let pullAng = Math.atan2(bo.y - ep.y, bo.x - ep.x);
                ep.x += Math.cos(pullAng) * 8;
                ep.y += Math.sin(pullAng) * 8;
                if(d < 30) enemyProjectiles.splice(epi, 1);
            }
        });
        if(bo.life <= 0) blueOrbs.splice(boi, 1);
    });

    laserBeams.forEach((lb, lbi) => {
        lb.life--;
        enemies.forEach(e => {
            let endX = lb.x + Math.cos(lb.ang) * lb.length;
            let endY = lb.y + Math.sin(lb.ang) * lb.length;
            let d = Math.abs((endY - lb.y)*e.x - (endX - lb.x)*e.y + endX*lb.y - endY*lb.x) / Math.hypot(endY - lb.y, endX - lb.x);
            if(d < lb.width / 2 + e.radius) e.hp -= lb.damage / 10;
        });
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

    projectiles.forEach((p, pi) => {
        p.x += p.vx; p.y += p.vy;

        if(p.type === 'aka') {
            for(let boi = 0; boi < blueOrbs.length; boi++) {
                let bo = blueOrbs[boi];
                if(Math.hypot(p.x - bo.x, p.y - bo.y) < bo.radius + 20) {
                    triggerPurpleExplosion(bo.x, bo.y, boi);
                    projectiles.splice(pi, 1);
                    return;
                }
            }

            if(Math.hypot(p.targetX - p.x, p.targetY - p.y) < 25) {
                triggerVibration(24);
                explosions.push({x: p.x, y: p.y, radius: 160, maxRadius: 160, color: '#ff4757', life: 20, damage: p.damage});
                projectiles.splice(pi, 1);
                return;
            }
        }

        enemies.forEach((e) => {
            if(Math.hypot(e.x - p.x, e.y - p.y) < e.radius + p.radius) {
                e.hp -= p.damage;
                if(p.type === 'normal' || p.type === 'gojo_basic') projectiles.splice(pi, 1);
            }
        });
    });

    purpleEffects.forEach((pe, pei) => {
        pe.x += pe.vx; pe.y += pe.vy; pe.life--;
        if(pe.life <= 0) purpleEffects.splice(pei, 1);
    });

    explosions.forEach((ex, exi) => {
        ex.life--;
        enemies.forEach(e => { if(Math.hypot(e.x - ex.x, e.y - ex.y) < ex.radius) e.hp -= ex.damage / 10; });
        if(ex.life <= 0) explosions.splice(exi, 1);
    });

    slashes.forEach((s, si) => {
        s.life--;
        enemies.forEach(e => { if(Math.hypot(e.x - s.x, e.y - s.y) < s.length / 2) e.hp -= s.damage / 4; });
        if(s.life <= 0) slashes.splice(si, 1);
    });

    enemies.forEach((e, ei) => {
        if(activeDomain && activeDomain.type === 'Gojo') e.speed = 0;
        else e.speed = e.isBoss ? e.speed : (e.isRanged ? 2.0 : 2.8);

        let ang = Math.atan2(player.y - e.y, player.x - e.x);
        let dist = Math.hypot(player.x - e.x, player.y - e.y);

        if(player.charType === 'Gojo' && limitlessActive && dist < 180) {
            e.x -= Math.cos(ang) * 12; 
            e.y -= Math.sin(ang) * 12;
        } else {
            if(e.isRanged && dist < 300) {
                e.x -= Math.cos(ang) * e.speed;
                e.y -= Math.sin(ang) * e.speed;
            } else {
                e.x += Math.cos(ang) * e.speed;
                e.y += Math.sin(ang) * e.speed;
            }
        }

        e.attackCd = (e.attackCd || 0) + 1;
        e.skillCd = (e.skillCd || 0) + 1;
        e.ultCd = (e.ultCd || 0) + 1;

        if(e.isRanged && e.attackCd >= 80 && dist < 550 && e.speed > 0) {
            e.attackCd = 0;
            enemyProjectiles.push({
                x: e.x, y: e.y, vx: Math.cos(ang)*8, vy: Math.sin(ang)*8,
                damage: 18, radius: 6
            });
        }

        if(e.isBoss && e.speed > 0) {
            if(e.skillCd >= 70) {
                e.skillCd = 0;
                let patternType = Math.floor(Math.random() * 3);
                
                if(patternType === 0) {
                    for(let i=-2; i<=2; i++) {
                        enemyProjectiles.push({
                            x: e.x, y: e.y, vx: Math.cos(ang + i*0.22)*11, vy: Math.sin(ang + i*0.22)*11,
                            damage: e.dmg * 0.7, radius: 8
                        });
                    }
                } else if(patternType === 1) {
                    explosions.push({
                        x: player.x + (Math.random()-0.5)*120, y: player.y + (Math.random()-0.5)*120,
                        radius: 150, maxRadius: 150, color: 'rgba(231, 76, 60, 0.65)', life: 25, damage: e.dmg * 1.1
                    });
                } else {
                    for(let i=0; i<8; i++) {
                        let rAng = (Math.PI * 2 / 8) * i;
                        enemyProjectiles.push({
                            x: e.x, y: e.y, vx: Math.cos(rAng)*7.5, vy: Math.sin(rAng)*7.5,
                            damage: e.dmg * 0.8, radius: 7
                        });
                    }
                }
            }

            if(e.ultCd >= 220) {
                e.ultCd = 0;
                showDialogue(`⚠️ [보스 궁극기] 파멸의 참격 파동 발동!`);
                triggerVibration(18);
                for(let i=0; i<12; i++) {
                    let rAng = (Math.PI * 2 / 12) * i;
                    slashes.push({
                        x: e.x, y: e.y, ang: rAng, length: 240, life: 20, damage: e.dmg * 1.4
                    });
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

        if(e.hp <= 0) {
            if(e.isBoss) {
                defeatedBosses++;
                bossLevel++;
                addUlt(25.0);
                enemies.splice(ei, 1);
                
                if(bossLevel <= 100) {
                    startBossRespawnTimer();
                } else {
                    document.getElementById('boss-status').innerText = `🏆 모든 보스 제령 완료!`;
                    showDialogue(`🎉 축하합니다! 100단계 보스 정복!`);
                }
            } else {
                addUlt(3.0);
                enemies.splice(ei, 1);
            }
        }
    });

    document.getElementById('hp-bar').style.width = Math.max(0, (player.hp / player.maxHp * 100)) + '%';
    document.getElementById('ult-bar').style.width = Math.min(100, (player.ultEnergy / player.maxUlt * 100)) + '%';
    document.getElementById('kill-status').innerText = `처치한 보스: ${defeatedBosses} / 100`;
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
        ctx.fillStyle = '#111'; ctx.fillRect(-10, -16, 20, 32);
        ctx.fillStyle = '#ff7675'; ctx.fillRect(-9, -32, 18, 10);
        ctx.fillStyle = '#ff4757'; ctx.fillRect(-6, -24, 12, 3);
    } else {
        ctx.fillStyle = '#0f172a'; ctx.fillRect(-10, -16, 20, 32);
        ctx.fillStyle = '#1e293b'; ctx.fillRect(-11, -34, 22, 12);
    }
    ctx.restore();
}

function drawEnemySprite(e) {
    ctx.save();
    ctx.translate(e.x, e.y);

    if(e.isBoss) {
        ctx.shadowBlur = 25 + Math.floor(e.level / 4); ctx.shadowColor = e.aura;
        ctx.fillStyle = e.color;
        ctx.beginPath(); ctx.arc(0, 0, e.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 4; ctx.stroke();
        
        ctx.fillStyle = e.aura;
        for(let i=0; i<e.spikes; i++) {
            let spikeAng = (Math.PI * 2 / e.spikes) * i;
            let sx = Math.cos(spikeAng) * (e.radius + 12);
            let sy = Math.sin(spikeAng) * (e.radius + 12);
            ctx.beginPath(); ctx.arc(sx, sy, 7, 0, Math.PI*2); ctx.fill();
        }

        ctx.shadowBlur = 0;
        ctx.fillStyle = '#ff4757';
        ctx.font = 'bold 16px Consolas';
        ctx.textAlign = 'center';
        ctx.fillText(`[LV.${e.level}]`, 0, -e.radius - 18);
    } else {
        if(e.isRanged) {
            ctx.fillStyle = '#8e44ad';
            ctx.beginPath();
            ctx.moveTo(0, -e.radius);
            ctx.lineTo(e.radius, 0);
            ctx.lineTo(0, e.radius);
            ctx.lineTo(-e.radius, 0);
            ctx.closePath();
            ctx.fill();
            ctx.strokeStyle = '#e056fd'; ctx.lineWidth = 2; ctx.stroke();
        } else {
            ctx.fillStyle = '#1e272e';
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
    ctx.translate(-camera.x, -camera.y);

    if(player.charType === 'Gojo' && limitlessActive) {
        ctx.save();
        ctx.strokeStyle = 'rgba(112, 161, 255, 0.75)';
        ctx.lineWidth = 4;
        ctx.shadowBlur = 25;
        ctx.shadowColor = '#70a1ff';
        ctx.beginPath();
        ctx.arc(player.x, player.y, 180, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillStyle = 'rgba(112, 161, 255, 0.08)';
        ctx.fill();
        ctx.restore();
    }

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
            ctx.fillStyle = 'rgba(40, 5, 5, 0.75)';
            ctx.fillRect(camera.x, camera.y, canvas.width, canvas.height);
        }
    }

    ctx.strokeStyle = 'rgba(168, 85, 247, 0.06)'; ctx.lineWidth = 1;
    for(let x=0; x<WORLD_WIDTH; x+=100) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,WORLD_HEIGHT); ctx.stroke(); }
    for(let y=0; y<WORLD_HEIGHT; y+=100) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(WORLD_WIDTH,y); ctx.stroke(); }

    blackHoles.forEach(bh => {
        ctx.shadowBlur = 45; ctx.shadowColor = '#3742fa';
        ctx.fillStyle = 'rgba(10, 10, 50, 0.9)';
        ctx.beginPath(); ctx.arc(bh.x, bh.y, 85, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#70a1ff'; ctx.lineWidth = 6; ctx.stroke();
        ctx.shadowBlur = 0;
    });

    blueOrbs.forEach(bo => {
        let alpha = bo.life / 350;
        ctx.shadowBlur = 50; ctx.shadowColor = '#0026ff';
        ctx.fillStyle = `rgba(0, 38, 255, ${alpha})`;
        ctx.beginPath(); ctx.arc(bo.x, bo.y, bo.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = `rgba(100, 200, 255, ${alpha})`; ctx.lineWidth = 8; ctx.stroke();
        ctx.shadowBlur = 0;
    });

    // 허식 무라사키 원형 투사체 렌더링
    purpleProjectiles.forEach(pp => {
        ctx.save();
        ctx.shadowBlur = 40;
        ctx.shadowColor = '#a855f7';
        ctx.fillStyle = '#7000ff';
        ctx.beginPath();
        ctx.arc(pp.x, pp.y, pp.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#e056fd';
        ctx.lineWidth = 6;
        ctx.stroke();
        ctx.restore();
    });

    laserBeams.forEach(lb => {
        ctx.save();
        ctx.shadowBlur = 30; ctx.shadowColor = '#a855f7';
        ctx.strokeStyle = 'rgba(224, 86, 253, 0.9)';
        ctx.lineWidth = lb.width;
        ctx.beginPath();
        ctx.moveTo(lb.x, lb.y);
        ctx.lineTo(lb.x + Math.cos(lb.ang)*lb.length, lb.y + Math.sin(lb.ang)*lb.length);
        ctx.stroke();
        
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = lb.width * 0.4;
        ctx.beginPath();
        ctx.moveTo(lb.x, lb.y);
        ctx.lineTo(lb.x + Math.cos(lb.ang)*lb.length, lb.y + Math.sin(lb.ang)*lb.length);
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

    slashes.forEach(s => {
        ctx.strokeStyle = '#ff4757'; ctx.lineWidth = 5;
        ctx.beginPath();
        ctx.moveTo(s.x - Math.cos(s.ang)*s.length/2, s.y - Math.sin(s.ang)*s.length/2);
        ctx.lineTo(s.x + Math.cos(s.ang)*s.length/2, s.y + Math.sin(s.ang)*s.length/2);
        ctx.stroke();
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
        ctx.shadowBlur = p.type === 'gojo_basic' ? 15 : 0;
        ctx.shadowColor = '#70a1ff';
        ctx.fillStyle = p.color || (p.type === 'aka' ? '#ff4757' : '#3742fa');
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
        ctx.shadowBlur = 0;
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

components.html(game_html, height=950)
