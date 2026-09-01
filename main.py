import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="주술회전: 타겟팅 스킬 & 보스전")

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
    
    /* 보스 체력바 */
    #boss-hud {
        position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
        width: 500px; background: rgba(15, 5, 5, 0.9);
        border: 2px solid #ff4757; border-radius: 10px; padding: 10px 20px;
        text-align: center; display: none; z-index: 15;
    }
    .boss-bar-outer { width: 100%; height: 16px; background: rgba(255,255,255,0.1); border-radius: 8px; overflow: hidden; margin-top: 5px; }
    .boss-bar-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff4757, #ff6b81); transition: width 0.1s; }

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
    
    <div id="boss-hud">
        <div id="boss-name" style="color:#ff4757; font-weight:bold; font-size:16px;">특급 주령 - 화곤</div>
        <div class="boss-bar-outer"><div id="boss-hp-bar" class="boss-bar-hp"></div></div>
    </div>

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
                        <span class="skill-key" style="color:#ff4757;">X</span><span>영역전개</span>
                        <div id="cd-x" class="cooldown-overlay">0</div>
                    </div>
                </div>
            </div>
            
            <div class="hud-card" style="text-align:right;">
                <div style="font-size:16px; font-weight:bold; color:#a855f7;">🎮 WASD 이동 | E,R,T,X 마우스 타겟팅 스킬</div>
                <div id="kill-status" style="font-size:14px; color:#aaa; margin-top:6px;">제령한 주령: 0마리</div>
            </div>
        </div>
    </div>

    <div id="dialogue-box">
        <div id="dialogue-text">영역전개 「무량처공」</div>
    </div>

    <div id="class-select">
        <h1 style="color:#f3e8ff; font-size:48px; letter-spacing:2px; text-shadow:0 0 20px #a855f7;">JUJUTSU KAISEN</h1>
        <p style="color:#a1a1aa; margin-top:10px;">주술사 및 주왕을 선택하여 전장에 참여하십시오.</p>
        <div class="card-group">
            <div class="card" onclick="selectChar('Gojo')">
                <h2 style="color:#70a1ff;">👁️ 고죠 사토루</h2>
                <p>
                    • E: 술식 반전 「아카」 (마우스 위치 폭발)<br>
                    • R: 술식 순전 「아오」 (적 끌어당긴 후 폭발)<br>
                    • T: 무하한 결계 (주변 밀쳐내기)<br>
                    • <strong>X [궁극기]: 영역전개 「무량처공」 (전체 마비)</strong>
                </p>
            </div>
            <div class="card" onclick="selectChar('Sukuna')">
                <h2 style="color:#ff4757;">👹 양면 스쿠나</h2>
                <p>
                    • E: 참격 「해(解)」 (마우스 방향 연속 참격)<br>
                    • R: 참격 「팔(捌)」 (근접 대상 절단)<br>
                    • T: 신화 「푸가」 (마우스 위치 화염 폭발)<br>
                    • <strong>X [궁극기]: 영역전개 「복마어주자」</strong>
                </p>
            </div>
            <div class="card" onclick="selectChar('Megumi')">
                <h2 style="color:#2ecc71;">🐺 후시구로 메구미</h2>
                <p>
                    • E: 십종영법술 「누에」 (마우스 위치 뇌격)<br>
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
let mouseWorld = { x: 0, y: 0 };
let dialogueTimeout = null;

let player = {
    x: WORLD_WIDTH / 2, y: WORLD_HEIGHT / 2,
    speed: 5.8, hp: 250, maxHp: 250,
    ultEnergy: 0, maxUlt: 100,
    charType: 'Gojo', facing: 1
};

let cooldowns = { E: 0, R: 0, T: 0, X: 0 };
let maxCooldowns = {
    Gojo: { E: 3, R: 5, T: 6, X: 0 },
    Sukuna: { E: 2, R: 4, T: 6, X: 0 },
    Megumi: { E: 3, R: 5, T: 6, X: 0 }
};

let dialogues = {
    Gojo: { E: '술식 반전 「아카」', R: '술식 순전 「아오」', T: '무하한', X: '영역전개 「무량처공」' },
    Sukuna: { E: '참격 「해(解)」', R: '참격 「팔(捌)」', T: '「푸가(🔥)」', X: '영역전개 「복마어주자」' },
    Megumi: { E: '십종영법술 「누에」', R: '십종영법술 「옥견」', T: '그림자 속박', X: '팔지검 이계신장 강대마허라' }
};

let activeDomain = null; // 영역전개 효과 제어
let bossMonster = null;
let mahoraga = null;
let keys = {};
let projectiles = [];
let enemyProjectiles = [];
let slashes = []; // 참격 효과
let explosions = []; // 아카/아오 폭발 VFX
let enemies = [];

window.addEventListener('mousemove', e => {
    mouseWorld.x = e.clientX + camera.x;
    mouseWorld.y = e.clientY + camera.y;
});

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
        'Gojo': ['아카', '아오', '무하한', '무량처공'],
        'Sukuna': ['해(解)', '팔(捌)', '푸가', '복마어주자'],
        'Megumi': ['누에', '옥견', '그림자', '마허라']
    };
    
    document.getElementById('char-name').innerText = type === 'Gojo' ? '고죠 사토루' : (type === 'Sukuna' ? '양면 스쿠나' : '후시구로 메구미');
    document.getElementById('sk-e').innerText = skNames[type][0];
    document.getElementById('sk-r').innerText = skNames[type][1];
    document.getElementById('sk-t').innerText = skNames[type][2];

    for(let i=0; i<15; i++) spawnCurse(); // 몬스터 개체수 감소 (쾌적함 유지)
    gameLoop();
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
        triggerVibration(8);

        if(player.charType === 'Gojo') {
            // 아카: 마우스 지정 장소로 날아가 폭발
            projectiles.push({
                x: player.x, y: player.y, targetX: targetX, targetY: targetY,
                vx: Math.cos(ang)*16, vy: Math.sin(ang)*16,
                type: 'aka', damage: 150, radius: 12
            });
        } else if(player.charType === 'Sukuna') {
            // 해(解): 마우스 방향 참격
            for(let i=-1; i<=1; i++) {
                slashes.push({
                    x: player.x, y: player.y, ang: ang + i*0.15,
                    length: 120, life: 12, damage: 70
                });
            }
        } else {
            explosions.push({x: targetX, y: targetY, radius: 60, maxRadius: 60, color: '#f1c40f', life: 15, damage: 100});
        }
    } else if(key === 'R') {
        cooldowns.R = maxCooldowns[player.charType].R;
        triggerVibration(12);

        if(player.charType === 'Gojo') {
            // 아오: 마우스 위치로 발사 후 적을 끌어당기고 폭발
            projectiles.push({
                x: player.x, y: player.y, targetX: targetX, targetY: targetY,
                vx: Math.cos(ang)*18, vy: Math.sin(ang)*18,
                type: 'ao', damage: 180, radius: 14
            });
        } else if(player.charType === 'Sukuna') {
            // 팔(捌): 근접 최적화 즉시 강력 절단
            slashes.push({
                x: player.x + Math.cos(ang)*40, y: player.y + Math.sin(ang)*40,
                ang: ang, length: 180, life: 15, damage: 280
            });
        } else {
            projectiles.push({x: player.x, y: player.y, vx: Math.cos(ang)*14, vy: Math.sin(ang)*14, type:'normal', damage: 90, radius: 10, color: '#2ecc71'});
        }
    } else if(key === 'T') {
        cooldowns.T = maxCooldowns[player.charType].T;
        triggerVibration(10);

        if(player.charType === 'Gojo') {
            enemies.forEach(e => {
                if(Math.hypot(e.x - player.x, e.y - player.y) < 260) {
                    let pushAng = Math.atan2(e.y - player.y, e.x - player.x);
                    e.x += Math.cos(pushAng)*200; e.y += Math.sin(pushAng)*200; e.hp -= 50;
                }
            });
        } else if(player.charType === 'Sukuna') {
            // 푸가(🔥): 지정 위치 화염 폭발
            explosions.push({x: targetX, y: targetY, radius: 110, maxRadius: 110, color: '#e67e22', life: 25, damage: 220});
        } else {
            enemies.forEach(e => { if(Math.hypot(e.x - player.x, e.y - player.y) < 300) e.speed = 0.5; });
        }
    } else if(key === 'X') {
        player.ultEnergy = 0;
        triggerVibration(25);

        if(player.charType === 'Gojo') {
            activeDomain = { type: 'Gojo', timer: 200 };
        } else if(player.charType === 'Sukuna') {
            activeDomain = { type: 'Sukuna', timer: 180 };
        } else {
            mahoraga = { x: player.x, y: player.y - 50, life: 600 };
        }
    }
}

function spawnCurse() {
    let x = Math.random() * WORLD_WIDTH;
    let y = Math.random() * WORLD_HEIGHT;
    if(Math.hypot(x - player.x, y - player.y) < 400) return;

    enemies.push({
        x: x, y: y, radius: 16,
        hp: 100, maxHp: 100, speed: 2.2, isBoss: false
    });
}

function spawnBoss() {
    if(bossMonster) return;
    bossMonster = {
        x: player.x + 400, y: player.y, radius: 45,
        hp: 2500, maxHp: 2500, speed: 1.4, isBoss: true, attackCd: 0
    };
    enemies.push(bossMonster);
    document.getElementById('boss-hud').style.display = 'block';
}

function triggerGameOver() {
    isGameOver = true;
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

    // 필드 몬스터 개체수 제어 (최대 18마리로 적절히 유지)
    if(enemies.filter(e => !e.isBoss).length < 18) spawnCurse();
    if(killCount >= 10 && !bossMonster) spawnBoss();

    // 영역전개 처리
    if(activeDomain) {
        activeDomain.timer--;
        if(activeDomain.type === 'Gojo') {
            enemies.forEach(e => { e.speed = 0; e.hp -= 2; }); // 무량처공 마비 + 데미지
        } else if(activeDomain.type === 'Sukuna') {
            if(activeDomain.timer % 5 === 0) {
                slashes.push({
                    x: player.x + (Math.random()-0.5)*400, y: player.y + (Math.random()-0.5)*400,
                    ang: Math.random()*Math.PI*2, length: 140, life: 8, damage: 45
                });
            }
        }
        if(activeDomain.timer <= 0) activeDomain = null;
    }

    // 마하라도 보스 타겟팅 지원
    if(mahoraga) {
        mahoraga.life--;
        let target = bossMonster || enemies[0];
        if(target) {
            let ang = Math.atan2(target.y - mahoraga.y, target.x - mahoraga.x);
            mahoraga.x += Math.cos(ang) * 4.5; mahoraga.y += Math.sin(ang) * 4.5;
            if(Math.hypot(target.x - mahoraga.x, target.y - mahoraga.y) < 60) target.hp -= 20;
        }
        if(mahoraga.life <= 0) mahoraga = null;
    }

    // 투사체 (아카 / 아오 포함)
    projectiles.forEach((p, pi) => {
        p.x += p.vx; p.y += p.vy;
        let distToTarget = Math.hypot(p.targetX - p.x, p.targetY - p.y);

        if(p.type === 'aka' && distToTarget < 20) {
            explosions.push({x: p.x, y: p.y, radius: 90, maxRadius: 90, color: '#ff4757', life: 18, damage: p.damage});
            projectiles.splice(pi, 1);
        } else if(p.type === 'ao' && distToTarget < 20) {
            enemies.forEach(e => {
                if(Math.hypot(e.x - p.x, e.y - p.y) < 250) {
                    e.x = p.x; e.y = p.y; // 중앙 흡입
                }
            });
            explosions.push({x: p.x, y: p.y, radius: 100, maxRadius: 100, color: '#3742fa', life: 20, damage: p.damage});
            projectiles.splice(pi, 1);
        }
    });

    // 폭발 효과 처리
    explosions.forEach((ex, exi) => {
        ex.life--;
        enemies.forEach(e => {
            if(Math.hypot(e.x - ex.x, e.y - ex.y) < ex.radius) e.hp -= ex.damage / 10;
        });
        if(ex.life <= 0) explosions.splice(exi, 1);
    });

    // 참격 처리
    slashes.forEach((s, si) => {
        s.life--;
        enemies.forEach(e => {
            if(Math.hypot(e.x - s.x, e.y - s.y) < s.length / 2) e.hp -= s.damage / 5;
        });
        if(s.life <= 0) slashes.splice(si, 1);
    });

    // 적 투사체 처리
    enemyProjectiles.forEach((ep, epi) => {
        ep.x += ep.vx; ep.y += ep.vy;
        if(Math.hypot(player.x - ep.x, player.y - ep.y) < ep.radius + 10) {
            player.hp -= ep.damage; enemyProjectiles.splice(epi, 1);
        }
    });

    // 주령 및 보스 AI
    enemies.forEach((e, ei) => {
        if(!activeDomain || activeDomain.type !== 'Gojo') {
            e.speed = e.isBoss ? 1.4 : 2.2;
        }
        let ang = Math.atan2(player.y - e.y, player.x - e.x);
        let dist = Math.hypot(player.x - e.x, player.y - e.y);

        e.x += Math.cos(ang) * e.speed;
        e.y += Math.sin(ang) * e.speed;

        // 보스 공격 패턴 (원형 탄막)
        if(e.isBoss) {
            e.attackCd++;
            if(e.attackCd > 90) {
                for(let a=0; a<Math.PI*2; a+=Math.PI/4) {
                    enemyProjectiles.push({x: e.x, y: e.y, vx: Math.cos(a)*5, vy: Math.sin(a)*5, damage: 20, radius: 8});
                }
                e.attackCd = 0;
            }
            document.getElementById('boss-hp-bar').style.width = Math.max(0, (e.hp / e.maxHp * 100)) + '%';
        }

        if(dist < e.radius + 12) player.hp -= e.isBoss ? 1.5 : 0.4;

        if(e.hp <= 0) {
            if(e.isBoss) {
                bossMonster = null;
                document.getElementById('boss-hud').style.display = 'none';
            }
            killCount++;
            player.ultEnergy = Math.min(player.maxUlt, player.ultEnergy + 12);
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
        ctx.fillStyle = '#111'; ctx.fillRect(-8, -12, 16, 26);
        ctx.fillStyle = '#ffdfc4'; ctx.fillRect(-6, -18, 12, 6);
        ctx.fillStyle = '#fff'; ctx.fillRect(-8, -26, 16, 7);
    } else if(p.charType === 'Sukuna') {
        ctx.fillStyle = '#222'; ctx.fillRect(-8, -12, 16, 26);
        ctx.fillStyle = '#ffdfc4'; ctx.fillRect(-6, -18, 12, 6);
        ctx.fillStyle = '#ff4757'; ctx.fillRect(-7, -20, 14, 2); // 붉은 문신
        ctx.fillStyle = '#ff7675'; ctx.fillRect(-8, -26, 16, 7);
    } else {
        ctx.fillStyle = '#0a192f'; ctx.fillRect(-8, -12, 16, 26);
        ctx.fillStyle = '#ffdfc4'; ctx.fillRect(-6, -18, 12, 6);
        ctx.fillStyle = '#1e272e'; ctx.fillRect(-10, -28, 20, 10);
    }
    ctx.restore();
}

function draw() {
    ctx.save();
    if(screenShake > 0) ctx.translate((Math.random()-0.5)*screenShake, (Math.random()-0.5)*screenShake);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.translate(-camera.x, -camera.y);

    // 영역전개 배경 연출
    if(activeDomain) {
        ctx.fillStyle = activeDomain.type === 'Gojo' ? 'rgba(10, 10, 35, 0.6)' : 'rgba(40, 5, 5, 0.6)';
        ctx.fillRect(camera.x, camera.y, canvas.width, canvas.height);
    }

    // Grid
    ctx.strokeStyle = 'rgba(168, 85, 247, 0.06)'; ctx.lineWidth = 1;
    for(let x=0; x<WORLD_WIDTH; x+=100) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,WORLD_HEIGHT); ctx.stroke(); }
    for(let y=0; y<WORLD_HEIGHT; y+=100) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(WORLD_WIDTH,y); ctx.stroke(); }

    // 몬스터 및 보스
    enemies.forEach(e => {
        ctx.fillStyle = e.isBoss ? '#ff4757' : '#57606f';
        ctx.beginPath(); ctx.arc(e.x, e.y, e.radius, 0, Math.PI*2); ctx.fill();
        if(e.isBoss) {
            ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 3; ctx.stroke();
        }
    });

    // 참격 연출 (스쿠나)
    slashes.forEach(s => {
        ctx.strokeStyle = '#ff4757'; ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(s.x - Math.cos(s.ang)*s.length/2, s.y - Math.sin(s.ang)*s.length/2);
        ctx.lineTo(s.x + Math.cos(s.ang)*s.length/2, s.y + Math.sin(s.ang)*s.length/2);
        ctx.stroke();
    });

    // 폭발 VFX
    explosions.forEach(ex => {
        ctx.fillStyle = ex.color;
        ctx.beginPath(); ctx.arc(ex.x, ex.y, ex.radius, 0, Math.PI*2); ctx.fill();
    });

    // 투사체
    projectiles.forEach(p => {
        ctx.fillStyle = p.type === 'aka' ? '#ff4757' : '#3742fa';
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
    });

    enemyProjectiles.forEach(ep => {
        ctx.fillStyle = '#ff6b81';
        ctx.beginPath(); ctx.arc(ep.x, ep.y, ep.radius, 0, Math.PI*2); ctx.fill();
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

components.html(game_html, height=1000)
