import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="주술회전: 보스 무한 침공 패치")

st.markdown("""
    <style>
        .main .block-container {
            max-width: 100% !important;
            padding: 0rem !important;
        }
        iframe { width: 100% !important; border: none; }
        header { visibility: hidden; }
        footer { visibility: hidden; }
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
    canvas { display: block; cursor: crosshair; }
    
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
    
    #boss-hud {
        position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
        width: 520px; background: rgba(15, 5, 5, 0.9);
        border: 2px solid #ff4757; border-radius: 10px; padding: 10px 20px;
        text-align: center; display: none; z-index: 15;
    }
    .boss-bar-outer { width: 100%; height: 16px; background: rgba(255,255,255,0.1); border-radius: 8px; overflow: hidden; margin-top: 5px; }
    .boss-bar-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff4757, #ff6b81); transition: width 0.1s; }

    .skill-container { display: flex; gap: 10px; margin-top: 8px; }
    .skill-icon {
        position: relative;
        width: 55px; height: 55px; background: rgba(255,255,255,0.08);
        border: 1px solid #a855f7; border-radius: 10px;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        font-size: 10px; font-weight: bold; color: #fff; overflow: hidden;
    }
    .skill-key { font-size: 13px; color: #e056fd; }
    .cooldown-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.75); color: #ff4757; font-size: 15px; font-weight: bold;
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
    
    <div id="boss-hud">
        <div id="boss-name" style="color:#ff4757; font-weight:bold; font-size:16px;">[LV.1] 특급 주령 - 화곤</div>
        <div class="boss-bar-outer"><div id="boss-hp-bar" class="boss-bar-hp"></div></div>
    </div>

    <div id="ui-layer">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div class="hud-card">
                <div id="char-name" style="color:#a855f7; font-weight:bold; font-size:16px;">주술사</div>
                <div style="font-size:10px; color:#aaa; margin-top:4px;">체력 (HP) <span id="regen-status" style="color:#2ecc71;">[3초 미피격 회복]</span></div>
                <div class="bar-outer"><div id="hp-bar" class="bar-hp"></div></div>
                <div style="font-size:10px; color:#aaa;">궁극기 게이지 (ULT) [X]</div>
                <div class="bar-outer"><div id="ult-bar" class="bar-ult"></div></div>
                
                <div class="skill-container">
                    <div class="skill-icon" style="border-color:#3498db;">
                        <span class="skill-key" style="color:#3498db;">L-Click</span><span>기본공격</span>
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
                <div style="font-size:16px; font-weight:bold; color:#a855f7;">🎮 WASD 이동 | 좌클릭 공격 | E,R,T,X 스킬</div>
                <div id="kill-status" style="font-size:14px; color:#aaa; margin-top:6px;">제령한 주령: 0마리</div>
            </div>
        </div>
    </div>

    <div id="dialogue-box">
        <div id="dialogue-text">영역전개 「무량처공」</div>
    </div>

    <div id="class-select">
        <h1 style="color:#f3e8ff; font-size:48px; letter-spacing:2px; text-shadow:0 0 20px #a855f7;">JUJUTSU KAISEN</h1>
        <p style="color:#a1a1aa; margin-top:10px;">플레이할 주술사를 선택하십시오.</p>
        <div class="card-group">
            <div class="card" onclick="selectChar('Gojo')">
                <h2 style="color:#70a1ff;">👁️ 고죠 사토루</h2>
                <p>
                    • 좌클릭: 주력 탄환<br>
                    • E: 술식 반전 「아카」<br>
                    • R: 술식 순전 「아오」<br>
                    • T: 허식 「무라사키」<br>
                    • <strong>★특수: 아오+아카 자폭 무라사키</strong><br>
                    • <strong>★회복: 3초 미피격 시 완만하게 HP 회복</strong>
                </p>
            </div>
            <div class="card" onclick="selectChar('Sukuna')">
                <h2 style="color:#ff4757;">👹 양면 스쿠나</h2>
                <p>
                    • 좌클릭: 근거리 참격<br>
                    • E: 광범위 참격 「해(解)」<br>
                    • R: 난사 절단 「팔(捌)」<br>
                    • T: 화염 신화 「푸가(🔥)」<br>
                    • <strong>X: 영역전개 「복마어주자」</strong>
                </p>
            </div>
            <div class="card" onclick="selectChar('Megumi')">
                <h2 style="color:#2ecc71;">🐺 후시구로 메구미</h2>
                <p>
                    • 좌클릭: 그림자 탄환<br>
                    • E: 십종영법술 「누에」<br>
                    • R: 십종영법술 「옥견」<br>
                    • T: 그림자 속박<br>
                    • <strong>X: 마허라 소환</strong>
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
let mouseWorld = { x: 0, y: 0 };
let dialogueTimeout = null;

let lastHitTime = Date.now();
let bossSpawnTimer = null;

let player = {
    x: WORLD_WIDTH / 2, y: WORLD_HEIGHT / 2,
    speed: 5.8, hp: 250, maxHp: 250,
    ultEnergy: 0, maxUlt: 100,
    charType: 'Gojo', facing: 1, lastAttack: 0
};

let cooldowns = { E: 0, R: 0, T: 0, X: 0 };
let maxCooldowns = {
    Gojo: { E: 3, R: 5, T: 10, X: 0 },
    Sukuna: { E: 2, R: 4, T: 6, X: 0 },
    Megumi: { E: 3, R: 5, T: 6, X: 0 }
};

let dialogues = {
    Gojo: { E: '술식 반전 「아카」', R: '술식 순전 「아오」', T: '허식 「무라사키」', X: '영역전개 「무량처공」' },
    Sukuna: { E: '참격 「해(解)」', R: '참격 「팔(捌)」', T: '「푸가(🔥)」', X: '영역전개 「복마어주자」' },
    Megumi: { E: '십종영법술 「누에」', R: '십종영법술 「옥견」', T: '그림자 속박', X: '팔지검 이계신장 강대마허라' }
};

let activeDomain = null;
let mahoraga = null;
let keys = {};
let projectiles = [];
let slashes = [];
let explosions = [];
let blackHoles = [];     
let blueOrbs = [];       
let purpleEffects = [];   
let meleeAttacks = [];
let enemies = [];

// 레벨별 보스 디자인/설정 정의
const BOSS_CONFIGS = [
    { level: 1, name: '하급 특급주령 - 화곤', hp: 2000, radius: 45, speed: 1.8, dmg: 25, color: '#e74c3c', aura: '#ff7675' },
    { level: 2, name: '중급 특급주령 - 다라', hp: 4500, radius: 55, speed: 2.2, dmg: 40, color: '#e67e22', aura: '#f39c12' },
    { level: 3, name: '상급 특급주령 - 죠고', hp: 9000, radius: 65, speed: 2.6, dmg: 60, color: '#d35400', aura: '#e67e22' },
    { level: 4, name: '최상급 주령 - 하나미', hp: 16000, radius: 75, speed: 3.0, dmg: 85, color: '#27ae60', aura: '#2ecc71' },
    { level: 5, name: '재앙의 주령 - 마히토', hp: 28000, radius: 85, speed: 3.4, dmg: 120, color: '#8e44ad', aura: '#9b59b6' },
    { level: 6, name: '원초의 마왕 - 두면사신', hp: 50000, radius: 100, speed: 3.8, dmg: 160, color: '#c0392b', aura: '#e74c3c' }
];

window.addEventListener('mousemove', e => {
    mouseWorld.x = e.clientX + camera.x;
    mouseWorld.y = e.clientY + camera.y;
});

window.addEventListener('mousedown', e => { if(e.button === 0) basicAttack(); });

window.addEventListener('keydown', e => {
    let k = e.key.toLowerCase();
    keys[k] = true;
    if(k === 'e') castSkill('E');
    if(k === 'r') castSkill('R');
    if(k === 't') castSkill('T');
    if(k === 'x') castSkill('X');
});
window.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

function addUlt(amount) {
    player.ultEnergy = Math.min(player.maxUlt, player.ultEnergy + amount);
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
    dialogueTimeout = setTimeout(() => box.style.opacity = '0', 1500);
}

function triggerVibration(intensity) {
    screenShake = intensity;
    if (navigator.vibrate) navigator.vibrate(intensity * 15);
}

function selectChar(type) {
    player.charType = type;
    document.getElementById('class-select').style.display = 'none';
    
    let skNames = {
        'Gojo': ['아카', '아오', '무라사키', '무량처공'],
        'Sukuna': ['해(解)', '팔(捌)', '푸가', '복마어주자'],
        'Megumi': ['누에', '옥견', '그림자', '마허라']
    };
    
    document.getElementById('char-name').innerText = type === 'Gojo' ? '고죠 사토루' : (type === 'Sukuna' ? '양면 스쿠나' : '후시구로 메구미');
    document.getElementById('sk-e').innerText = skNames[type][0];
    document.getElementById('sk-r').innerText = skNames[type][1];
    document.getElementById('sk-t').innerText = skNames[type][2];

    for(let i=0; i<15; i++) spawnCurse();

    // 5초 간격 보스 자동 스폰 타이머 설정
    bossSpawnTimer = setInterval(() => {
        if(!isGameOver) spawnBoss();
    }, 5000);

    gameLoop();
}

function basicAttack() {
    if(isGameOver) return;
    let now = Date.now();
    if(now - player.lastAttack < 180) return;
    player.lastAttack = now;

    addUlt(2.0);
    let ang = Math.atan2(mouseWorld.y - player.y, mouseWorld.x - player.x);

    if(player.charType === 'Gojo') {
        projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang)*15, vy: Math.sin(ang)*15, damage: 35, radius: 8, color: '#70a1ff', type:'normal'});
    } else if(player.charType === 'Sukuna') {
        slashes.push({x: player.x + Math.cos(ang)*30, y: player.y + Math.sin(ang)*30, ang: ang, length: 80, life: 6, damage: 45});
    } else {
        projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang)*14, vy: Math.sin(ang)*14, damage: 30, radius: 7, color: '#2ecc71', type:'normal'});
    }
}

function castSkill(key) {
    if(isGameOver) return;
    if(cooldowns[key] > 0) return;
    if(key === 'X' && player.ultEnergy < player.maxUlt) return;

    let targetX = mouseWorld.x;
    let targetY = mouseWorld.y;
    let ang = Math.atan2(targetY - player.y, targetX - player.x);

    showDialogue(dialogues[player.charType][key]);

    if(key === 'E') {
        cooldowns.E = maxCooldowns[player.charType].E;
        addUlt(8.0);
        
        if(player.charType === 'Gojo') {
            triggerVibration(18);
            projectiles.push({
                x: player.x, y: player.y, targetX: targetX, targetY: targetY,
                vx: Math.cos(ang)*18, vy: Math.sin(ang)*18,
                type: 'aka', damage: 220, radius: 14
            });
        } else if(player.charType === 'Sukuna') {
            triggerVibration(15);
            for(let i=-2; i<=2; i++) {
                slashes.push({ x: player.x, y: player.y, ang: ang + i*0.2, length: 220, life: 14, damage: 95 });
            }
        } else {
            triggerVibration(8);
            explosions.push({x: targetX, y: targetY, radius: 70, maxRadius: 70, color: '#f1c40f', life: 15, damage: 120});
        }
    } else if(key === 'R') {
        cooldowns.R = maxCooldowns[player.charType].R;
        addUlt(12.0);
        
        if(player.charType === 'Gojo') {
            triggerVibration(14);
            blackHoles.push({x: targetX, y: targetY, radius: 180, life: 120, damage: 180});
        } else if(player.charType === 'Sukuna') {
            triggerVibration(20);
            for(let i=0; i<12; i++) {
                slashes.push({
                    x: targetX + (Math.random()-0.5)*200, y: targetY + (Math.random()-0.5)*200,
                    ang: Math.random()*Math.PI*2, length: 160, life: 12, damage: 130
                });
            }
        } else {
            triggerVibration(10);
            projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang)*15, vy: Math.sin(ang)*15, type:'normal', damage: 100, radius: 10, color: '#2ecc71'});
        }
    } else if(key === 'T') {
        cooldowns.T = maxCooldowns[player.charType].T;
        if(player.charType === 'Gojo') {
            addUlt(20.0);
            triggerVibration(28);
            projectiles.push({
                x: player.x, y: player.y, vx: Math.cos(ang)*22, vy: Math.sin(ang)*22,
                damage: 660, radius: 35, color: '#8e44ad', type: 'murasaki'
            });
        } else if(player.charType === 'Sukuna') {
            addUlt(15.0);
            triggerVibration(12);
            explosions.push({x: targetX, y: targetY, radius: 180, maxRadius: 180, color: '#e67e22', life: 30, damage: 300});
        } else {
            addUlt(15.0);
            triggerVibration(12);
            enemies.forEach(e => { if(Math.hypot(e.x - player.x, e.y - player.y) < 300) e.speed = 0.5; });
        }
    } else if(key === 'X') {
        player.ultEnergy = 0;
        triggerVibration(30);
        if(player.charType === 'Gojo') activeDomain = { type: 'Gojo', timer: 220 };
        else if(player.charType === 'Sukuna') activeDomain = { type: 'Sukuna', timer: 200 };
        else mahoraga = { x: player.x, y: player.y - 50, life: 600 };
    }
}

function triggerPurpleExplosion(x, y, boIndex) {
    showDialogue('허식 「무라사키」 (자폭)');
    triggerVibration(60);

    if(boIndex !== undefined && boIndex !== null && boIndex >= 0 && boIndex < blueOrbs.length) {
        blueOrbs.splice(boIndex, 1);
    }

    takeDamage(player.hp * 0.8);
    if(player.hp < 1) player.hp = 1;

    for (let i = 0; i < 120; i++) {
        let pAng = Math.random() * Math.PI * 2;
        let pDist = Math.random() * 400 + 50;
        let pSpeed = Math.random() * 12 + 6;
        purpleEffects.push({
            x: x + Math.cos(pAng) * pDist, y: y + Math.sin(pAng) * pDist,
            targetX: x, targetY: y,
            vx: -Math.cos(pAng) * pSpeed, vy: -Math.sin(pAng) * pSpeed,
            radius: Math.random() * 8 + 4, life: 45, color: i % 2 === 0 ? '#a855f7' : '#e056fd'
        });
    }

    explosions.push({
        x: x, y: y, radius: 2500, maxRadius: 2500,
        color: 'rgba(168, 85, 247, 0.9)', life: 50, damage: 9999
    });
    enemies.forEach(e => { e.hp -= 9999; });
}

function spawnCurse() {
    let x = Math.random() * WORLD_WIDTH;
    let y = Math.random() * WORLD_HEIGHT;
    if(Math.hypot(x - player.x, y - player.y) < 400) return;

    enemies.push({
        x: x, y: y, radius: 20,
        hp: 120, maxHp: 120, speed: 2.5, isBoss: false, attackCd: 0
    });
}

// 레벨별 보스 소환 함수 (5초 간격 자동 실행)
function spawnBoss() {
    let lvlIdx = Math.min(BOSS_CONFIGS.length - 1, Math.floor(killCount / 5));
    let cfg = BOSS_CONFIGS[lvlIdx];

    let spawnAngle = Math.random() * Math.PI * 2;
    let spawnDist = 600 + Math.random() * 200;
    let bx = player.x + Math.cos(spawnAngle) * spawnDist;
    let by = player.y + Math.sin(spawnAngle) * spawnDist;

    bx = Math.max(100, Math.min(WORLD_WIDTH - 100, bx));
    by = Math.max(100, Math.min(WORLD_HEIGHT - 100, by));

    let boss = {
        x: bx, y: by,
        level: cfg.level, name: cfg.name,
        hp: cfg.hp, maxHp: cfg.hp,
        radius: cfg.radius, speed: cfg.speed, dmg: cfg.dmg,
        color: cfg.color, aura: cfg.aura,
        isBoss: true, attackCd: 0
    };
    
    enemies.push(boss);
    showDialogue(`⚠️ [LV.${cfg.level}] 보스 출현!`);
    triggerVibration(15);
}

function triggerGameOver() {
    isGameOver = true;
    if(bossSpawnTimer) clearInterval(bossSpawnTimer);
    document.getElementById('ui-layer').style.display = 'none';
    document.getElementById('game-over').style.display = 'flex';
    document.getElementById('final-stats').innerText = `제령한 주령 수: ${killCount}마리`;
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
            player.hp = Math.min(player.maxHp, player.hp + (player.maxHp * 0.003)); 
        }
    }
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

    if(enemies.filter(e => !e.isBoss).length < 18) spawnCurse();

    if(activeDomain) {
        activeDomain.timer--;
        triggerVibration(5);
        if(activeDomain.type === 'Gojo') enemies.forEach(e => { e.speed = 0; });
        else if(activeDomain.type === 'Sukuna') {
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
        let target = activeBosses[0] || enemies[0];
        if(target) {
            let ang = Math.atan2(target.y - mahoraga.y, target.x - mahoraga.x);
            mahoraga.x += Math.cos(ang) * 4.5; mahoraga.y += Math.sin(ang) * 4.5;
            if(Math.hypot(target.x - mahoraga.x, target.y - mahoraga.y) < 60) target.hp -= 20;
        }
        if(mahoraga.life <= 0) mahoraga = null;
    }

    blackHoles.forEach((bh, bhi) => {
        bh.life--;
        enemies.forEach(e => {
            let d = Math.hypot(bh.x - e.x, bh.y - e.y);
            if(d < bh.radius) {
                let pullAng = Math.atan2(bh.y - e.y, bh.x - e.x);
                e.x += Math.cos(pullAng) * 7;
                e.y += Math.sin(pullAng) * 7;
                e.hp -= 1.5;
                if(e.hp <= 0) blueOrbs.push({ x: bh.x, y: bh.y, radius: 45, life: 300 });
            }
        });
        if(bh.life <= 0) {
            explosions.push({x: bh.x, y: bh.y, radius: 120, maxRadius: 120, color: '#3742fa', life: 15, damage: bh.damage});
            blackHoles.splice(bhi, 1);
        }
    });

    blueOrbs.forEach((bo, boi) => {
        bo.life--;
        if(bo.life <= 0) blueOrbs.splice(boi, 1);
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

            if(Math.hypot(p.targetX - p.x, p.targetY - p.y) < 20) {
                triggerVibration(22);
                explosions.push({x: p.x, y: p.y, radius: 130, maxRadius: 130, color: '#ff4757', life: 20, damage: p.damage});
                projectiles.splice(pi, 1);
                return;
            }
        }

        enemies.forEach((e) => {
            if(Math.hypot(e.x - p.x, e.y - p.y) < e.radius + p.radius) {
                e.hp -= p.damage;
                if(p.type === 'normal') projectiles.splice(pi, 1);
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
        else e.speed = e.isBoss ? e.speed : 2.5;

        let ang = Math.atan2(player.y - e.y, player.x - e.x);
        let dist = Math.hypot(player.x - e.x, player.y - e.y);

        e.x += Math.cos(ang) * e.speed;
        e.y += Math.sin(ang) * e.speed;

        e.attackCd = (e.attackCd || 0) + 1;

        if(dist < e.radius + 30 && e.speed > 0) {
            if(e.attackCd >= (e.isBoss ? 25 : 40)) {
                e.attackCd = 0;
                let dmg = e.isBoss ? e.dmg : 12;
                takeDamage(dmg);
                triggerVibration(e.isBoss ? 15 : 6);

                meleeAttacks.push({
                    x: (e.x + player.x) / 2, y: (e.y + player.y) / 2,
                    ang: ang, radius: e.isBoss ? e.radius + 10 : 25, life: 10, isBoss: e.isBoss
                });
            }
        }

        if(e.hp <= 0) {
            killCount++;
            addUlt(e.isBoss ? 15.0 : 3.0);
            enemies.splice(ei, 1);
        }
    });

    document.getElementById('hp-bar').style.width = Math.max(0, (player.hp / player.maxHp * 100)) + '%';
    document.getElementById('ult-bar').style.width = Math.min(100, (player.ultEnergy / player.maxUlt * 100)) + '%';
    document.getElementById('kill-status').innerText = `제령한 주령: ${killCount}마리`;
}

function drawPlayerSprite(p) {
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.scale(p.facing, 1);

    if(p.charType === 'Gojo') {
        ctx.shadowBlur = 15; ctx.shadowColor = '#70a1ff';
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

// 레벨별 보스 스프라이트 및 머리 위 레벨 텍스트 렌더링
function drawEnemySprite(e) {
    ctx.save();
    ctx.translate(e.x, e.y);

    if(e.isBoss) {
        // 보스 레벨별 오라 및 외형
        ctx.shadowBlur = 20 + e.level * 5; ctx.shadowColor = e.aura;
        ctx.fillStyle = e.color;
        ctx.beginPath(); ctx.arc(0, 0, e.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 3 + Math.floor(e.level / 2); ctx.stroke();
        
        // 보스 레벨별 뿔/장식 갯수 증가
        ctx.fillStyle = '#ffffff';
        for(let i=0; i<Math.min(e.level, 6); i++) {
            let eyeAng = (Math.PI * 2 / e.level) * i;
            ctx.beginPath();
            ctx.arc(Math.cos(eyeAng) * (e.radius * 0.5), Math.sin(eyeAng) * (e.radius * 0.5), 6, 0, Math.PI*2);
            ctx.fill();
        }
        ctx.shadowBlur = 0;

        // 보스 머리 위 레벨 텍스트
        ctx.fillStyle = '#ff4757';
        ctx.font = 'bold 16px Consolas';
        ctx.textAlign = 'center';
        ctx.fillText(`[LV.${e.level}]`, 0, -e.radius - 12);
    } else {
        ctx.fillStyle = '#1e272e';
        ctx.beginPath(); ctx.arc(0, 0, e.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#57606f'; ctx.lineWidth = 2; ctx.stroke();
        
        ctx.fillStyle = '#e74c3c';
        ctx.beginPath(); ctx.arc(-6, -4, 4, 0, Math.PI*2); ctx.fill();
        ctx.beginPath(); ctx.arc(6, -4, 4, 0, Math.PI*2); ctx.fill();
    }
    ctx.restore();
}

function draw() {
    ctx.save();
    if(screenShake > 0) ctx.translate((Math.random()-0.5)*screenShake, (Math.random()-0.5)*screenShake);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.translate(-camera.x, -camera.y);

    if(activeDomain) {
        ctx.fillStyle = activeDomain.type === 'Gojo' ? 'rgba(10, 10, 35, 0.65)' : 'rgba(40, 5, 5, 0.65)';
        ctx.fillRect(camera.x, camera.y, canvas.width, canvas.height);
    }

    ctx.strokeStyle = 'rgba(168, 85, 247, 0.06)'; ctx.lineWidth = 1;
    for(let x=0; x<WORLD_WIDTH; x+=100) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,WORLD_HEIGHT); ctx.stroke(); }
    for(let y=0; y<WORLD_HEIGHT; y+=100) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(WORLD_WIDTH,y); ctx.stroke(); }

    blackHoles.forEach(bh => {
        ctx.fillStyle = 'rgba(55, 66, 250, 0.35)';
        ctx.beginPath(); ctx.arc(bh.x, bh.y, bh.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#5352ed'; ctx.lineWidth = 3; ctx.stroke();
    });

    blueOrbs.forEach(bo => {
        let alpha = bo.life / 300;
        ctx.shadowBlur = 35; ctx.shadowColor = '#0026ff';
        ctx.fillStyle = `rgba(0, 38, 255, ${alpha})`;
        ctx.beginPath(); ctx.arc(bo.x, bo.y, bo.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = `rgba(100, 200, 255, ${alpha})`; ctx.lineWidth = 5; ctx.stroke();
        ctx.shadowBlur = 0;
    });

    if(mahoraga) {
        ctx.fillStyle = '#ffffff';
        ctx.beginPath(); ctx.arc(mahoraga.x, mahoraga.y, 30, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#f1c40f'; ctx.lineWidth = 4; ctx.stroke();
    }

    enemies.forEach(e => drawEnemySprite(e));

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
        ctx.fillStyle = p.color || (p.type === 'aka' ? '#ff4757' : '#3742fa');
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
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
