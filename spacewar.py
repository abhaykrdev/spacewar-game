import pygame
from pygame import mixer
import random
import math

pygame.init()

# Game Constants
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 788
FPS = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
background = pygame.image.load('Assets/img/bg_main.jpg')
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Enhanced")

icon = pygame.image.load('Assets/img/spaceship.png')
pygame.display.set_icon(icon)

class GameState:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.high_score = self.load_high_score()
        self.game_over = False
        self.paused = False
        self.enemies_killed = 0
        self.difficulty_multiplier = 1.0

    def load_high_score(self):
        try:
            with open('high_score.txt', 'r') as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open('high_score.txt', 'w') as f:
                f.write(str(self.high_score))

    def update_difficulty(self, total_enemies, remaining_enemies):
        if remaining_enemies > 0:
            kill_ratio = (total_enemies - remaining_enemies) / total_enemies
            self.difficulty_multiplier = 1.0 + (kill_ratio * 2.0) + (self.level * 0.3)

class Player:
    def __init__(self):
        self.image = pygame.image.load('Assets/img/player.png')
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 3
        self.speed_y = 1
        self.shield = 100
        self.power_level = 1
        self.power_time = 0
        self.invulnerable = False
        self.invulnerable_time = 0

    def update(self):
        if self.power_time > 0:
            self.power_time -= 1
            if self.power_time <= 0:
                self.power_level = max(1, self.power_level - 1)

        if self.invulnerable_time > 0:
            self.invulnerable_time -= 1
            if self.invulnerable_time <= 0:
                self.invulnerable = False

    def move(self, keys):
        self.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed_x
        self.rect.y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed_y
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(350, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

    def power_up(self, power_type):
        if power_type == "double_shot":
            self.power_level = min(3, self.power_level + 1)
            self.power_time = 600
        elif power_type == "shield":
            self.shield = min(100, self.shield + 25)

    def take_damage(self, damage=20):
        if not self.invulnerable:
            self.shield -= damage
            self.invulnerable = True
            self.invulnerable_time = 120
            return self.shield <= 0
        return False

    def draw(self, surface):
        if not self.invulnerable or (self.invulnerable_time // 5) % 2:
            surface.blit(self.image, self.rect)

class Bullet:
    def __init__(self, x, y, speed=-3, bullet_type="player"):
        if bullet_type == "enemy_sniper":
            self.image = pygame.Surface((8, 16))
            self.image.fill(RED)
        elif bullet_type == "enemy_tank":
            self.image = pygame.Surface((12, 20))
            self.image.fill(ORANGE)
        else:
            self.image = pygame.image.load('Assets/img/bullet.png')
            self.image = pygame.transform.scale(self.image, (32, 32))
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = speed
        self.bullet_type = bullet_type

    def update(self):
        self.rect.y += self.speed
        return self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Enemy:
    def __init__(self, x, y, enemy_type="basic"):
        self.enemy_type = enemy_type
        self.setup_enemy_properties()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.shoot_timer = random.randint(60, 300)
        self.special_timer = 0
        self.direction_change_timer = 0
        self.spawned_minions = 0
        self.max_minions = 2

    def setup_enemy_properties(self):
        if self.enemy_type == "basic":
            self.image = pygame.image.load('Assets/img/enemy.png')
            self.image = pygame.transform.scale(self.image, (80, 80))
            self.speed_x = random.choice([2, 6])
            self.speed_y = 30
            self.health = 2
            self.points = 10
            self.shoot_frequency = 0.3
        
        elif self.enemy_type == "fast":
            self.image = pygame.image.load('Assets/img/enemy2.png')
            self.image = pygame.transform.scale(self.image, (50, 50))
            self.speed_x = 8
            self.speed_y = 25
            self.health = 1
            self.points = 15
            self.shoot_frequency = 0.4
        
        elif self.enemy_type == "tank":
            self.image = pygame.image.load('Assets/img/enemy3.png')
            self.image = pygame.transform.scale(self.image,(60, 60))
            self.speed_x = random.choice([1, 3])
            self.speed_y = 35
            self.health = 3
            self.points = 25
            self.shoot_frequency = 0.5
        
        elif self.enemy_type == "sniper":
            self.image = pygame.image.load('Assets/img/enemy4.png')
            self.image = pygame.transform.scale(self.image,(70, 70))
            self.speed_x = random.choice([1, 4])
            self.speed_y = 32
            self.health = 1
            self.points = 20
            self.shoot_frequency = 0.6
        
        elif self.enemy_type == "zigzag":
            self.image = pygame.image.load('Assets/img/enemy4.png')
            self.image = pygame.transform.scale(self.image,(70, 70))
            self.speed_x = random.choice([3, 7])
            self.speed_y = 25
            self.health = 1
            self.points = 18
            self.shoot_frequency = 0.35
            self.zigzag_amplitude = 50
            self.zigzag_frequency = 0.1

    def update(self, difficulty_multiplier=1.0, player_pos=None):
        if self.enemy_type == "zigzag":
            self.special_timer += 1
            zigzag_offset = math.sin(self.special_timer * self.zigzag_frequency) * self.zigzag_amplitude
            self.rect.x += self.speed_x * difficulty_multiplier + zigzag_offset * 0.1
        else:
            self.rect.x += self.speed_x * difficulty_multiplier

        self.shoot_timer -= 1
        self.direction_change_timer += 1

        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed_x *= -1
            self.rect.y += self.speed_y * difficulty_multiplier
            if self.direction_change_timer > 30:
                self.direction_change_timer = 0

        return self.rect.y > 300

    def should_shoot(self):
        if self.shoot_timer <= 0:
            base_timer = 180 if self.enemy_type != "sniper" else 120
            variation = 600 if self.enemy_type != "tank" else 300
            self.shoot_timer = random.randint(base_timer, variation)
            return True
        return False

    def get_bullet_type(self):
        if self.enemy_type == "tank":
            return "enemy_tank"
        elif self.enemy_type == "sniper":
            return "enemy_sniper"
        return "enemy"

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class PowerUp:
    def __init__(self, x, y):
        self.type = random.choice(["double_shot", "shield"])
        size = (40, 40)
        if self.type == "double_shot":
            self.image = pygame.Surface(size)
            self.image.fill(BLUE)
        else:
            self.image = pygame.Surface(size)
            self.image.fill(GREEN)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        return self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-3, 3)
        self.life = 30
        self.color = random.choice([RED, YELLOW, ORANGE])

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        return self.life <= 0

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)

class Game:
    def __init__(self):
        self.state = GameState()
        self.player = Player()
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.power_ups = []
        self.particles = []
        self.font = pygame.font.Font('Assets/font/evil_empire.otf', 64)
        self.small_font = pygame.font.Font('Assets/font/evil_empire.otf', 32)
        self.last_shot = 0
        self.shoot_delay = 250
        self.total_enemies = 0
        self.spawn_enemies()

    def spawn_enemies(self):
        base_count = 6 + self.state.level
        enemy_types = ["basic", "fast", "tank", "sniper", "zigzag"]
        
        if self.state.level <= 2:
            enemy_types = ["basic", "fast"]
        elif self.state.level <= 4:
            enemy_types = ["basic", "fast", "tank"]
        elif self.state.level <= 6:
            enemy_types = ["basic", "fast", "tank", "sniper"]
        
        self.enemies.clear()
        self.total_enemies = base_count
        
        for i in range(base_count):
            x = random.randint(0, SCREEN_WIDTH - 100)
            y = random.randint(50, 150)
            
            if self.state.level >= 8 and random.random() < 0.15:
                enemy_type = "spawner"
            elif self.state.level >= 5 and random.random() < 0.2:
                enemy_type = random.choice(["sniper", "zigzag"])
            elif self.state.level >= 3 and random.random() < 0.3:
                enemy_type = "tank"
            else:
                enemy_type = random.choice(enemy_types)
            
            self.enemies.append(Enemy(x, y, enemy_type))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_p] and not hasattr(self, 'p_pressed'):
            self.state.paused = not self.state.paused
            self.p_pressed = True
        elif not keys[pygame.K_p]:
            self.p_pressed = False

        if self.state.paused or self.state.game_over:
            return

        self.player.move(keys)

        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot > self.shoot_delay:
                self.shoot_bullet()
                self.last_shot = current_time

    def shoot_bullet(self):
        bullet_sound = mixer.Sound('Assets/sound/shoot.wav')
        bullet_sound.play()

        if self.player.power_level == 1:
            self.bullets.append(Bullet(self.player.rect.centerx, self.player.rect.top))
        elif self.player.power_level == 2:
            self.bullets.append(Bullet(self.player.rect.centerx - 15, self.player.rect.top))
            self.bullets.append(Bullet(self.player.rect.centerx + 15, self.player.rect.top))
        else:
            self.bullets.append(Bullet(self.player.rect.centerx - 20, self.player.rect.top))
            self.bullets.append(Bullet(self.player.rect.centerx, self.player.rect.top))
            self.bullets.append(Bullet(self.player.rect.centerx + 20, self.player.rect.top))

    def update(self):
        if self.state.paused or self.state.game_over:
            return

        self.player.update()
        self.state.update_difficulty(self.total_enemies, len(self.enemies))

        self.bullets = [b for b in self.bullets if not b.update()]
        self.enemy_bullets = [b for b in self.enemy_bullets if not b.update()]

        for enemy in self.enemies[:]:
            if enemy.update(self.state.difficulty_multiplier, self.player.rect.center):
                self.game_over()
                return

            if enemy.should_shoot() and random.random() < enemy.shoot_frequency:
                bullet_speed = 2
                if enemy.enemy_type == "sniper":
                    dx = self.player.rect.centerx - enemy.rect.centerx
                    dy = self.player.rect.centery - enemy.rect.centery
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance > 0:
                        bullet_speed = 3
                        self.enemy_bullets.append(Bullet(
                            enemy.rect.centerx + dx/distance * 20, 
                            enemy.rect.bottom + dy/distance * 20, 
                            bullet_speed, 
                            enemy.get_bullet_type()
                        ))
                elif enemy.enemy_type == "tank":
                    self.enemy_bullets.append(Bullet(enemy.rect.centerx - 10, enemy.rect.bottom, 2, "enemy_tank"))
                    self.enemy_bullets.append(Bullet(enemy.rect.centerx + 10, enemy.rect.bottom, 2, "enemy_tank"))
                else:
                    self.enemy_bullets.append(Bullet(enemy.rect.centerx, enemy.rect.bottom, bullet_speed))

        self.power_ups = [p for p in self.power_ups if not p.update()]
        self.particles = [p for p in self.particles if not p.update()]

        self.check_collisions()

        if not self.enemies:
            self.next_level()

    def check_collisions(self):
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.bullets.remove(bullet)
                    if enemy.take_damage():
                        self.enemies.remove(enemy)
                        self.state.score += enemy.points
                        self.state.enemies_killed += 1
                        self.create_explosion(enemy.rect.centerx, enemy.rect.centery)
                        
                        power_up_chance = 0.15 - (self.state.level * 0.01)
                        power_up_chance = max(0.05, power_up_chance)
                        if random.random() < power_up_chance:
                            self.power_ups.append(PowerUp(enemy.rect.centerx, enemy.rect.centery))
                    break

        for bullet in self.enemy_bullets[:]:
            if bullet.rect.colliderect(self.player.rect):
                self.enemy_bullets.remove(bullet)
                damage = 20
                if bullet.bullet_type == "enemy_tank":
                    damage = 35
                elif bullet.bullet_type == "enemy_sniper":
                    damage = 25
                
                if self.player.take_damage(damage):
                    self.lose_life()

        for power_up in self.power_ups[:]:
            if power_up.rect.colliderect(self.player.rect):
                self.power_ups.remove(power_up)
                self.player.power_up(power_up.type)

    def create_explosion(self, x, y):
        explosion_sound = mixer.Sound('Assets/sound/explosion.wav')
        explosion_sound.play()
        
        for _ in range(15):
            self.particles.append(Particle(x, y))

    def lose_life(self):
        self.state.lives -= 1
        self.player.shield = 100
        if self.state.lives <= 0:
            self.game_over()
        else:
            self.player.invulnerable = True
            self.player.invulnerable_time = 180

    def game_over(self):
        self.state.game_over = True
        self.state.save_high_score()

    def next_level(self):
        self.state.level += 1
        self.spawn_enemies()

    def restart(self):
        self.__init__()

    def draw(self):
        screen.fill(BLACK)
        screen.blit(background, (0, 0))

        for x in range(0, SCREEN_WIDTH, 20):
            pygame.draw.line(screen, WHITE, (x, 350), (x + 10, 350), 2)

        if not self.state.game_over:
            self.player.draw(screen)

        for bullet in self.bullets: 
            bullet.draw(screen)

        for bullet in self.enemy_bullets:
            bullet.draw(screen)

        for enemy in self.enemies:
            enemy.draw(screen)

        for power_up in self.power_ups:
            power_up.draw(screen)

        for particle in self.particles:
            particle.draw(screen)

        self.draw_ui()

        if self.state.paused:
            self.draw_pause_screen()
        elif self.state.game_over:
            self.draw_game_over_screen()

    def draw_ui(self):
        score_text = self.small_font.render(f"Score: {self.state.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        high_score_text = self.small_font.render(f"High: {self.state.high_score}", True, WHITE)
        screen.blit(high_score_text, (10, 50))

        lives_text = self.small_font.render(f"Lives: {self.state.lives}", True, WHITE)
        screen.blit(lives_text, (10, 90))

        level_text = self.small_font.render(f"Level: {self.state.level}", True, WHITE)
        screen.blit(level_text, (10, 130))

        difficulty_text = self.small_font.render(f"Difficulty: {self.state.difficulty_multiplier:.1f}x", True, YELLOW)
        screen.blit(difficulty_text, (10, 170))

        if not self.state.game_over:
            shield_width = int((self.player.shield / 100) * 200)
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH - 220, 20, 200, 20))
            pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 220, 20, shield_width, 20))
            shield_text = self.small_font.render("Shield", True, WHITE)
            screen.blit(shield_text, (SCREEN_WIDTH - 220, 45))

            if self.player.power_level > 1:
                power_text = self.small_font.render(f"Power: {self.player.power_level}", True, YELLOW)
                screen.blit(power_text, (SCREEN_WIDTH - 220, 80))

    def draw_pause_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        pause_text = self.font.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, text_rect)

        continue_text = self.small_font.render("Press P to continue", True, WHITE)
        text_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        screen.blit(continue_text, text_rect)

    def draw_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(game_over_text, text_rect)

        final_score_text = self.small_font.render(f"Final Score: {self.state.score}", True, WHITE)
        text_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(final_score_text, text_rect)

        if self.state.score == self.state.high_score and self.state.score > 0:
            new_record_text = self.small_font.render("NEW HIGH SCORE!", True, YELLOW)
            text_rect = new_record_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(new_record_text, text_rect)

        restart_text = self.small_font.render("Press R to restart or Q to quit", True, WHITE)
        text_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        screen.blit(restart_text, text_rect)

def main():
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game.state.game_over:
                    if event.key == pygame.K_r:
                        game.restart()
                    elif event.key == pygame.K_q:
                        running = False

        game.handle_input()
        game.update()
        game.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()