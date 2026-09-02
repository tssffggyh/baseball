import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="주술회전: 허식 무라사키 완벽 고증판")

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
<meta charset="utf-8">
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body, html {
        width: 100%; height: 100%; overflow: hidden;
        background-color: #020204; color: #fff;
        font-family: 'Consolas', monospace;
    }
    #game-container {
        position: relative; width: 100vw; height: 100vh;
        overflow: hidden; background: #020204;
    }
    canvas { display: block; cursor: crosshair; width: 100%; height: 100%; }
    
    #ui-layer {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; padding: 20px 30px;
        display: flex; flex-direction: column; justify-content: space-between; z-index: 10;
    }
    .hud-card {
        background: rgba(10, 10, 18, 0.85); backdrop-filter: blur(10px);
        padding: 15px 25px; border-radius: 12px;
        border: 1px solid rgba(0, 210, 255, 0.4); box-shadow: 0 8px 32px rgba(0,0,0,0.6);
        pointer-events: auto;
    }
    .bar-outer {
        width: 280px; height: 12px; background: rgba(255,255,255,0.1);
        border-radius: 6px; overflow: hidden; margin: 4px 0 10px 0;
    }
    .bar-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff4757, #ff6b81); transition: width 0.1s; }
    .bar-ult { width: 0%; height: 100%; background: linear-gradient(90deg, #00d2ff, #70a1ff); transition: width 0.1s; }
    
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
        border: 1px solid #00d2ff; border-radius: 10px;
        display: flex; flex-direction: column; justify-content: space-between; align-items: center;
        padding: 4px; font-size: 9px; font-weight: bold; color: #fff; overflow: hidden;
    }
    .skill-key { font-size: 12px; color: #70a1ff; }
    .cooldown-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.75); color: #ff4757; font-size: 14px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; display: none;
    }

    #dialogue-box {
        position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%);
        background: rgba(5, 5, 12, 0.95); border: 2px solid #00d2ff;
        border-radius: 12px; padding: 12px 30px; text-align: center;
        box-shadow: 0 0 30px rgba(0, 210, 255, 0.6);
        opacity: 0; transition: opacity 0.15s ease-in-out; pointer-events: none; z-index: 20;
    }
    #dialogue-text { font-size: 24px; font-weight: bold; color: #e0f2fe; letter-spacing: 3px; }

    #class-select {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(3, 3, 6, 0.98); backdrop-filter: blur(15px);
        display: flex; flex-direction: column; justify-content: center; z-index: 9999;
        align-items: center; pointer-events: auto;
    }
    .card-group { display: flex; gap: 30px; margin-top: 40px; }
    .card {
        background: rgba(20, 20, 35, 0.7); border: 2px solid rgba(0, 210, 255, 0.3);
        border-radius: 20px; padding: 30px 20px; width: 320px;
        text-align: center; cursor: pointer; transition: all 0.3s ease;
    }
    .card:hover {
        transform: translateY(-10px); border-color: #00d2ff;
        box-shadow: 0 15px 35px rgba(0, 210, 255, 0.4); background: rgba(30, 30, 50, 0.9);
    }
    .card h2 { margin-bottom: 12px; font-size: 26px; }
    .card p { font-size: 12px; color: #a1a1aa; line-height: 1.6; text-align: left; }
    
    #game-over {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(3, 3, 6, 0.98); backdrop-filter: blur(15px);
        display: none; flex-direction: column; justify-content: center; z-index: 100;
        align-items: center; pointer-events: auto;
    }
    .restart-btn {
        margin-top: 30px; padding: 15px 40px; font-size: 20px; font-weight: bold;
        color: #fff; background: linear-gradient(90deg, #ff4757, #00d2ff);
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
                <div id="char-name" style="color:#00d2ff; font-weight:bold; font-size:16px;">원작 고죠 사토루</div>
                <div style="font-size:10px; color:#aaa; margin-top:4px;">체력 (HP)</div>
                <div class="bar-outer"><div id="hp-bar" class="bar-hp"></div></div>
                <div style="font-size:10px; color:#aaa;">궁극기 게이지 (ULT) [X]</div>
                <div class="bar-outer"><div id="ult-bar" class="bar-ult"></div></div>
                
                <div class="skill-container">
                    <div class="skill-icon" style="border-color:#3498db;">
                        <span class="skill-key" style="color:#3498db;">AUTO</span><span>오토에임</span>
                    </div>
                    <div class="skill-icon">
                        <span class="skill-key">Q</span><span id="sk-q">신속이동</span>
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
                        <span class="skill-key" style="color:#ff4757;">X</span><span>무량공처</span>
                        <div id="cd-x" class="cooldown-overlay">0</div>
                    </div>
                </div>
            </div>
            
            <div class="hud-card" style="text-align:right;">
                <div id="boss-status" style="font-size:14px; color:#ff4757; font-weight:bold;">보스 소환 대기 중...</div>
                <div id="kill-status" style="font-size:13px; color:#aaa; margin-top:6px;">처치한 보스: 0 / 100</div>
                <div id="mob-kill-status" style="font-size:13px; color:#00d2ff; margin-top:2px; font-weight:bold;">처치한 일반 주령: 0마리</div>
            </div>
        </div>
    </div>

    <div id="dialogue-box">
        <div id="dialogue-text">무량공처</div>
    </div>

    <div id="class-select">
        <h1 style="color:#e0f2fe; font-size:48px; letter-spacing:2px; text-shadow:0 0 20px #00d2ff;">JUJUTSU KAISEN</h1>
        <p style="color:#a1a1aa; margin-top:10px;">[원작 고증 고죠 사토루 | 궤도형 아오 견인 | 잔해 아카 자폭 무라사키 | 지연형 茈]</p>
        <div class="card-group">
            <div class="card" id="card-gojo">
                <h2 style="color:#00d2ff;">👁️ 고죠 사토루 (원작 고증)</h2>
                <p>
                    • 외형: 흑발 머리칼 + 검은색 안대 (원작 의상)<br>
                    • Q: 신속 순간이동 (순보)<br>
                    • E: 술식반전 「赤」 (아오가 있으면 자동 유도)<br>
                    • R: 술식순전 「蒼」 (내 주위 거리두고 궤도 회전 + 몹/발사체 끌고 감)<br>
                    • T: 허식 「茈」 (엄청 늦게 나가며 강력한 파괴력)<br>
                    • X: 영역전개 · 무량공처
                </p>
            </div>
            <div class="card" id="card-sukuna">
                <h2 style="color:#ff4757;">👹 양면 스쿠나</h2>
                <p>
                    • Q: 신속 폭주<br>
                    • E: 참격 「해(解)」<br>
                    • R: 참격 「팔(捌)」<br>
                    • T: 「푸가(🔥)」<br>
                    • X: 복마어주자
                </p>
            </div>
        </div>
    </div>

    <div id="game-over">
        <h1 style="color:#ff4757; font-size:56px; letter-spacing:3px;">YOU DIED</h1>
        <p style="color:#aaa; margin-top:10px; font-size:18px;" id="final-stats">주령들의 공격으로 사망했습니다.</p>
        <button class="restart-btn" id="restart-btn">다시 도전하기</button>
    </div>
</div>

<script>
// 웹 오디오 API 합성 사운드 시스템 (브라우저 자동 재생 정책 우회 및 호환성 확보)
let audioCtx = null;

function initAudio() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
}

function playSound(type) {
    if (!audioCtx) return;
    try {
        let osc = audioCtx.createOscillator();
        let gain = audioCtx.createGain();
        osc.connect(gain);
        gain.connect(audioCtx.destination);

        let now = audioCtx.currentTime;

        if (type === 'shoot') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(600, now);
            osc.frequency.exponentialRampToValueAtTime(150, now + 0.1);
            gain.gain.setValueAtTime(0.15, now);
            gain.gain.linearRampToValueAtTime(0.01, now + 0.1);
            osc.start(now);
            osc.stop(now + 0.1);
        } else if (type === 'skill') {
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(300, now);
            osc.frequency.exponentialRampToValueAtTime(900, now + 0.25);
            gain.gain.setValueAtTime(0.2, now);
            gain.gain.linearRampToValueAtTime(0.01, now + 0.25);
            osc.start(now);
            osc.stop(now + 0.25);
        } else if (type === 'explosion') {
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(120, now);
            osc.frequency.linearRampToValueAtTime(30, now + 0.4);
            gain.gain.setValueAtTime(0.3, now);
            gain.gain.linearRampToValueAtTime(0.01, now + 0.4);
            osc.start(now);
            osc.stop(now + 0.4);
        } else if (type === 'hit') {
            osc.type = 'square';
            osc.frequency.setValueAtTime(150, now);
            osc.frequency.linearRampToValueAtTime(50, now + 0.08);
            gain.gain.setValueAtTime(0.1, now);
            gain.gain.linearRampToValueAtTime(0.01, now + 0.08);
            osc.start(now);
            osc.stop(now + 0.08);
        }
    } catch(e) {}
}

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

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
    Gojo: { Q: 12, E: 5, R: 14, T: 22, X: 0 },
    Sukuna: { Q: 29, E: 7, R: 14, T: 21, X: 0 }
};

let dialogues = {
    Gojo: { Q: '신속 이동', E: '술식반전 · 「赤」', R: '술식순전 · 「蒼」', T: '허식 「茈」', X: '료이키텐카이 무량공처' },
    Sukuna: { Q: '신속 폭주', E: '참격 「해(解)」', R: '참격 「팔(捌)」', T: '「푸가(🔥)」', X: '영역전개 「복마어주자」' }
};

let activeDomain = null;
let keys = {};
let projectiles = [];
let enemyProjectiles = [];
let slashes = [];
let explosions = [];
let blackHoles = [];      
let blueOrbs = [];        
let purpleProjectiles = []; 
let enemies = [];
let highQualityShots = []; 

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
window.addEventListener('click', () => { initAudio(); });

function addUlt(amount) { player.ultEnergy = Math.min(player.maxUlt, player.ultEnergy + (amount * 0.35 * 1.5)); }

function takeDamage(damage) {
    player.hp -= damage; 
    lastHitTime = Date.now();
    playSound('hit');
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

function startGame(type) {
    initAudio();
    player.charType = type;
    document.getElementById('class-select').style.display = 'none';
    
    let skNames = {
        'Gojo': ['신속이동', '아카', '아오', '무라사키', '무량공처'],
        'Sukuna': ['신속폭주', '해(解)', '팔(捌)', '푸가', '복마어주자']
    };
    
    document.getElementById('char-name').innerText = type === 'Gojo' ? '원작 고죠 사토루' : '양면 스쿠나';
    document.getElementById('sk-q').innerText = skNames[type][0];
    document.getElementById('sk-e').innerText = skNames[type][1];
    document.getElementById('sk-r').innerText = skNames[type][2];
    document.getElementById('sk-t').innerText = skNames[type][3];
    document.getElementById('sk-x').innerText = type === 'Gojo' ? '무량공처' : '복마어주자';

    for(let i=0; i<50; i++) spawnCurse();
    spawnBoss();
    requestAnimationFrame(gameLoop);
}

document.getElementById('card-gojo').addEventListener('click', () => startGame('Gojo'));
document.getElementById('card-sukuna').addEventListener('click', () => startGame('Sukuna'));
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
    let attackInterval = 600;
    if(now - player.lastAttack < attackInterval) return;
    player.lastAttack = now;

    let ang = getAutoAimAngle();
    addUlt(0.8);
    player.facing = Math.cos(ang) >= 0 ? 1 : -1;
    playSound('shoot');

    if(player.charType === 'Gojo') {
        let shotX = player.x + Math.cos(ang) * 20;
        let shotY = player.y + Math.sin(ang) * 20;
        projectiles.push({
            x: shotX, y: shotY, vx: Math.cos(ang)*18, vy: Math.sin(ang)*18,
            damage: 90, radius: 12, color: '#00d2ff', type:'gojo_hq_basic', trailTimer: 25
        });
        for(let i=0; i<8; i++) {
            highQualityShots.push({
                x: shotX, y: shotY, vx: Math.cos(ang + (Math.random()-0.5)*0.5)*(Math.random()*6+3), vy: Math.sin(ang + (Math.random()-0.5)*0.5)*(Math.random()*6+3),
                radius: Math.random()*5+2, life: 18, color: '#70a1ff'
            });
        }
    } else {
        slashes.push({x: player.x + Math.cos(ang)*30, y: player.y + Math.sin(ang)*30, ang: ang, length: 80, life: 6, damage: 70});
    }
}

function castSkill(key) {
    if(isGameOver) return;
    if(cooldowns[key] > 0) return;
    if(key === 'X' && player.ultEnergy < player.maxUlt) return;

    let ang = getAutoAimAngle();
    let targetX = player.x + Math.cos(ang) * 250;
    let targetY = player.y + Math.sin(ang) * 250;

    playSound('skill');

    if(key === 'X' && player.charType === 'Gojo') {
        gojoDomainCount++;
        if(gojoDomainCount >= 4) {
            showDialogue('뇌에 과부하가 걸렸다...');
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
        player.x += Math.cos(ang) * 350;
        player.y += Math.sin(ang) * 350;
        triggerVibration(20);
        addUlt(3.0);
    } else if(key === 'E') {
        cooldowns.E = maxCooldowns[player.charType].E;
        addUlt(2.5);
        
        if(player.charType === 'Gojo') {
            triggerVibration(30);
            let finalTargetX = targetX;
            let finalTargetY = targetY;
            if(blackHoles.length > 0) {
                finalTargetX = blackHoles[0].x;
                finalTargetY = blackHoles[0].y;
            }
            let autoAng = Math.atan2(finalTargetY - player.y, finalTargetX - player.x);

            projectiles.push({
                x: player.x, y: player.y, 
                targetX: finalTargetX, targetY: finalTargetY,
                vx: Math.cos(autoAng)*22, vy: Math.sin(autoAng)*22,
                type: 'aka', damage: 4500, radius: 28, maxDist: Math.hypot(finalTargetX - player.x, finalTargetY - player.y), traveled: 0
            });
        } else {
            for(let i=-2; i<=2; i++) {
                slashes.push({ x: player.x, y: player.y, ang: ang + i*0.2, length: 220, life: 14, damage: 1500 });
            }
        }
    } else if(key === 'R') {
        cooldowns.R = maxCooldowns[player.charType].R;
        addUlt(4.0);
        
        if(player.charType === 'Gojo') {
            triggerVibration(25);
            blackHoles.push({
                orbitAngle: ang, orbitRadius: 160, radius: 90, life: 350, damage: 2500, x: player.x, y: player.y
            });
        } else {
            for(let i=0; i<12; i++) {
                slashes.push({
                    x: targetX + (Math.random()-0.5)*200, y: targetY + (Math.random()-0.5)*200,
                    ang: Math.random()*Math.PI*2, length: 160, life: 12, damage: 1800
                });
            }
        }
    } else if(key === 'T') {
        cooldowns.T = maxCooldowns[player.charType].T;
        if(player.charType === 'Gojo') {
            addUlt(6.0);
            triggerVibration(45);
            playSound('explosion');
            
            purpleProjectiles.push({
                x: player.x + Math.cos(ang)*35, 
                y: player.y + Math.sin(ang)*35,
                vx: Math.cos(ang) * 11, 
                vy: Math.sin(ang) * 11,
                phase: 'expanding', 
                timer: 110, 
                currentRadius: 4,
                maxRadius: 160,
                life: 400, 
                damage: 99999, 
                ang: ang
            });
        } else {
            addUlt(5.0);
            playSound('explosion');
            explosions.push({x: targetX, y: targetY, radius: 180, maxRadius: 180, color: '#e67e22', life: 30, damage: 4000});
        }
    } else if(key === 'X') {
        player.ultEnergy = 0;
        playSound('explosion');
        if(player.charType === 'Gojo') {
            activeDomain = { type: 'Gojo', timer: 1200 };
        } else {
            activeDomain = { type: 'Sukuna', timer: 1000 };
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
        isBoss: false, isRanged: isRanged
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
        isBoss: true
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
    let gOver = document.getElementById('game-over');
    gOver.style.display = 'flex';
    gOver.style.zIndex = '9999';
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

    if(player.charType === 'Gojo') {
        limitlessTimer += 0.016; 
        if(!limitlessActive && limitlessTimer >= 6.0) {
            limitlessActive = true;
            limitlessDurationCounter = 200; 
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
            let progress = (110 - pp.timer) / 110;
            pp.currentRadius = 4 + (pp.maxRadius - 4) * progress;
            
            if(pp.timer <= 0) {
                pp.phase = 'charging';
                pp.timer = 30; 
                triggerVibration(20);
            }
        } else if(pp.phase === 'charging') {
            pp.timer--;
            if(pp.timer <= 0) {
                pp.phase = 'firing';
                triggerVibration(45);
                playSound('explosion');
                permanentCraters.push({ x: pp.x, y: pp.y, radius: pp.maxRadius * 1.5 });
            }
        } else if(pp.phase === 'firing') {
            pp.x += pp.vx * 2.2;
            pp.y += pp.vy * 2.2;

            enemies.forEach(e => {
                let dist = Math.hypot(e.x - pp.x, e.y - pp.y);
                if(dist < e.radius + pp.maxRadius) {
                    e.hp -= 99999;
                }
            });
        }

        if(pp.life <= 0 || pp.x < 0 || pp.x > WORLD_WIDTH || pp.y < 0 || pp.y > WORLD_HEIGHT) {
            purpleProjectiles.splice(ppi, 1);
        }
    });

    blackHoles.forEach((bh, bhi) => {
        bh.life--;
        bh.orbitAngle += 0.05;
        bh.x = player.x + Math.cos(bh.orbitAngle) * bh.orbitRadius;
        bh.y = player.y + Math.sin(bh.orbitAngle) * bh.orbitRadius;

        enemies.forEach(e => {
            let d = Math.hypot(bh.x - e.x, bh.y - e.y);
            if(d < bh.radius * 2.2) {
                let pullAng = Math.atan2(bh.y - e.y, bh.x - e.x);
                e.x += Math.cos(pullAng) * 6;
                e.y += Math.sin(pullAng) * 6;
            }
        });

        enemyProjectiles.forEach(ep => {
            let d = Math.hypot(bh.x - ep.x, bh.y - ep.y);
            if(d < bh.radius * 2) {
                let pullAng = Math.atan2(bh.y - ep.y, bh.x - ep.x);
                ep.vx += Math.cos(pullAng) * 2;
                ep.vy += Math.sin(pullAng) * 2;
            }
        });

        if(bh.life <= 0) {
            blackHoles.splice(bhi, 1);
        }
    });

    blueOrbs.forEach((bo, boi) => {
        bo.life--;
        if(bo.life <= 0) blueOrbs.splice(boi, 1);
    });

    enemyProjectiles.forEach((ep, epi) => {
        ep.x += ep.vx; ep.y += ep.vy;
        if(Math.hypot(player.x - ep.x, player.y - ep.y) < ep.radius + 15) {
            takeDamage(ep.damage);
            triggerVibration(8);
            enemyProjectiles.splice(epi, 1);
        }
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
                if(Math.hypot(deb.x - p.x, deb.y - p.y) < deb.radius + p.radius + 40) {
                    hitDebrisIdx = di;
                }
            });

            if(hitDebrisIdx !== -1) {
                let deb = debrisList[hitDebrisIdx];
                debrisList.splice(hitDebrisIdx, 1);

                explosions.push({
                    x: deb.x, y: deb.y, radius: 40, maxRadius: 3500, color: 'rgba(168, 85, 247, 0.95)', life: 40, damage: 999999
                });
                permanentCraters.push({ x: deb.x, y: deb.y, radius: 2500 });
                triggerVibration(60);
                playSound('explosion');
                showDialogue('💥 잔해 연계 자폭 무라사키 발동!!');

                enemies.forEach(e => { e.hp = 0; });

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
                    x: p.x, y: p.y, radius: 30, maxRadius: 380, color: 'rgba(255, 71, 87, 0.85)', life: 20, damage: p.damage
                });
                permanentCraters.push({ x: p.x, y: p.y, radius: 380 });
                projectiles.splice(pi, 1);
                triggerVibration(25);
                playSound('explosion');
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
                    radius: Math.random()*6+3, life: 60, color: e.isBoss ? '#ff4757' : '#00d2ff'
                });
            }

            debrisList.push({
                x: e.x, y: e.y, radius: 22, life: 900 
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

    ctx.strokeStyle = 'rgba(0, 210, 255, 0.06)';
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
        ctx.fillStyle = 'rgba(5, 2, 10, 0.7)';
        ctx.beginPath(); ctx.arc(cr.x, cr.y, cr.radius * 0.85, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = 'rgba(0, 210, 255, 0.35)';
        ctx.lineWidth = 4;
        ctx.stroke();
        ctx.restore();
    });

    debrisList.forEach(deb => {
        ctx.save();
        ctx.fillStyle = '#2f3542';
        ctx.beginPath(); ctx.arc(deb.x, deb.y, deb.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#00d2ff'; ctx.lineWidth = 2.5; ctx.stroke();
        ctx.fillStyle = '#70a1ff'; ctx.font = '10px Consolas'; ctx.textAlign = 'center';
        ctx.fillText('술식 잔해', deb.x, deb.y - deb.radius - 6);
        ctx.restore();
    });

    bloodSplatters.forEach(bs => {
        ctx.fillStyle = bs.color;
        ctx.beginPath(); ctx.arc(bs.x, bs.y, bs.radius, 0, Math.PI*2); ctx.fill();
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
        ctx.fillStyle = 'rgba(0, 210, 255, 0.35)';
        ctx.beginPath(); ctx.arc(bh.x, bh.y, bh.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#00d2ff'; ctx.lineWidth = 4; ctx.stroke();
        ctx.shadowBlur = 30; ctx.shadowColor = '#00d2ff';
        ctx.restore();
    });

    purpleProjectiles.forEach(pp => {
        ctx.save();
        if(pp.phase === 'expanding') {
            ctx.fillStyle = 'rgba(168, 85, 247, 0.8)';
            ctx.beginPath(); ctx.arc(pp.x, pp.y, pp.currentRadius, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#d290ff'; ctx.lineWidth = 4; ctx.stroke();
            ctx.shadowBlur = 30; ctx.shadowColor = '#a855f7';
        } else if(pp.phase === 'charging') {
            let isFlash = Math.floor(Date.now() / 40) % 2 === 0;
            ctx.fillStyle = isFlash ? 'rgba(255, 255, 255, 0.95)' : 'rgba(224, 86, 253, 0.95)';
            ctx.beginPath(); ctx.arc(pp.x, pp.y, pp.maxRadius, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#ffffff'; ctx.lineWidth = isFlash ? 8 : 4; ctx.stroke();
            ctx.shadowBlur = 70; ctx.shadowColor = '#ffffff';
        } else if(pp.phase === 'firing') {
            ctx.fillStyle = '#e056fd';
            ctx.beginPath(); ctx.arc(pp.x, pp.y, pp.maxRadius, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#fff'; ctx.lineWidth = 6; ctx.stroke();
            ctx.shadowBlur = 80; ctx.shadowColor = '#a855f7';
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
        ctx.fillStyle = e.isBoss ? '#ff4757' : '#00d2ff';
        ctx.fillRect(e.x - barW/2, e.y - e.radius - 14, barW * (e.hp / e.maxHp), 6);

        ctx.fillStyle = '#fff'; ctx.font = '11px Consolas'; ctx.textAlign = 'center';
        ctx.fillText(e.name || '주령', e.x, e.y - e.radius - 18);
        ctx.restore();
    });

    ctx.save();
    if(player.charType === 'Gojo') {
        let pulse = Math.sin(Date.now() / 150) * 4;

        ctx.strokeStyle = 'rgba(0, 210, 255, 0.45)';
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(player.x, player.y, 32 + pulse, 0, Math.PI*2); ctx.stroke();

        ctx.fillStyle = '#1e272e';
        ctx.beginPath();
        ctx.arc(player.x, player.y - 4, 22, Math.PI, 0, false);
        ctx.fill();

        ctx.fillStyle = '#2f3542';
        ctx.beginPath(); ctx.arc(player.x, player.y + 2, 20, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#70a1ff'; ctx.lineWidth = 3; ctx.stroke();

        ctx.fillStyle = '#000000';
        ctx.beginPath();
        ctx.rect(player.x - 15, player.y - 10, 30, 8);
        ctx.fill();
        ctx.strokeStyle = '#00d2ff'; ctx.lineWidth = 1.5; ctx.stroke();
    } else {
        ctx.fillStyle = '#ff4757';
        ctx.beginPath(); ctx.arc(player.x, player.y, 22, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.stroke();
    }

    if(limitlessActive) {
        ctx.strokeStyle = 'rgba(0, 210, 255, 0.85)';
        ctx.lineWidth = 4;
        ctx.beginPath(); ctx.arc(player.x, player.y, 46, 0, Math.PI*2); ctx.stroke();
    }

    ctx.fillStyle = '#fff'; ctx.font = 'bold 13px Consolas'; ctx.textAlign = 'center';
    ctx.fillText(player.charType === 'Gojo' ? '고죠 사토루' : '스쿠나', player.x, player.y - 45);
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
