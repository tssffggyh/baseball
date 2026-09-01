import math
import os
import random
import sys
import pygame

# Pygame 및 믹서 초기화
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ==========================================
# 1. 상수 및 설정 (CONSTANTS & CONFIG)
# ==========================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# 색상 정의
BLACK = (15, 15, 20)
WHITE = (240, 240, 240)
RED = (220, 50, 50)
GREEN = (50, 205, 50)
BLUE = (65, 105, 225)
YELLOW = (255, 215, 0)
PURPLE = (147, 112, 219)
CYAN = (0, 255, 255)
ORANGE = (255, 140, 0)
DARK_GRAY = (40, 40, 50)
LIGHT_GRAY = (180, 180, 200)
WALL_COLOR = (60, 60, 80)
FLOOR_COLOR = (25, 25, 35)

# 폰트 설정
FONT_LARGE = pygame.font.SysFont("malgungothic", 48, bold=True)
FONT_MEDIUM = pygame.font.SysFont("malgungothic", 28, bold=True)
FONT_SMALL = pygame.font.SysFont("malgungothic", 18)

# ==========================================
# 2. 사운드 제너레이터 (절차적 합성 음향)
# ==========================================
class SoundEffectGenerator:
    """외부 음악 파일 없이 수학적 파형으로 효과음을 생성합니다."""
    @staticmethod
    def generate_sound(freq=441, duration=0.1, wave_type='square'):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            if wave_type == 'square':
                val = 32767 if (math.sin(2 * math.pi * freq * t) > 0) else -32768
            elif wave_type == 'saw':
                val = int((2 * (t * freq - math.floor(0.5 + t * freq))) * 32767)
            else: # noise
                val = random.randint(-32768, 32767)
            
            # 감쇠(Fade Out) 적용
            attenuation = (1.0 - (i / n_samples))
            val = int(val * attenuation * 0.3)
            
            buf.extend(val.to_bytes(2, byteorder='little', signed=True))
            buf.extend(val.to_bytes(2, byteorder='little', signed=True)) # 스테레오
            
        return pygame.mixer.Sound(buffer=bytes(buf))

class SoundManager:
    def __init__(self):
        try:
            self.sounds = {
                'hit': SoundEffectGenerator.generate_sound(150, 0.08, 'saw'),
                'shoot': SoundEffectGenerator.generate_sound(600, 0.1, 'square'),
                'slash': SoundEffectGenerator.generate_sound(300, 0.05, 'noise'),
                'item': SoundEffectGenerator.generate_sound(880, 0.15, 'square'),
                'skill': SoundEffectGenerator.generate_sound(440, 0.25, 'saw')
            }
            self.enabled = True
        except Exception as e:
            print(f"사운드 생성 실패 (무음 모드로 실행): {e}")
            self.enabled = False

    def play(self, sound_name):
        if self.enabled and sound_name in self.sounds:
            self.sounds[sound_name].play()

SOUND_SYS = SoundManager()

# ==========================================
# 3. 파티클 및 비주얼 이펙트 시스템
# ==========================================
class Particle:
    def __init__(self, x, y, color, vel_x, vel_y, lifetime, size_start, size_end=0):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size_start = size_start
        self.size_end = size_end

    def update(self, dt):
        self.x += self.vel_x * dt * 60
        self.y += self.vel_y * dt * 60
        self.lifetime -= dt

    def draw(self, surface, camera):
        if self.lifetime <= 0:
            return
        progress = max(0, self.lifetime / self.max_lifetime)
        current_size = self.size_end + (self.size_start - self.size_end) * progress
        screen_pos = camera.apply_pos((self.x, self.y))
        pygame.draw.circle(surface, self.color, (int(screen_pos[0]), int(screen_pos[1])), int(current_size))

class ParticleManager:
    def __init__(self):
        self.particles = []

    def create_burst(self, x, y, color, count=10, speed=3):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            sp = random.uniform(0.5, speed)
            vx = math.cos(angle) * sp
            vy = math.sin(angle) * sp
            life = random.uniform(0.2, 0.5)
            size = random.uniform(3, 7)
            self.particles.append(Particle(x, y, color, vx, vy, life, size))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.lifetime > 0]

    def draw(self, surface, camera):
        for p in self.particles:
            p.draw(surface, camera)

# ==========================================
# 4. 카메라 및 맵 시스템
# ==========================================
class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.shake_time = 0
        self.shake_intensity = 0

    def apply(self, entity):
        return entity.rect.move(self.rect.topleft)

    def apply_pos(self, pos):
        shake_x = random.uniform(-self.shake_intensity, self.shake_intensity) if self.shake_time > 0 else 0
        shake_y = random.uniform(-self.shake_intensity, self.shake_intensity) if self.shake_time > 0 else 0
        return (pos[0] + self.rect.x + shake_x, pos[1] + self.rect.y + shake_y)

    def apply_rect(self, rect):
        shake_x = random.uniform(-self.shake_intensity, self.shake_intensity) if self.shake_time > 0 else 0
        shake_y = random.uniform(-self.shake_intensity, self.shake_intensity) if self.shake_time > 0 else 0
        return rect.move(self.rect.x + shake_x, self.rect.y + shake_y)

    def update(self, target, dt):
        # 타겟 중앙 추적
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        
        # 맵 경계 제한 (소프트 추적)
        self.rect.x += (x - self.rect.x) * 0.1
        self.rect.y += (y - self.rect.y) * 0.1

        if self.shake_time > 0:
            self.shake_time -= dt

    def shake(self, intensity=5, duration=0.2):
        self.shake_intensity = intensity
        self.shake_time = duration

class DungeonGenerator:
    """무작위 던전 방과 복도를 생성합니다."""
    def __init__(self, map_width_tiles=60, map_height_tiles=60, tile_size=64):
        self.grid_w = map_width_tiles
        self.grid_h = map_height_tiles
        self.tile_size = tile_size
        self.grid = [[1 for _ in range(self.grid_h)] for _ in range(self.grid_w)] # 1: Wall, 0: Floor
        self.rooms = []
        self.generate()

    def generate(self):
        min_room_size = 6
        max_room_size = 12
        max_rooms = 15

        for _ in range(max_rooms):
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            x = random.randint(1, self.grid_w - w - 1)
            y = random.randint(1, self.grid_h - h - 1)

            new_room = pygame.Rect(x, y, w, h)
            failed = False
            for other_room in self.rooms:
                if new_room.colliderect(other_room.inflate(2, 2)):
                    failed = True
                    break

            if not failed:
                self.create_room(new_room)
                if self.rooms:
                    # 이전 방과 복도로 연결
                    prev_x, prev_y = self.rooms[-1].center
                    new_x, new_y = new_room.center
                    if random.randint(0, 1) == 1:
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.rooms.append(new_room)

    def create_room(self, room):
        for x in range(room.left, room.right):
            for y in range(room.top, room.bottom):
                self.grid[x][y] = 0

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.grid[x][y] = 0
            self.grid[x][y+1] = 0

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.grid[x][y] = 0
            self.grid[x+1][y] = 0

    def draw(self, surface, camera):
        start_x = max(0, int(-camera.rect.x // self.tile_size) - 1)
        end_x = min(self.grid_w, start_x + (SCREEN_WIDTH // self.tile_size) + 3)
        start_y = max(0, int(-camera.rect.y // self.tile_size) - 1)
        end_y = min(self.grid_h, start_y + (SCREEN_HEIGHT // self.tile_size) + 3)

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                world_x = x * self.tile_size
                world_y = y * self.tile_size
                screen_pos = camera.apply_pos((world_x, world_y))
                rect = pygame.Rect(screen_pos[0], screen_pos[1], self.tile_size, self.tile_size)
                
                if self.grid[x][y] == 1:
                    pygame.draw.rect(surface, WALL_COLOR, rect)
                    pygame.draw.rect(surface, BLACK, rect, 1)
                else:
                    pygame.draw.rect(surface, FLOOR_COLOR, rect)
                    pygame.draw.rect(surface, (35, 35, 45), rect, 1)

# ==========================================
# 5. 게임 오브젝트 Base 클래스 및 투사체
# ==========================================
class Projectile:
    def __init__(self, x, y, target_x, target_y, speed, damage, owner_tag, color=YELLOW, radius=6):
        self.x = x
        self.y = y
        angle = math.atan2(target_y - y, target_x - x)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.damage = damage
        self.owner_tag = owner_tag
        self.color = color
        self.radius = radius
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.is_alive = True

    def update(self, dt, dungeon):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.rect.center = (int(self.x), int(self.y))

        # 벽 충돌 체크
        tile_x = int(self.x // dungeon.tile_size)
        tile_y = int(self.y // dungeon.tile_size)
        if 0 <= tile_x < dungeon.grid_w and 0 <= tile_y < dungeon.grid_h:
            if dungeon.grid[tile_x][tile_y] == 1:
                self.is_alive = False

    def draw(self, surface, camera):
        pos = camera.apply_pos((self.x, self.y))
        pygame.draw.circle(surface, self.color, (int(pos[0]), int(pos[1])), self.radius)
        pygame.draw.circle(surface, WHITE, (int(pos[0]), int(pos[1])), self.radius // 2)

class Item:
    def __init__(self, x, y, item_type):
        self.rect = pygame.Rect(x - 12, y - 12, 24, 24)
        self.item_type = item_type  # 'health', 'exp', 'stat'
        self.color = GREEN if item_type == 'health' else (CYAN if item_type == 'exp' else YELLOW)
        self.hover_offset = 0

    def update(self, dt):
        self.hover_offset += dt * 5

    def draw(self, surface, camera):
        pos = camera.apply_pos((self.rect.x, self.rect.y + math.sin(self.hover_offset) * 4))
        draw_rect = pygame.Rect(pos[0], pos[1], self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.color, draw_rect, border_radius=4)
        pygame.draw.rect(surface, WHITE, draw_rect, width=2, border_radius=4)

# ==========================================
# 6. 엔티티 클래스 (플레이어 & 적)
# ==========================================
class Entity:
    def __init__(self, x, y, size, hp, speed, color):
        self.rect = pygame.Rect(x, y, size, size)
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.color = color
        self.is_alive = True
        self.vel_x = 0
        self.vel_y = 0

    def take_damage(self, amount):
        self.hp -= amount
        SOUND_SYS.play('hit')
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False

    def move_and_collide(self, dungeon, dt):
        # X축 이동 및 충돌
        self.rect.x += self.vel_x * self.speed * dt * 60
        self.check_collision_x(dungeon)

        # Y축 이동 및 충돌
        self.rect.y += self.vel_y * self.speed * dt * 60
        self.check_collision_y(dungeon)

    def check_collision_x(self, dungeon):
        for x in range(self.rect.left // dungeon.tile_size, self.rect.right // dungeon.tile_size + 1):
            for y in range(self.rect.top // dungeon.tile_size, self.rect.bottom // dungeon.tile_size + 1):
                if 0 <= x < dungeon.grid_w and 0 <= y < dungeon.grid_h:
                    if dungeon.grid[x][y] == 1:
                        wall_rect = pygame.Rect(x * dungeon.tile_size, y * dungeon.tile_size, dungeon.tile_size, dungeon.tile_size)
                        if self.rect.colliderect(wall_rect):
                            if self.vel_x > 0:
                                self.rect.right = wall_rect.left
                            elif self.vel_x < 0:
                                self.rect.left = wall_rect.right

    def check_collision_y(self, dungeon):
        for x in range(self.rect.left // dungeon.tile_size, self.rect.right // dungeon.tile_size + 1):
            for y in range(self.rect.top // dungeon.tile_size, self.rect.bottom // dungeon.tile_size + 1):
                if 0 <= x < dungeon.grid_w and 0 <= y < dungeon.grid_h:
                    if dungeon.grid[x][y] == 1:
                        wall_rect = pygame.Rect(x * dungeon.tile_size, y * dungeon.tile_size, dungeon.tile_size, dungeon.tile_size)
                        if self.rect.colliderect(wall_rect):
                            if self.vel_y > 0:
                                self.rect.bottom = wall_rect.top
                            elif self.vel_y < 0:
                                self.rect.top = wall_rect.bottom

class Player(Entity):
    def __init__(self, x, y, char_class):
        super().__init__(x, y, size=32, hp=100, speed=4.5, color=BLUE)
        self.char_class = char_class # 'Warrior', 'Mage', 'Ranger'
        self.level = 1
        self.exp = 0
        self.max_exp = 50
        self.attack_cooldown = 0
        self.skill_cooldown = 0
        self.dash_cooldown = 0
        self.is_dashing = False
        self.dash_timer = 0

        # 직업별 능력치 조정
        if char_class == 'Warrior':
            self.max_hp = 150
            self.hp = 150
            self.speed = 4.0
            self.color = RED
        elif char_class == 'Mage':
            self.max_hp = 80
            self.hp = 80
            self.speed = 4.5
            self.color = PURPLE
        elif char_class == 'Ranger':
            self.max_hp = 100
            self.hp = 100
            self.speed = 5.2
            self.color = GREEN

    def handle_input(self, keys, mouse_pos, camera, projectiles, particle_mgr):
        self.vel_x = 0
        self.vel_y = 0

        if not self.is_dashing:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.vel_x = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.vel_x = 1
            if keys[pygame.K_w] or keys[pygame.K_UP]: self.vel_y = -1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.vel_y = 1

            # 대각선 이동 속도 보정
            if self.vel_x != 0 and self.vel_y != 0:
                self.vel_x *= 0.7071
                self.vel_y *= 0.7071

            # 스페이스바 대시
            if keys[pygame.K_SPACE] and self.dash_cooldown <= 0:
                self.is_dashing = True
                self.dash_timer = 0.15
                self.dash_cooldown = 1.0
                SOUND_SYS.play('slash')

        # 마우스 월드 좌표 변환
        world_mouse_x = mouse_pos[0] - camera.rect.x
        world_mouse_y = mouse_pos[1] - camera.rect.y

        # 일반 공격 (마우스 좌클릭)
        if pygame.mouse.get_pressed()[0] and self.attack_cooldown <= 0:
            self.attack(world_mouse_x, world_mouse_y, projectiles, particle_mgr)

        # 특수 스킬 (마우스 우클릭)
        if pygame.mouse.get_pressed()[2] and self.skill_cooldown <= 0:
            self.use_skill(world_mouse_x, world_mouse_y, projectiles, particle_mgr)

    def attack(self, target_x, target_y, projectiles, particle_mgr):
        if self.char_class == 'Ranger':
            projectiles.append(Projectile(self.rect.centerx, self.rect.centery, target_x, target_y, 12, 18, 'player', YELLOW, 5))
            self.attack_cooldown = 0.25
            SOUND_SYS.play('shoot')
        elif self.char_class == 'Mage':
            projectiles.append(Projectile(self.rect.centerx, self.rect.centery, target_x, target_y, 8, 25, 'player', CYAN, 8))
            self.attack_cooldown = 0.4
            SOUND_SYS.play('shoot')
        else: # Warrior 근접 파동
            projectiles.append(Projectile(self.rect.centerx, self.rect.centery, target_x, target_y, 10, 35, 'player', ORANGE, 12))
            self.attack_cooldown = 0.35
            SOUND_SYS.play('slash')

    def use_skill(self, target_x, target_y, projectiles, particle_mgr):
        SOUND_SYS.play('skill')
        if self.char_class == 'Mage': # 360도 마법탄
            for i in range(12):
                angle = (math.pi * 2 / 12) * i
                tx = self.rect.centerx + math.cos(angle) * 100
                ty = self.rect.centery + math.sin(angle) * 100
                projectiles.append(Projectile(self.rect.centerx, self.rect.centery, tx, ty, 7, 20, 'player', PURPLE, 7))
            self.skill_cooldown = 4.0

        elif self.char_class == 'Ranger': # 산탄 사격
            base_angle = math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx)
            for offset in [-0.2, -0.1, 0, 0.1, 0.2]:
                ang = base_angle + offset
                tx = self.rect.centerx + math.cos(ang) * 100
                ty = self.rect.centery + math.sin(ang) * 100
                projectiles.append(Projectile(self.rect.centerx, self.rect.centery, tx, ty, 14, 15, 'player', YELLOW, 4))
            self.skill_cooldown = 3.0

        else: # Warrior 충격파
            particle_mgr.create_burst(self.rect.centerx, self.rect.centery, RED, count=30, speed=8)
            for i in range(8):
                angle = (math.pi * 2 / 8) * i
                tx = self.rect.centerx + math.cos(angle) * 100
                ty = self.rect.centery + math.sin(angle) * 100
                projectiles.append(Projectile(self.rect.centerx, self.rect.centery, tx, ty, 6, 40, 'player', RED, 14))
            self.skill_cooldown = 5.0

    def update(self, dt, dungeon):
        # 쿨타임 감소
        if self.attack_cooldown > 0: self.attack_cooldown -= dt
        if self.skill_cooldown > 0: self.skill_cooldown -= dt
        if self.dash_cooldown > 0: self.dash_cooldown -= dt

        # 대시 처리
        if self.is_dashing:
            self.dash_timer -= dt
            self.speed_multiplier = 3.0
            if self.dash_timer <= 0:
                self.is_dashing = False
        else:
            self.speed_multiplier = 1.0

        # 이동 실행
        curr_speed = self.speed * self.speed_multiplier
        self.rect.x += self.vel_x * curr_speed * dt * 60
        self.check_collision_x(dungeon)
        self.rect.y += self.vel_y * curr_speed * dt * 60
        self.check_collision_y(dungeon)

    def add_exp(self, amount):
        self.exp += amount
        if self.exp >= self.max_exp:
            self.level += 1
            self.exp -= self.max_exp
            self.max_exp = int(self.max_exp * 1.4)
            self.max_hp += 15
            self.hp = self.max_hp
            SOUND_SYS.play('item')

    def draw(self, surface, camera):
        pos = camera.apply_rect(self.rect)
        pygame.draw.rect(surface, self.color, pos, border_radius=6)
        pygame.draw.rect(surface, WHITE, pos, width=2, border_radius=6)
        
        # 방향 표시 선
        mouse_pos = pygame.mouse.get_pos()
        angle = math.atan2(mouse_pos[1] - pos.centery, mouse_pos[0] - pos.centerx)
        end_x = pos.centerx + math.cos(angle) * 20
        end_y = pos.centery + math.sin(angle) * 20
        pygame.draw.line(surface, WHITE, pos.center, (end_x, end_y), 3)

class Enemy(Entity):
    def __init__(self, x, y, enemy_type):
        self.enemy_type = enemy_type
        if enemy_type == 'slime':
            super().__init__(x, y, size=28, hp=40, speed=2.0, color=GREEN)
            self.exp_value = 15
            self.damage = 10
        elif enemy_type == 'goblin':
            super().__init__(x, y, size=32, hp=70, speed=3.0, color=ORANGE)
            self.exp_value = 25
            self.damage = 15
            self.shoot_cooldown = 0
        elif enemy_type == 'boss':
            super().__init__(x, y, size=64, hp=400, speed=1.5, color=PURPLE)
            self.exp_value = 150
            self.damage = 25
            self.shoot_cooldown = 0

    def update(self, dt, player, dungeon, projectiles):
        if not self.is_alive:
            return

        # 플레이어 추적 AI
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist > 0:
            self.vel_x = dx / dist
            self.vel_y = dy / dist
        else:
            self.vel_x, self.vel_y = 0, 0

        # 고블린 및 보스의 원거리 공격 AI
        if self.enemy_type in ['goblin', 'boss']:
            self.shoot_cooldown -= dt
            if dist < 400 and self.shoot_cooldown <= 0:
                self.shoot_cooldown = 2.0 if self.enemy_type == 'goblin' else 1.0
                projectiles.append(Projectile(self.rect.centerx, self.rect.centery, 
                                             player.rect.centerx, player.rect.centery, 
                                             6, self.damage, 'enemy', RED, 6))

        # 근접 이동 실행
        if self.enemy_type == 'slime' or dist > 100:
            self.move_and_collide(dungeon, dt)

    def draw(self, surface, camera):
        pos = camera.apply_rect(self.rect)
        pygame.draw.rect(surface, self.color, pos, border_radius=4)
        
        # 체력바 표시
        if self.hp < self.max_hp:
            bar_w = self.rect.width
            bar_h = 4
            hp_ratio = self.hp / self.max_hp
            pygame.draw.rect(surface, RED, (pos.x, pos.y - 8, bar_w, bar_h))
            pygame.draw.rect(surface, GREEN, (pos.x, pos.y - 8, int(bar_w * hp_ratio), bar_h))

# ==========================================
# 7. UI 매니저 (User Interface)
# ==========================================
class UIManager:
    @staticmethod
    def draw_hud(surface, player, dungeon_level):
        # 체력바
        pygame.draw.rect(surface, DARK_GRAY, (20, 20, 200, 20), border_radius=5)
        hp_ratio = max(0, player.hp / player.max_hp)
        pygame.draw.rect(surface, RED, (20, 20, int(200 * hp_ratio), 20), border_radius=5)
        pygame.draw.rect(surface, WHITE, (20, 20, 200, 20), width=2, border_radius=5)
        
        hp_text = FONT_SMALL.render(f"HP: {int(player.hp)} / {player.max_hp}", True, WHITE)
        surface.blit(hp_text, (25, 21))

        # 경험치바
        pygame.draw.rect(surface, DARK_GRAY, (20, 48, 200, 12), border_radius=3)
        exp_ratio = min(1.0, player.exp / player.max_exp)
        pygame.draw.rect(surface, CYAN, (20, 48, int(200 * exp_ratio), 12), border_radius=3)

        # 레벨 및 던전 층수
        info_text = FONT_MEDIUM.render(f"Lv.{player.level} {player.char_class}  |  층수: B{dungeon_level}F", True, YELLOW)
        surface.blit(info_text, (20, 68))

        # 스킬 쿨타임 UI
        UIManager.draw_cooldown_icon(surface, SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, "Dash [Space]", player.dash_cooldown, 1.0)
        UIManager.draw_cooldown_icon(surface, SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60, "Skill [R-Click]", player.skill_cooldown, 4.0)

    @staticmethod
    def draw_cooldown_icon(surface, x, y, label, cd, max_cd):
        rect = pygame.Rect(x, y, 48, 48)
        pygame.draw.rect(surface, DARK_GRAY, rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, rect, width=2, border_radius=8)
        
        if cd > 0:
            ratio = cd / max_cd
            cd_h = int(48 * ratio)
            overlay = pygame.Surface((48, cd_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (x, y + (48 - cd_h)))
            
            cd_text = FONT_SMALL.render(f"{cd:.1f}", True, WHITE)
            surface.blit(cd_text, (x + 10, y + 14))

# ==========================================
# 8. 메인 게임 루프 및 씬 매니저
# ==========================================
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("스트리밋 기가 수행평가 던전 크롤러")
        self.clock = pygame.time.Clock()
        self.state = 'MENU' # MENU, CLASS_SELECT, PLAYING, GAME_OVER
        self.dungeon_level = 1
        
        self.particle_mgr = ParticleManager()
        self.projectiles = []
        self.enemies = []
        self.items = []
        self.selected_class = 'Warrior'

    def start_new_game(self):
        self.dungeon = DungeonGenerator(50, 50, 64)
        start_room = self.dungeon.rooms[0]
        self.player = Player(start_room.centerx * 64, start_room.centery * 64, self.selected_class)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.spawn_enemies_and_items()
        self.state = 'PLAYING'

    def next_floor(self):
        self.dungeon_level += 1
        self.dungeon = DungeonGenerator(50 + self.dungeon_level * 2, 50 + self.dungeon_level * 2, 64)
        start_room = self.dungeon.rooms[0]
        self.player.rect.center = (start_room.centerx * 64, start_room.centery * 64)
        self.projectiles.clear()
        self.enemies.clear()
        self.items.clear()
        self.spawn_enemies_and_items()

    def spawn_enemies_and_items(self):
        for room in self.dungeon.rooms[1:]: # 첫번째 방(출발지)은 제외
            # 적 스폰
            enemy_count = random.randint(2, 4 + self.dungeon_level)
            for _ in range(enemy_count):
                ex = random.randint(room.left + 1, room.right - 2) * 64
                ey = random.randint(room.top + 1, room.bottom - 2) * 64
                etype = random.choice(['slime', 'goblin'])
                self.enemies.append(Enemy(ex, ey, etype))

            # 아이템 스폰
            if random.random() < 0.6:
                ix = room.centerx * 64
                iy = room.centery * 64
                itype = 'health' if random.random() < 0.5 else 'stat'
                self.items.append(Item(ix, iy, itype))

        # 마지막 방 보스 스폰
        boss_room = self.dungeon.rooms[-1]
        self.enemies.append(Enemy(boss_room.centerx * 64, boss_room.centery * 64, 'boss'))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0 # 초 단위 Delta Time

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.state == 'MENU':
                self.update_menu(events)
                self.draw_menu()
            elif self.state == 'CLASS_SELECT':
                self.update_class_select(events)
                self.draw_class_select()
            elif self.state == 'PLAYING':
                self.update_playing(dt)
                self.draw_playing()
            elif self.state == 'GAME_OVER':
                self.update_game_over(events)
                self.draw_game_over()

            pygame.display.flip()

    # --- 씬별 업데이트 & 드로우 ---
    def update_menu(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.state = 'CLASS_SELECT'

    def draw_menu(self):
        self.screen.fill(BLACK)
        title = FONT_LARGE.render("기가 수행평가 RPG: 픽셀 던전", True, YELLOW)
        sub = FONT_MEDIUM.render("[Enter] 키를 눌러 직업 선택으로 이동", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 250))
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 400))

    def update_class_select(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.selected_class = 'Warrior'
                    self.start_new_game()
                elif event.key == pygame.K_2:
                    self.selected_class = 'Mage'
                    self.start_new_game()
                elif event.key == pygame.K_3:
                    self.selected_class = 'Ranger'
                    self.start_new_game()

    def draw_class_select(self):
        self.screen.fill(BLACK)
        title = FONT_LARGE.render("직업을 선택하세요", True, WHITE)
        c1 = FONT_MEDIUM.render("1. 전사 (Warrior) - 체력 높음 / 강력한 근접 공격", True, RED)
        c2 = FONT_MEDIUM.render("2. 마법사 (Mage) - 범위 스킬 / 높은 데미지", True, PURPLE)
        c3 = FONT_MEDIUM.render("3. 궁수 (Ranger) - 빠른 이동 / 기원거리 공격", True, GREEN)
        
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        self.screen.blit(c1, (SCREEN_WIDTH // 2 - c1.get_width() // 2, 280))
        self.screen.blit(c2, (SCREEN_WIDTH // 2 - c2.get_width() // 2, 350))
        self.screen.blit(c3, (SCREEN_WIDTH // 2 - c3.get_width() // 2, 420))

    def update_playing(self, dt):
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # 플레이어 업데이트
        self.player.handle_input(keys, mouse_pos, self.camera, self.projectiles, self.particle_mgr)
        self.player.update(dt, self.dungeon)

        if not self.player.is_alive:
            self.state = 'GAME_OVER'

        # 카메라 추적
        self.camera.update(self.player, dt)

        # 파티클 업데이트
        self.particle_mgr.update(dt)

        # 아이템 획득 체크
        for item in self.items[:]:
            item.update(dt)
            if self.player.rect.colliderect(item.rect):
                if item.item_type == 'health':
                    self.player.hp = min(self.player.max_hp, self.player.hp + 30)
                elif item.item_type == 'stat':
                    self.player.add_exp(20)
                SOUND_SYS.play('item')
                self.items.remove(item)

        # 투사체 업데이트 및 충돌
        for p in self.projectiles[:]:
            p.update(dt, self.dungeon)
            if not p.is_alive:
                self.projectiles.remove(p)
                continue

            # 플레이어 투사체 -> 적 타격
            if p.owner_tag == 'player':
                for e in self.enemies:
                    if e.rect.colliderect(p.rect):
                        e.take_damage(p.damage)
                        self.particle_mgr.create_burst(p.x, p.y, RED, 6)
                        p.is_alive = False
                        self.camera.shake(3, 0.1)
                        if not e.is_alive:
                            self.player.add_exp(e.exp_value)
                        break
            # 적 투사체 -> 플레이어 타격
            elif p.owner_tag == 'enemy':
                if self.player.rect.colliderect(p.rect):
                    self.player.take_damage(p.damage)
                    self.particle_mgr.create_burst(p.x, p.y, WHITE, 8)
                    p.is_alive = False
                    self.camera.shake(6, 0.15)

        # 적 AI 및 충돌
        for e in self.enemies[:]:
            e.update(dt, self.player, self.dungeon, self.projectiles)
            if not e.is_alive:
                self.enemies.remove(e)
                continue

            # 적 플레이어 접촉 데미지
            if e.rect.colliderect(self.player.rect) and not self.player.is_dashing:
                self.player.take_damage(e.damage * dt)

        # 모든 적 처치 시 다음 층 이동
        if len(self.enemies) == 0:
            self.next_floor()

    def draw_playing(self):
        self.screen.fill(BLACK)

        # 던전 맵
        self.dungeon.draw(self.screen, self.camera)

        # 아이템
        for item in self.items:
            item.draw(self.screen, self.camera)

        # 적
        for e in self.enemies:
            e.draw(self.screen, self.camera)

        # 플레이어
        self.player.draw(self.screen, self.camera)

        # 투사체
        for p in self.projectiles:
            p.draw(self.screen, self.camera)

        # 파티클
        self.particle_mgr.draw(self.screen, self.camera)

        # UI / HUD
        UIManager.draw_hud(self.screen, self.player, self.dungeon_level)

    def update_game_over(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.dungeon_level = 1
                self.state = 'CLASS_SELECT'

    def draw_game_over(self):
        self.screen.fill(BLACK)
        title = FONT_LARGE.render("GAME OVER", True, RED)
        sub = FONT_MEDIUM.render(f"최종 돌파 층수: B{self.dungeon_level}F | [R] 키를 눌러 재도전", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 250))
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 380))

# ==========================================
# 실행부
# ==========================================
if __name__ == "__main__":
    game = Game()
    game.run()
