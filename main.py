<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2026 KBO 3D Real Hitting Baseball</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome CDN -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
    <!-- Three.js CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

    <style>
        body {
            font-family: 'Noto Sans KR', sans-serif;
            background-color: #0b0f19;
            color: #ffffff;
            overflow: hidden;
            user-select: none;
        }
        .font-title {
            font-family: 'Black Han Sans', sans-serif;
        }
        #game-canvas {
            width: 100vw;
            height: 100vh;
            display: block;
        }
        .glass-panel {
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        .team-card {
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .team-card:hover {
            transform: translateY(-6px) scale(1.02);
            box-shadow: 0 12px 25px -5px rgba(59, 130, 246, 0.5);
        }
        .pulse-hit {
            animation: pulse-border 1.5s infinite;
        }
        @keyframes pulse-border {
            0%, 100% { border-color: rgba(239, 68, 68, 0.8); box-shadow: 0 0 15px rgba(239, 68, 68, 0.5); }
            50% { border-color: rgba(245, 158, 11, 0.9); box-shadow: 0 0 25px rgba(245, 158, 11, 0.8); }
        }
        @keyframes popup-text {
            0% { transform: translate(-50%, -50%) scale(0.3); opacity: 0; }
            50% { transform: translate(-50%, -50%) scale(1.2); opacity: 1; }
            100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
        }
        .animate-popup {
            animation: popup-text 0.4s ease-out forwards;
        }
    </style>
</head>
<body class="relative min-h-screen">

    <!-- TEAM SELECTION SCREEN -->
    <div id="selection-screen" class="fixed inset-0 z-50 flex flex-col items-center justify-center p-4 bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 overflow-y-auto">
        <div class="text-center mb-6">
            <span class="inline-block px-4 py-1.5 bg-blue-600/30 text-blue-400 font-bold rounded-full text-sm border border-blue-500/40 mb-2 tracking-wider">
                2026 OFFICIAL KBO ROSTER
            </span>
            <h1 class="font-title text-4xl md:text-6xl text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-yellow-200 to-amber-500 drop-shadow-md">
                KBO 3D 리얼 타격 야구
            </h1>
            <p class="text-slate-300 text-sm md:text-base mt-2">응원하는 KBO 구단을 선택하고 직접 타석에 들어서서 홈런을 날려보세요!</p>
        </div>

        <!-- Team Grid -->
        <div id="team-grid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4 max-w-5xl w-full px-2">
            <!-- Dynamically populated -->
        </div>

        <div class="mt-8 text-center text-xs text-slate-400">
            <p><i class="fa-solid fa-gamepad mr-1 text-amber-400"></i> 조작법: 투구가 들어올 때 <span class="bg-slate-800 text-amber-300 px-2 py-0.5 rounded border border-slate-700 font-mono">SPACE BAR</span> 또는 <span class="bg-slate-800 text-amber-300 px-2 py-0.5 rounded border border-slate-700">마우스 클릭 / 스크린 터치</span>로 타격</p>
        </div>
    </div>

    <!-- MAIN GAME CANVAS & OVERLAY -->
    <div id="game-wrapper" class="relative hidden w-full h-screen">
        <canvas id="game-canvas"></canvas>

        <!-- TOP HUD: Scoreboard & Inning -->
        <div class="absolute top-4 left-4 right-4 z-20 flex flex-col sm:flex-row justify-between items-center gap-3 pointer-events-none">
            <!-- Scoreboard -->
            <div class="glass-panel rounded-2xl px-5 py-3 flex items-center gap-6 shadow-2xl pointer-events-auto">
                <div class="flex items-center gap-3">
                    <div id="hud-team-logo" class="w-10 h-10 rounded-xl flex items-center justify-center font-title text-xl text-white shadow-inner">
                        KIA
                    </div>
                    <div>
                        <div id="hud-team-name" class="font-bold text-base text-white">KIA 타이거즈</div>
                        <div class="text-xs text-slate-400 flex items-center gap-2">
                            <span id="hud-inning" class="text-amber-400 font-bold">1회초</span>
                            <span>•</span>
                            <span>공격</span>
                        </div>
                    </div>
                </div>

                <div class="h-8 w-px bg-slate-700"></div>

                <div class="text-center">
                    <div class="text-xs text-slate-400">SCORE</div>
                    <div id="hud-score" class="font-title text-2xl text-amber-400 tracking-wider">0 - 0</div>
                </div>

                <div class="h-8 w-px bg-slate-700"></div>

                <!-- BSO Counter -->
                <div class="flex flex-col gap-1 text-xs font-bold">
                    <div class="flex items-center gap-1.5">
                        <span class="text-slate-400 w-3">B</span>
                        <div class="flex gap-1" id="ball-indicators">
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-700"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-700"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-700"></span>
                        </div>
                    </div>
                    <div class="flex items-center gap-1.5">
                        <span class="text-slate-400 w-3">S</span>
                        <div class="flex gap-1" id="strike-indicators">
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-700"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-700"></span>
                        </div>
                    </div>
                    <div class="flex items-center gap-1.5">
                        <span class="text-slate-400 w-3">O</span>
                        <div class="flex gap-1" id="out-indicators">
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-700"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-700"></span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Pitcher Info & Game Status -->
            <div class="glass-panel rounded-2xl px-5 py-3 flex items-center gap-4 text-right shadow-2xl pointer-events-auto">
                <div>
                    <div class="text-xs text-slate-400">상대 선발 투수</div>
                    <div id="hud-pitcher" class="font-bold text-sm text-slate-200">외국인 에이스 (RHP)</div>
                    <div id="hud-pitch-type" class="text-xs text-emerald-400 font-semibold mt-0.5">직구 준비 중...</div>
                </div>
                <div class="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-amber-400">
                    <i class="fa-solid fa-baseball text-lg"></i>
                </div>
            </div>
        </div>

        <!-- BOTTOM HUD: Active Batter Card & Hitting Button -->
        <div class="absolute bottom-4 left-4 right-4 z-20 flex flex-col md:flex-row justify-between items-end gap-4 pointer-events-none">
            <!-- Current Batter Info -->
            <div class="glass-panel rounded-2xl p-4 flex items-center gap-4 shadow-2xl pointer-events-auto max-w-md w-full">
                <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-slate-800 to-slate-700 flex items-center justify-center font-title text-2xl text-amber-400 border border-slate-600 shadow-md">
                    <span id="batter-number">38</span>
                </div>
                <div class="flex-grow">
                    <div class="flex items-center justify-between">
                        <span id="batter-order" class="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded font-bold border border-amber-500/30">3번 타자</span>
                        <span id="batter-pos" class="text-xs text-slate-400">3루수</span>
                    </div>
                    <div id="batter-name" class="font-title text-xl text-white mt-0.5">김도영</div>
                    <div class="flex gap-3 text-xs text-slate-300 mt-1">
                        <span>타율: <strong id="batter-avg" class="text-amber-300">.347</strong></span>
                        <span>홈런: <strong id="batter-hr" class="text-amber-300">38개</strong></span>
                        <span>OPS: <strong id="batter-ops" class="text-amber-300">1.060</strong></span>
                    </div>
                </div>
            </div>

            <!-- Swing / Pitch Controls -->
            <div class="flex items-center gap-3 pointer-events-auto w-full md:w-auto justify-center">
                <button id="btn-change-camera" class="glass-panel hover:bg-slate-800 text-slate-200 px-4 py-3 rounded-2xl font-bold text-sm flex items-center gap-2 transition active:scale-95 shadow-lg">
                    <i class="fa-solid fa-camera"></i> 시점 변경
                </button>
                <button id="btn-pitch" class="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-title text-lg px-6 py-3 rounded-2xl shadow-xl transition active:scale-95 flex items-center gap-2 border border-emerald-400/30">
                    <i class="fa-solid fa-play"></i> 투구 시작
                </button>
                <button id="btn-swing" class="pulse-hit bg-gradient-to-r from-red-600 via-amber-600 to-red-600 hover:from-red-500 hover:to-amber-500 text-white font-title text-xl px-10 py-3 rounded-2xl shadow-2xl transition active:scale-95 flex items-center gap-2 border border-amber-300/50">
                    <i class="fa-solid fa-baseball-bat-ball"></i> SWING! (Space)
                </button>
            </div>
        </div>

        <!-- ACTION RESULT ANNOUNCEMENT POPUP -->
        <div id="action-popup" class="hidden absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 pointer-events-none text-center">
            <div id="action-text" class="font-title text-5xl md:text-7xl text-amber-300 drop-shadow-[0_10px_10px_rgba(0,0,0,0.8)] stroke-black tracking-wider animate-popup">
                HOME RUN!
            </div>
            <div id="action-subtext" class="text-xl md:text-2xl text-white font-bold mt-2 drop-shadow-md">
                비거리 125m • 대형 홈런!
            </div>
        </div>
    </div>

    <!-- GAME LOGIC & THREE.JS ENGINE -->
    <script>
        // KBO 10 TEAM DATA & REAL ACTIVE LINEUPS (2025/2026 Key Rosters)
        const KBO_TEAMS = [
            {
                id: 'KIA',
                name: 'KIA 타이거즈',
                color: '#EA0029',
                secondaryColor: '#06141F',
                logoText: 'KIA',
                pitchers: ['네일', '양현종', '윤영철', '정해영'],
                lineup: [
                    { order: 1, name: '박찬호', pos: '유격수', number: 1, avg: '.307', hr: 5, ops: '.770' },
                    { order: 2, name: '소크라테스', pos: '좌익수', number: 30, avg: '.310', hr: 26, ops: '.880' },
                    { order: 3, name: '김도영', pos: '3루수', number: 38, avg: '.347', hr: 38, ops: '1.060' },
                    { order: 4, name: '최형우', pos: '지명타자', number: 34, avg: '.280', hr: 22, ops: '.860' },
                    { order: 5, name: '나성범', pos: '우익수', number: 47, avg: '.290', hr: 21, ops: '.850' },
                    { order: 6, name: '김선빈', pos: '2루수', number: 3, avg: '.320', hr: 9, ops: '.810' },
                    { order: 7, name: '이우성', pos: '1루수', number: 25, avg: '.288', hr: 9, ops: '.775' },
                    { order: 8, name: '김태군', pos: '포수', number: 42, avg: '.260', hr: 7, ops: '.690' },
                    { order: 9, name: '최원준', pos: '중견수', number: 2, avg: '.292', hr: 9, ops: '.760' }
                ]
            },
            {
                id: 'SAMSUNG',
                name: '삼성 라이온즈',
                color: '#0066B3',
                secondaryColor: '#C0C0C0',
                logoText: '삼성',
                pitchers: ['원태인', '레예스', '최채흥', '김재윤'],
                lineup: [
                    { order: 1, name: '김지찬', pos: '중견수', number: 58, avg: '.316', hr: 3, ops: '.802' },
                    { order: 2, name: '이재현', pos: '유격수', number: 7, avg: '.260', hr: 14, ops: '.770' },
                    { order: 3, name: '구자욱', pos: '좌익수', number: 65, avg: '.343', hr: 33, ops: '1.044' },
                    { order: 4, name: '디아즈', pos: '1루수', number: 44, avg: '.282', hr: 25, ops: '.890' },
                    { order: 5, name: '강민호', pos: '포수', number: 47, avg: '.303', hr: 19, ops: '.861' },
                    { order: 6, name: '김영웅', pos: '3루수', number: 5, avg: '.252', hr: 28, ops: '.806' },
                    { order: 7, name: '박병호', pos: '지명타자', number: 59, avg: '.245', hr: 23, ops: '.790' },
                    { order: 8, name: '윤정빈', pos: '우익수', number: 31, avg: '.286', hr: 7, ops: '.780' },
                    { order: 9, name: '류지혁', pos: '2루수', number: 16, avg: '.258', hr: 3, ops: '.680' }
                ]
            },
            {
                id: 'LG',
                name: 'LG 트윈스',
                color: '#C3002F',
                secondaryColor: '#000000',
                logoText: 'LG',
                pitchers: ['임찬규', '최원태', '손주영', '유영찬'],
                lineup: [
                    { order: 1, name: '홍창기', pos: '우익수', number: 51, avg: '.336', hr: 5, ops: '.857' },
                    { order: 2, name: '신민재', pos: '2루수', number: 4, avg: '.297', hr: 1, ops: '.750' },
                    { order: 3, name: '오스틴', pos: '1루수', number: 23, avg: '.319', hr: 32, ops: '.957' },
                    { order: 4, name: '문보경', pos: '3루수', number: 35, avg: '.301', hr: 22, ops: '.870' },
                    { order: 5, name: '김현수', pos: '지명타자', number: 22, avg: '.294', hr: 8, ops: '.780' },
                    { order: 6, name: '오지환', pos: '유격수', number: 10, avg: '.254', hr: 10, ops: '.750' },
                    { order: 7, name: '박동원', pos: '포수', number: 27, avg: '.272', hr: 20, ops: '.810' },
                    { order: 8, name: '문성주', pos: '좌익수', number: 8, avg: '.315', hr: 2, ops: '.790' },
                    { order: 9, name: '박해민', pos: '중견수', number: 17, avg: '.263', hr: 6, ops: '.700' }
                ]
            },
            {
                id: 'DOOSAN',
                name: '두산 베어스',
                color: '#131230',
                secondaryColor: '#ED1C24',
                logoText: '두산',
                pitchers: ['곽빈', '발라조빅', '최승용', '정철원'],
                lineup: [
                    { order: 1, name: '정수빈', pos: '중견수', number: 31, avg: '.284', hr: 4, ops: '.760' },
                    { order: 2, name: '허경민', pos: '3루수', number: 13, avg: '.309', hr: 7, ops: '.810' },
                    { order: 3, name: '양의지', pos: '포수', number: 25, avg: '.314', hr: 17, ops: '.890' },
                    { order: 4, name: '김재환', pos: '지명타자', number: 32, avg: '.283', hr: 29, ops: '.880' },
                    { order: 5, name: '양석환', pos: '1루수', number: 53, avg: '.246', hr: 34, ops: '.815' },
                    { order: 6, name: '강승호', pos: '2루수', number: 23, avg: '.280', hr: 18, ops: '.800' },
                    { order: 7, name: '제러디', pos: '좌익수', number: 33, avg: '.325', hr: 10, ops: '.930' },
                    { order: 8, name: '전민재', pos: '유격수', number: 14, avg: '.272', hr: 2, ops: '.690' },
                    { order: 9, name: '조수행', pos: '우익수', number: 51, avg: '.265', hr: 0, ops: '.660' }
                ]
            },
            {
                id: 'KT',
                name: 'KT 위즈',
                color: '#000000',
                secondaryColor: '#EC1C24',
                logoText: 'KT',
                pitchers: ['고영표', '엄상백', '쿠에바스', '박영현'],
                lineup: [
                    { order: 1, name: '멜 로하스', pos: '좌익수', number: 3, avg: '.329', hr: 32, ops: '.980' },
                    { order: 2, name: '강백호', pos: '지명타자', number: 50, avg: '.289', hr: 26, ops: '.840' },
                    { order: 3, name: '장성우', pos: '포수', number: 22, avg: '.275', hr: 19, ops: '.810' },
                    { order: 4, name: '문상철', pos: '1루수', number: 24, avg: '.256', hr: 17, ops: '.770' },
                    { order: 5, name: '황재균', pos: '3루수', number: 10, avg: '.260', hr: 13, ops: '.740' },
                    { order: 6, name: '김상수', pos: '유격수', number: 7, avg: '.270', hr: 4, ops: '.710' },
                    { order: 7, name: '배정대', pos: '중견수', number: 27, avg: '.275', hr: 8, ops: '.750' },
                    { order: 8, name: '오윤석', pos: '2루수', number: 6, avg: '.250', hr: 6, ops: '.700' },
                    { order: 9, name: '정준영', pos: '우익수', number: 51, avg: '.262', hr: 1, ops: '.650' }
                ]
            },
            {
                id: 'SSG',
                name: 'SSG 랜더스',
                color: '#CE0E2D',
                secondaryColor: '#FFB81C',
                logoText: 'SSG',
                pitchers: ['김광현', '앤더슨', '엘리아스', '조병현'],
                lineup: [
                    { order: 1, name: '최지훈', pos: '중견수', number: 54, avg: '.272', hr: 11, ops: '.740' },
                    { order: 2, name: '박성한', pos: '유격수', number: 2, avg: '.301', hr: 10, ops: '.790' },
                    { order: 3, name: '최정', pos: '3루수', number: 14, avg: '.291', hr: 37, ops: '.978' },
                    { order: 4, name: '에레디아', pos: '좌익수', number: 27, avg: '.360', hr: 21, ops: '.960' },
                    { order: 5, name: '한유섬', pos: '지명타자', number: 35, avg: '.265', hr: 24, ops: '.830' },
                    { order: 6, name: '이지영', pos: '포수', number: 59, avg: '.280', hr: 5, ops: '.710' },
                    { order: 7, name: '고명준', pos: '1루수', number: 18, avg: '.270', hr: 11, ops: '.730' },
                    { order: 8, name: '하재훈', pos: '우익수', number: 13, avg: '.250', hr: 8, ops: '.700' },
                    { order: 9, name: '안상현', pos: '2루수', number: 6, avg: '.235', hr: 2, ops: '.620' }
                ]
            },
            {
                id: 'LOTTE',
                name: '롯데 자이언츠',
                color: '#041E42',
                secondaryColor: '#D11241',
                logoText: '롯데',
                pitchers: ['박세웅', '반즈', '윌커슨', '김원중'],
                lineup: [
                    { order: 1, name: '황성빈', pos: '중견수', number: 0, avg: '.320', hr: 5, ops: '.800' },
                    { order: 2, name: '윤동희', pos: '우익수', number: 91, avg: '.293', hr: 14, ops: '.820' },
                    { order: 3, name: '레이예스', pos: '좌익수', number: 29, avg: '.352', hr: 15, ops: '.905' },
                    { order: 4, name: '전준우', pos: '지명타자', number: 8, avg: '.290', hr: 17, ops: '.830' },
                    { order: 5, name: '손호영', pos: '3루수', number: 33, avg: '.317', hr: 18, ops: '.890' },
                    { order: 6, name: '고승민', pos: '2루수', number: 4, avg: '.308', hr: 14, ops: '.840' },
                    { order: 7, name: '나승엽', pos: '1루수', number: 51, avg: '.312', hr: 7, ops: '.870' },
                    { order: 8, name: '유강남', pos: '포수', number: 27, avg: '.240', hr: 6, ops: '.680' },
                    { order: 9, name: '박승욱', pos: '유격수', number: 5, avg: '.262', hr: 7, ops: '.720' }
                ]
            },
            {
                id: 'HANWHA',
                name: '한화 이글스',
                color: '#FF6600',
                secondaryColor: '#000000',
                logoText: '한화',
                pitchers: ['류현진', '문동주', '와이스', '주현상'],
                lineup: [
                    { order: 1, name: '황영묵', pos: '2루수', number: 5, avg: '.301', hr: 3, ops: '.740' },
                    { order: 2, name: '페라자', pos: '좌익수', number: 30, avg: '.275', hr: 24, ops: '.850' },
                    { order: 3, name: '노시환', pos: '3루수', number: 8, avg: '.272', hr: 24, ops: '.820' },
                    { order: 4, name: '채은성', pos: '1루수', number: 22, avg: '.270', hr: 20, ops: '.800' },
                    { order: 5, name: '안치홍', pos: '지명타자', number: 25, avg: '.285', hr: 13, ops: '.780' },
                    { order: 6, name: '김태연', pos: '우익수', number: 26, avg: '.291', hr: 12, ops: '.810' },
                    { order: 7, name: '최재훈', pos: '포수', number: 13, avg: '.268', hr: 5, ops: '.730' },
                    { order: 8, name: '하주석', pos: '유격수', number: 16, avg: '.280', hr: 2, ops: '.710' },
                    { order: 9, name: '장진혁', pos: '중견수', number: 38, avg: '.263', hr: 9, ops: '.720' }
                ]
            },
            {
                id: 'NC',
                name: 'NC 다이노스',
                color: '#112C55',
                secondaryColor: '#A1B2C6',
                logoText: 'NC',
                pitchers: ['하트', '신민혁', '김시훈', 'R.유영찬'],
                lineup: [
                    { order: 1, name: '박민우', pos: '2루수', number: 2, avg: '.328', hr: 7, ops: '.860' },
                    { order: 2, name: '권희동', pos: '좌익수', number: 36, avg: '.285', hr: 11, ops: '.810' },
                    { order: 3, name: '박건우', pos: '우익수', number: 37, avg: '.344', hr: 13, ops: '.920' },
                    { order: 4, name: '데이비슨', pos: '1루수', number: 24, avg: '.289', hr: 46, ops: '.970' },
                    { order: 5, name: '손아섭', pos: '지명타자', number: 31, avg: '.291', hr: 7, ops: '.760' },
                    { order: 6, name: '서호철', pos: '3루수', number: 5, avg: '.282', hr: 10, ops: '.750' },
                    { order: 7, name: '김형준', pos: '포수', number: 25, avg: '.220', hr: 17, ops: '.710' },
                    { order: 8, name: '김주원', pos: '유격수', number: 7, avg: '.252', hr: 9, ops: '.730' },
                    { order: 9, name: '최정원', pos: '중견수', number: 64, avg: '.270', hr: 1, ops: '.680' }
                ]
            },
            {
                id: 'KIWOOM',
                name: '키움 히어로즈',
                color: '#820024',
                secondaryColor: '#B2B2B2',
                logoText: '키움',
                pitchers: ['후라도', '헤이수스', '하영민', '주승우'],
                lineup: [
                    { order: 1, name: '이주형', pos: '중견수', number: 2, avg: '.266', hr: 13, ops: '.750' },
                    { order: 2, name: '송성문', pos: '3루수', number: 24, avg: '.340', hr: 19, ops: '.927' },
                    { order: 3, name: '김혜성', pos: '2루수', number: 3, avg: '.326', hr: 11, ops: '.840' },
                    { order: 4, name: '최주환', pos: '1루수', number: 53, avg: '.255', hr: 13, ops: '.740' },
                    { order: 5, name: '김건희', pos: '지명타자', number: 60, avg: '.270', hr: 9, ops: '.730' },
                    { order: 6, name: '변상권', pos: '좌익수', number: 50, avg: '.260', hr: 5, ops: '.690' },
                    { order: 7, name: '김태진', pos: '유격수', number: 27, avg: '.275', hr: 1, ops: '.670' },
                    { order: 8, name: '김동헌', pos: '포수', number: 12, avg: '.240', hr: 3, ops: '.640' },
                    { order: 9, name: '원성준', pos: '우익수', number: 10, avg: '.250', hr: 2, ops: '.650' }
                ]
            }
        ];

        // GAME STATE
        let selectedTeam = null;
        let currentBatterIdx = 0;
        let score = { user: 0, cpu: 0 };
        let count = { ball: 0, strike: 0, out: 0 };
        let inning = 1;

        // THREE.JS SYSTEM VARIABLES
        let scene, camera, renderer;
        let pitcherMesh, batterMesh, batMesh, ballMesh, stadiumGroup;
        let cameraMode = 0; // 0: Catcher View, 1: Broadcast View
        
        let pitchState = 'IDLE'; // IDLE, PITCHING, HIT, RESULT
        let ballVel = new THREE.Vector3();
        let pitchType = 'FASTBALL';
        let pitchStartTime = 0;
        let swingStartTime = 0;
        let isSwung = false;

        // Initialize Web Audio API for sound effects
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        let audioCtx = null;

        function playSound(type) {
            try {
                if (!audioCtx) audioCtx = new AudioContext();
                if (audioCtx.state === 'suspended') audioCtx.resume();

                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.connect(gain);
                gain.connect(audioCtx.destination);

                const now = audioCtx.currentTime;
                if (type === 'HIT') {
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(600, now);
                    osc.frequency.exponentialRampToValueAtTime(150, now + 0.15);
                    gain.gain.setValueAtTime(1.0, now);
                    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
                    osc.start(now);
                    osc.stop(now + 0.2);
                } else if (type === 'HOMERUN') {
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(300, now);
                    osc.frequency.linearRampToValueAtTime(800, now + 0.5);
                    gain.gain.setValueAtTime(0.8, now);
                    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.6);
                    osc.start(now);
                    osc.stop(now + 0.6);
                } else if (type === 'CATCH') {
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(180, now);
                    gain.gain.setValueAtTime(0.5, now);
                    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
                    osc.start(now);
                    osc.stop(now + 0.08);
                }
            } catch (e) { console.log('Audio context not allowed yet.'); }
        }

        // INIT DOM & SELECTION
        window.addEventListener('DOMContentLoaded', () => {
            renderTeamSelection();
            setupEventListeners();
        });

        function renderTeamSelection() {
            const grid = document.getElementById('team-grid');
            grid.innerHTML = KBO_TEAMS.map(team => `
                <div onclick="selectTeam('${team.id}')" class="team-card glass-panel rounded-2xl p-4 flex flex-col items-center cursor-pointer border-2 border-slate-700/60 hover:border-amber-400 group relative overflow-hidden">
                    <div class="w-16 h-16 rounded-2xl flex items-center justify-center font-title text-2xl text-white shadow-lg mb-3 transform group-hover:scale-110 transition" style="background: linear-gradient(135deg, ${team.color}, ${team.secondaryColor})">
                        ${team.logoText}
                    </div>
                    <div class="font-bold text-base text-white group-hover:text-amber-300 text-center">${team.name}</div>
                    <div class="text-xs text-slate-400 mt-1">대표타자: ${team.lineup[2].name}</div>
                    <div class="mt-3 text-xs bg-slate-800/80 text-amber-400 font-bold px-3 py-1 rounded-full border border-slate-700">선택하기</div>
                </div>
            `).join('');
        }

        function selectTeam(teamId) {
            selectedTeam = KBO_TEAMS.find(t => t.id === teamId);
            document.getElementById('selection-screen').classList.add('hidden');
            document.getElementById('game-wrapper').classList.remove('hidden');

            updateHUD();
            init3DScene();
            animate();
        }

        function updateHUD() {
            if (!selectedTeam) return;
            const batter = selectedTeam.lineup[currentBatterIdx];

            document.getElementById('hud-team-logo').innerText = selectedTeam.logoText;
            document.getElementById('hud-team-logo').style.background = `linear-gradient(135deg, ${selectedTeam.color}, ${selectedTeam.secondaryColor})`;
            document.getElementById('hud-team-name').innerText = selectedTeam.name;
            document.getElementById('hud-score').innerText = `${score.user} - ${score.cpu}`;

            document.getElementById('batter-number').innerText = batter.number;
            document.getElementById('batter-order').innerText = `${batter.order}번 타자`;
            document.getElementById('batter-pos').innerText = batter.pos;
            document.getElementById('batter-name').innerText = batter.name;
            document.getElementById('batter-avg').innerText = batter.avg;
            document.getElementById('batter-hr').innerText = `${batter.hr}개`;
            document.getElementById('batter-ops').innerText = batter.ops;

            updateBSO();
        }

        function updateBSO() {
            const ballContainer = document.getElementById('ball-indicators');
            const strikeContainer = document.getElementById('strike-indicators');
            const outContainer = document.getElementById('out-indicators');

            ballContainer.innerHTML = Array(3).fill(0).map((_, i) => 
                `<span class="w-2.5 h-2.5 rounded-full ${i < count.ball ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-slate-700'}"></span>`
            ).join('');

            strikeContainer.innerHTML = Array(2).fill(0).map((_, i) => 
                `<span class="w-2.5 h-2.5 rounded-full ${i < count.strike ? 'bg-amber-400 shadow-[0_0_8px_#f59e0b]' : 'bg-slate-700'}"></span>`
            ).join('');

            outContainer.innerHTML = Array(2).fill(0).map((_, i) => 
                `<span class="w-2.5 h-2.5 rounded-full ${i < count.out ? 'bg-red-500 shadow-[0_0_8px_#ef4444]' : 'bg-slate-700'}"></span>`
            ).join('');
        }

        // THREE.JS STADIUM & GAME OBJECT BUILDER
        function init3DScene() {
            const container = document.getElementById('game-wrapper');
            canvas = document.getElementById('game-canvas');

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0c1427);
            scene.fog = new THREE.FogExp2(0x0c1427, 0.003);

            camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
            setCameraPosition();

            renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;

            // Lights
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);

            const sunLight = new THREE.DirectionalLight(0xfffaed, 1.2);
            sunLight.position.set(30, 80, -20);
            sunLight.castShadow = true;
            sunLight.shadow.mapSize.width = 2048;
            sunLight.shadow.mapSize.height = 2048;
            scene.add(sunLight);

            // Stadium Lights (Stadium Floodlights)
            const floodPositions = [[-40, 35, 10], [40, 35, 10], [-50, 40, -60], [50, 40, -60]];
            floodPositions.forEach(pos => {
                const light = new THREE.PointLight(0xffffff, 0.8, 120);
                light.position.set(...pos);
                scene.add(light);
            });

            stadiumGroup = new THREE.Group();
            scene.add(stadiumGroup);

            buildStadium();
            createPitcherAndBatter();
            createBall();

            window.addEventListener('resize', onWindowResize);
        }

        function setCameraPosition() {
            if (cameraMode === 0) {
                // Catcher / Batter View
                camera.position.set(0, 2.2, 3.8);
                camera.lookAt(0, 1.2, -18.4);
            } else {
                // Broadcast Angle
                camera.position.set(12, 14, 18);
                camera.lookAt(0, 1, -8);
            }
        }

        function buildStadium() {
            // Field Dirt Diamond
            const dirtGeo = new THREE.PlaneGeometry(55, 55);
            const dirtMat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b, roughness: 0.9 });
            const dirt = new THREE.Mesh(dirtGeo, dirtMat);
            dirt.rotation.x = -Math.PI / 2;
            dirt.rotation.z = Math.PI / 4;
            dirt.position.set(0, 0, -18);
            dirt.receiveShadow = true;
            stadiumGroup.add(dirt);

            // Grass Outfield
            const grassGeo = new THREE.CircleGeometry(110, 64, 0, Math.PI);
            const grassMat = new THREE.MeshStandardMaterial({ color: 0x1e6b2c, roughness: 0.8 });
            const grass = new THREE.Mesh(grassGeo, grassMat);
            grass.rotation.x = -Math.PI / 2;
            grass.rotation.z = Math.PI / 4;
            grass.position.set(0, -0.05, -18);
            grass.receiveShadow = true;
            stadiumGroup.add(grass);

            // Infield Grass Diamond
            const innerGrassGeo = new THREE.PlaneGeometry(28, 28);
            const innerGrass = new THREE.Mesh(innerGrassGeo, grassMat);
            innerGrass.rotation.x = -Math.PI / 2;
            innerGrass.rotation.z = Math.PI / 4;
            innerGrass.position.set(0, 0.02, -18);
            stadiumGroup.add(innerGrass);

            // Bases (Home, 1B, 2B, 3B)
            const baseGeo = new THREE.BoxGeometry(0.5, 0.1, 0.5);
            const baseMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
            const basePositions = [
                [0, 0.05, 0],       // Home Plate
                [13, 0.05, -13],    // 1B
                [0, 0.05, -26],     // 2B
                [-13, 0.05, -13]    // 3B
            ];
            basePositions.forEach(pos => {
                const base = new THREE.Mesh(baseGeo, baseMat);
                base.position.set(...pos);
                stadiumGroup.add(base);
            });

            // Pitcher Mound
            const moundGeo = new THREE.CylinderGeometry(2.5, 3.2, 0.4, 32);
            const moundMat = new THREE.MeshStandardMaterial({ color: 0x7c4f24 });
            const mound = new THREE.Mesh(moundGeo, moundMat);
            mound.position.set(0, 0.15, -18.4);
            stadiumGroup.add(mound);

            // Outfield Fence Wall
            const wallGeo = new THREE.CylinderGeometry(100, 100, 6, 64, 1, true, Math.PI * 0.25, Math.PI * 0.5);
            const wallMat = new THREE.MeshStandardMaterial({ color: 0x0a2f52, side: THREE.DoubleSide });
            const wall = new THREE.Mesh(wallGeo, wallMat);
            wall.position.set(0, 3, -18);
            stadiumGroup.add(wall);

            // Outfield Distance Ads / Signs
            const signGeo = new THREE.PlaneGeometry(16, 4);
            const signMat = new THREE.MeshStandardMaterial({ color: 0x3b82f6 });
            const sign = new THREE.Mesh(signGeo, signMat);
            sign.position.set(0, 5, -117.5);
            stadiumGroup.add(sign);
        }

        function createPitcherAndBatter() {
            // Pitcher Model (Simple Stylized Mesh)
            const bodyGeo = new THREE.CylinderGeometry(0.35, 0.3, 1.6, 16);
            const bodyMat = new THREE.MeshStandardMaterial({ color: 0x1e293b });
            pitcherMesh = new THREE.Mesh(bodyGeo, bodyMat);
            pitcherMesh.position.set(0, 1.1, -18.4);
            pitcherMesh.castShadow = true;

            const headGeo = new THREE.SphereGeometry(0.25, 16, 16);
            const headMat = new THREE.MeshStandardMaterial({ color: 0xffdbac });
            const pHead = new THREE.Mesh(headGeo, headMat);
            pHead.position.set(0, 1.0, 0);
            pitcherMesh.add(pHead);

            scene.add(pitcherMesh);

            // Batter Model & Bat
            const batterColor = selectedTeam ? selectedTeam.color : 0xef4444;
            const bBodyMat = new THREE.MeshStandardMaterial({ color: batterColor });
            batterMesh = new THREE.Mesh(bodyGeo, bBodyMat);
            batterMesh.position.set(-0.8, 1.1, 0.2); // Right handed batter position
            batterMesh.castShadow = true;

            const bHead = new THREE.Mesh(headGeo, headMat);
            bHead.position.set(0, 1.0, 0);
            batterMesh.add(bHead);

            // Bat
            const batGeo = new THREE.CylinderGeometry(0.03, 0.07, 1.1, 16);
            const batMat = new THREE.MeshStandardMaterial({ color: 0xc8963e, roughness: 0.3 });
            batMesh = new THREE.Mesh(batGeo, batMat);
            batMesh.position.set(0.4, 0.5, 0.2);
            batMesh.rotation.z = -Math.PI / 4;
            batMesh.rotation.x = Math.PI / 6;
            batterMesh.add(batMesh);

            scene.add(batterMesh);
        }

        function createBall() {
            const ballGeo = new THREE.SphereGeometry(0.12, 32, 32);
            const ballMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
            ballMesh = new THREE.Mesh(ballGeo, ballMat);
            ballMesh.castShadow = true;
            ballMesh.position.set(0, 1.5, -18.4); // Start at pitcher hand
            scene.add(ballMesh);
        }

        // GAME MECHANICS & CONTROLS
        function setupEventListeners() {
            document.getElementById('btn-pitch').addEventListener('click', startPitch);
            document.getElementById('btn-swing').addEventListener('click', triggerSwing);
            document.getElementById('btn-change-camera').addEventListener('click', () => {
                cameraMode = (cameraMode === 0) ? 1 : 0;
                setCameraPosition();
            });

            window.addEventListener('keydown', (e) => {
                if (e.code === 'Space') {
                    e.preventDefault();
                    if (pitchState === 'IDLE') {
                        startPitch();
                    } else if (pitchState === 'PITCHING') {
                        triggerSwing();
                    }
                }
            });

            // Touch screen / mouse hit on canvas
            document.getElementById('game-canvas').addEventListener('pointerdown', () => {
                if (pitchState === 'IDLE') startPitch();
                else if (pitchState === 'PITCHING') triggerSwing();
            });
        }

        function startPitch() {
            if (pitchState !== 'IDLE') return;

            pitchState = 'PITCHING';
            isSwung = false;
            pitchStartTime = performance.now();

            // Random Pitch Type
            const pitchTypes = ['직구 (Fastball)', '슬라이더 (Slider)', '커브 (Curveball)', '체인지업 (Changeup)'];
            const pIdx = Math.floor(Math.random() * pitchTypes.length);
            const pitchName = pitchTypes[pIdx];

            const speedKmh = Math.floor(138 + Math.random() * 16);
            document.getElementById('hud-pitch-type').innerText = `${pitchName} • ${speedKmh} km/h`;

            // Initial Ball Position at Pitcher Release
            ballMesh.position.set(0, 1.6, -18.4);

            // Pitch Physics trajectory logic
            const durationSec = 180 / speedKmh; // Flight duration approx 0.8s - 1.2s
            ballVel.z = 18.4 / durationSec; 

            // Curve/Break offsets
            ballVel.x = (Math.random() - 0.5) * 0.8;
            if (pIdx === 1) ballVel.x = 1.2; // Slider breaks right
            if (pIdx === 2) ballVel.y = -0.8; // Curve breaks down

            // Windup Pitcher Animation
            pitcherMesh.position.y = 1.4;
            setTimeout(() => { pitcherMesh.position.y = 1.1; }, 200);
        }

        function triggerSwing() {
            if (pitchState !== 'PITCHING' || isSwung) return;

            isSwung = true;
            swingStartTime = performance.now();

            // Bat Swing Animation
            const duration = 250;
            const startTime = performance.now();

            function animateBat() {
                const elapsed = performance.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);

                // Bat Rotation Sweep
                batMesh.rotation.y = -Math.PI * 0.8 * progress;
                batMesh.rotation.z = -Math.PI / 4 + Math.PI * 0.5 * progress;

                if (progress < 1) {
                    requestAnimationFrame(animateBat);
                } else {
                    // Reset Bat
                    batMesh.rotation.set(Math.PI / 6, 0, -Math.PI / 4);
                }
            }
            animateBat();

            // Contact Timing Check (Distance to home plate z = 0)
            const ballZ = ballMesh.position.z;
            const timingDiff = Math.abs(ballZ - 0.0); // Perfect hit when ball z is close to 0

            if (timingDiff < 1.2) {
                // HIT!
                pitchState = 'HIT';
                playSound('HIT');

                // Determine Hit Quality based on timing & pitch position
                let hitQuality = 'SINGLE';
                if (timingDiff < 0.35) {
                    hitQuality = 'HOMERUN';
                } else if (timingDiff < 0.65) {
                    hitQuality = 'DOUBLE';
                } else if (timingDiff < 0.95) {
                    hitQuality = (Math.random() > 0.4) ? 'SINGLE' : 'FOUL';
                } else {
                    hitQuality = 'OUT';
                }

                executeHitTrajectory(hitQuality);
            }
        }

        function executeHitTrajectory(type) {
            const exitVel = (type === 'HOMERUN') ? 42 : (type === 'DOUBLE') ? 30 : 22;
            const launchAngle = (type === 'HOMERUN') ? 0.65 : (type === 'DOUBLE') ? 0.4 : 0.25;

            const spreadX = (Math.random() - 0.5) * 0.8;

            ballVel.x = Math.sin(spreadX) * exitVel;
            ballVel.y = Math.sin(launchAngle) * exitVel;
            ballVel.z = -Math.cos(launchAngle) * exitVel;

            let text = '안타!';
            let subtext = '1루타 성공!';

            if (type === 'HOMERUN') {
                text = 'HOME RUN!!';
                const dist = Math.floor(115 + Math.random() * 20);
                subtext = `대형 담장을 넘어갑니다! 비거리 ${dist}m`;
                score.user += 1;
                playSound('HOMERUN');
            } else if (type === 'DOUBLE') {
                text = '2루타!';
                subtext = '우중간을 가르는 통쾌한 장타!';
            } else if (type === 'FOUL') {
                text = '파울 Ball';
                subtext = '타구는 관중석으로 들어갑니다.';
                if (count.strike < 2) count.strike++;
            } else if (type === 'OUT') {
                text = '아웃 (OUT)';
                subtext = '야수 정면으로 향하는 타구입니다.';
                count.out++;
            }

            if (type === 'SINGLE' || type === 'DOUBLE') {
                // Advance score
                if (Math.random() > 0.5) score.user += 1;
            }

            showActionPopup(text, subtext);
            updateHUD();

            setTimeout(resetPitch, 3500);
        }

        function handleStrikeOrBall() {
            if (pitchState !== 'PITCHING') return;

            pitchState = 'RESULT';
            playSound('CATCH');

            // Ball Zone check
            const inZone = Math.abs(ballMesh.position.x) < 0.6 && Math.abs(ballMesh.position.y - 1.2) < 0.6;

            if (isSwung) {
                count.strike++;
                showActionPopup('헛스윙 삼진!', '타이밍을 빼앗겼습니다.');
            } else if (inZone) {
                count.strike++;
                showActionPopup('스트라이크!', '루킹 스트라이크 인정');
            } else {
                count.ball++;
                showActionPopup('볼 (BALL)', '선구안이 빛났습니다!');
            }

            if (count.strike >= 3) {
                count.out++;
                count.strike = 0;
                count.ball = 0;
                showActionPopup('삼진 아웃!', '다음 타자로 교체됩니다.');
                nextBatter();
            } else if (count.ball >= 4) {
                count.ball = 0;
                count.strike = 0;
                showActionPopup('볼넷 출루!', '1루로 출루합니다.');
                nextBatter();
            }

            if (count.out >= 3) {
                count.out = 0;
                count.strike = 0;
                count.ball = 0;
                inning++;
                showActionPopup('공수 교대!', '이닝이 종료되었습니다.');
            }

            updateHUD();
            setTimeout(resetPitch, 2200);
        }

        function nextBatter() {
            currentBatterIdx = (currentBatterIdx + 1) % selectedTeam.lineup.length;
            updateHUD();
        }

        function resetPitch() {
            pitchState = 'IDLE';
            ballMesh.position.set(0, 1.5, -18.4);
            document.getElementById('hud-pitch-type').innerText = '투구 준비 중...';
            document.getElementById('action-popup').classList.add('hidden');
        }

        function showActionPopup(mainText, subText) {
            const popup = document.getElementById('action-popup');
            document.getElementById('action-text').innerText = mainText;
            document.getElementById('action-subtext').innerText = subText;
            popup.classList.remove('hidden');
        }

        // MAIN THREE.JS ANIMATION LOOP
        function animate() {
            requestAnimationFrame(animate);

            const delta = 0.016; // approx 60fps frame delta

            if (pitchState === 'PITCHING') {
                ballMesh.position.z += ballVel.z * delta;
                ballMesh.position.x += ballVel.x * delta;
                ballMesh.position.y += ballVel.y * delta;
                ballMesh.rotation.x += 0.2;

                // Pass catcher threshold
                if (ballMesh.position.z >= 1.0) {
                    handleStrikeOrBall();
                }
            } else if (pitchState === 'HIT') {
                ballMesh.position.x += ballVel.x * delta;
                ballMesh.position.y += ballVel.y * delta;
                ballMesh.position.z += ballVel.z * delta;

                // Gravity on batted ball
                ballVel.y -= 9.8 * delta;

                ballMesh.rotation.x += 0.3;
                ballMesh.rotation.y += 0.3;

                // Bounce on field floor
                if (ballMesh.position.y <= 0.12) {
                    ballMesh.position.y = 0.12;
                    ballVel.y *= -0.5;
                    ballVel.x *= 0.7;
                    ballVel.z *= 0.7;
                }
            }

            renderer.render(scene, camera);
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }
    </script>
</body>
</html>
