import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -12
PLAYER_SPEED = 5

# Colors
SKY_BLUE = (107, 140, 255)
GREEN = (0, 168, 0)
BROWN = (180, 122, 48)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_BLUE = (173, 216, 230)
DARK_GREEN = (0, 100, 0)
PURPLE = (200, 0, 200)
ORANGE = (255, 165, 0)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(RED)
        # Draw a simple Mario-like character
        pygame.draw.rect(self.image, RED, (0, 0, 30, 50))
        pygame.draw.rect(self.image, (255, 200, 150), (5, 5, 20, 15))  # Face
        pygame.draw.rect(self.image, RED, (0, 20, 30, 10))  # Hat brim
        pygame.draw.rect(self.image, BLUE, (0, 30, 30, 20))  # Overalls
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.lives = 3
        
    def update(self, platforms):
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Move horizontally
        self.rect.x += self.vel_x
        
        # Check for horizontal collisions
        platform_hits = pygame.sprite.spritecollide(self, platforms, False)
        for platform in platform_hits:
            if self.vel_x > 0:  # Moving right
                self.rect.right = platform.rect.left
            elif self.vel_x < 0:  # Moving left
                self.rect.left = platform.rect.right
                
        # Move vertically
        self.rect.y += self.vel_y
        self.on_ground = False
        
        # Check for vertical collisions
        platform_hits = pygame.sprite.spritecollide(self, platforms, False)
        for platform in platform_hits:
            if self.vel_y > 0:  # Falling
                self.rect.bottom = platform.rect.top
                self.on_ground = True
                self.vel_y = 0
            elif self.vel_y < 0:  # Jumping
                self.rect.top = platform.rect.bottom
                self.vel_y = 0
                
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            
    def move_left(self):
        self.vel_x = -PLAYER_SPEED
        self.facing_right = False
        
    def move_right(self):
        self.vel_x = PLAYER_SPEED
        self.facing_right = True
        
    def stop(self):
        self.vel_x = 0
        
    def reset_position(self):
        self.rect.x = 100
        self.rect.y = 300
        self.vel_x = 0
        self.vel_y = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=GREEN):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        # Add texture to platform
        for i in range(0, width, 10):
            pygame.draw.line(self.image, (0, 128, 0), (i, 0), (i, height), 1)
        for i in range(0, height, 10):
            pygame.draw.line(self.image, (0, 128, 0), (0, i), (width, i), 1)
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (7, 7), 7)
        pygame.draw.circle(self.image, (200, 200, 0), (7, 7), 5)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((150, 75, 0))  # Brown color for Goomba
        # Draw eyes
        pygame.draw.circle(self.image, WHITE, (8, 10), 5)
        pygame.draw.circle(self.image, WHITE, (22, 10), 5)
        pygame.draw.circle(self.image, (0, 0, 0), (8, 10), 2)
        pygame.draw.circle(self.image, (0, 0, 0), (22, 10), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1  # 1 for right, -1 for left
        self.speed = 2
        
    def update(self, platforms):
        self.rect.x += self.speed * self.direction
        
        # Change direction if hitting a platform edge or wall
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1
            
        # Check if about to fall off a platform
        test_rect = self.rect.copy()
        test_rect.x += self.speed * self.direction
        test_rect.y += 5  # Look a bit below
        
        on_platform = False
        for platform in platforms:
            if test_rect.colliderect(platform.rect):
                on_platform = True
                break
                
        if not on_platform:
            self.direction *= -1

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill((255, 215, 0))  # Gold color
        # Draw flag pole
        pygame.draw.rect(self.image, GRAY, (15, 0, 10, 60))
        # Draw flag
        pygame.draw.polygon(self.image, RED, [(25, 10), (25, 30), (40, 20)])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class OverworldMap:
    def __init__(self):
        # Create a more connected overworld with branching paths
        self.nodes = [
            # World 1 - Grass Land
            {"x": 100, "y": 100, "level": 1, "completed": False, "type": "start", "world": 1},
            {"x": 250, "y": 100, "level": 2, "completed": False, "type": "normal", "world": 1},
            {"x": 400, "y": 100, "level": 3, "completed": False, "type": "normal", "world": 1},
            
            # World 2 - Desert Hills
            {"x": 175, "y": 200, "level": 4, "completed": False, "type": "normal", "world": 2},
            {"x": 325, "y": 200, "level": 5, "completed": False, "type": "boss", "world": 2},
            
            # World 3 - Sky World
            {"x": 250, "y": 300, "level": 6, "completed": False, "type": "normal", "world": 3},
            {"x": 400, "y": 300, "level": 7, "completed": False, "type": "normal", "world": 3},
            
            # World 4 - Ice Land
            {"x": 325, "y": 400, "level": 8, "completed": False, "type": "castle", "world": 4}
        ]
        
        # Define connections between nodes (bidirectional)
        self.connections = [
            (0, 1), (1, 2),  # World 1
            (1, 3), (2, 4),  # Branching to World 2
            (3, 5), (4, 5),  # Rejoining at World 3
            (5, 6), (6, 7)   # To World 4 castle
        ]
        
        self.current_node = 0
        self.player_pos = [self.nodes[0]["x"], self.nodes[0]["y"]]
        self.unlocked_nodes = {0}  # Start with first node unlocked
        
    def draw(self, screen):
        # Draw connections (paths) between nodes
        for connection in self.connections:
            start = self.nodes[connection[0]]
            end = self.nodes[connection[1]]
            
            # Only draw path if at least one node is unlocked
            if connection[0] in self.unlocked_nodes or connection[1] in self.unlocked_nodes:
                pygame.draw.line(screen, BROWN, (start["x"], start["y"]), (end["x"], end["y"]), 5)
            
        # Draw nodes
        for i, node in enumerate(self.nodes):
            # Determine node color based on type and state
            if node["type"] == "start":
                color = GREEN
            elif node["type"] == "boss":
                color = RED
            elif node["type"] == "castle":
                color = PURPLE
            else:
                color = YELLOW if node["completed"] else BLUE
                
            # Draw node (only if unlocked)
            if i in self.unlocked_nodes:
                pygame.draw.circle(screen, color, (node["x"], node["y"]), 20)
                
                # Draw node border
                border_color = DARK_GREEN if node["completed"] else BLACK
                pygame.draw.circle(screen, border_color, (node["x"], node["y"]), 20, 2)
                
                # Draw level number
                font = pygame.font.SysFont(None, 24)
                text = font.render(str(node["level"]), True, WHITE)
                screen.blit(text, (node["x"] - 5, node["y"] - 8))
            
        # Draw player
        pygame.draw.circle(screen, RED, (int(self.player_pos[0]), int(self.player_pos[1])), 15)
        pygame.draw.circle(screen, (255, 100, 100), (int(self.player_pos[0]), int(self.player_pos[1])), 15, 2)
        
    def move(self, direction):
        current_node = self.nodes[self.current_node]
        possible_moves = []
        
        # Find all connected nodes
        for connection in self.connections:
            if connection[0] == self.current_node and connection[1] in self.unlocked_nodes:
                possible_moves.append(connection[1])
            elif connection[1] == self.current_node and connection[0] in self.unlocked_nodes:
                possible_moves.append(connection[0])
        
        if not possible_moves:
            return False
            
        # Simple direction-based movement
        # Find the node that best matches the direction
        target_node = None
        
        for node_idx in possible_moves:
            node = self.nodes[node_idx]
            dx = node["x"] - current_node["x"]
            dy = node["y"] - current_node["y"]
            
            # Check if this node is in the requested direction
            if direction == "right" and dx > 0:
                target_node = node_idx
                break
            elif direction == "left" and dx < 0:
                target_node = node_idx
                break
            elif direction == "down" and dy > 0:
                target_node = node_idx
                break
            elif direction == "up" and dy < 0:
                target_node = node_idx
                break
                
        # If no exact direction match, just pick the first available
        if target_node is None and possible_moves:
            target_node = possible_moves[0]
            
        if target_node is not None:
            self.current_node = target_node
            target_node_data = self.nodes[self.current_node]
            self.player_pos = [target_node_data["x"], target_node_data["y"]]
            return True
            
        return False
        
    def complete_current_level(self):
        # Mark current level as completed
        self.nodes[self.current_node]["completed"] = True
        
        # Unlock connected nodes
        for connection in self.connections:
            if connection[0] == self.current_node:
                self.unlocked_nodes.add(connection[1])
            elif connection[1] == self.current_node:
                self.unlocked_nodes.add(connection[0])
        
    def get_current_level(self):
        return self.nodes[self.current_node]["level"]

class Level:
    def __init__(self, level_number, player_lives):
        self.level_number = level_number
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.goals = pygame.sprite.Group()
        self.score = 0
        self.completed = False
        
        # Create player with current lives
        self.player = Player(100, 300)
        self.player.lives = player_lives
        self.all_sprites.add(self.player)
        
        # Create level based on level number
        self.create_level(level_number)
        
    def create_level(self, level_number):
        # Ground
        ground = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)
        self.all_sprites.add(ground)
        self.platforms.add(ground)
        
        if level_number == 1:
            self.create_level1()
        elif level_number == 2:
            self.create_level2()
        elif level_number == 3:
            self.create_level3()
        elif level_number == 4:
            self.create_level4()
        elif level_number == 5:
            self.create_level5()
        elif level_number == 6:
            self.create_level6()
        elif level_number == 7:
            self.create_level7()
        elif level_number == 8:
            self.create_level8()
            
    def create_level1(self):
        # World 1-1: Simple beginner level
        platforms_data = [
            (100, 450, 200, 20),
            (400, 400, 150, 20),
            (200, 350, 100, 20),
            (500, 300, 200, 20),
        ]
        
        for x, y, width, height in platforms_data:
            platform = Platform(x, y, width, height)
            self.all_sprites.add(platform)
            self.platforms.add(platform)
            
        # Coins
        coin_positions = [(150, 400), (450, 350), (250, 300), (550, 250)]
        for x, y in coin_positions:
            coin = Coin(x, y)
            self.all_sprites.add(coin)
            self.coins.add(coin)
            
        # Goal
        goal = Goal(700, 340)
        self.all_sprites.add(goal)
        self.goals.add(goal)
            
    def create_level2(self):
        # World 1-2: Level with more platforms and enemies
        platforms_data = [
            (100, 450, 200, 20),
            (400, 400, 150, 20),
            (200, 350, 100, 20),
            (500, 300, 200, 20),
            (100, 250, 150, 20),
        ]
        
        for x, y, width, height in platforms_data:
            platform = Platform(x, y, width, height)
            self.all_sprites.add(platform)
            self.platforms.add(platform)
            
        # Coins
        for i in range(8):
            coin = Coin(random.randint(50, SCREEN_WIDTH - 50), 
                       random.randint(100, SCREEN_HEIGHT - 100))
            self.all_sprites.add(coin)
            self.coins.add(coin)
            
        # Enemies
        for i in range(2):
            enemy = Enemy(random.randint(100, SCREEN_WIDTH - 100), 
                         SCREEN_HEIGHT - 70)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
            
        # Goal
        goal = Goal(700, 240)
        self.all_sprites.add(goal)
        self.goals.add(goal)
            
    def create_level3(self):
        # World 1-3: Challenging level with gaps
        platforms_data = [
            (0, 450, 150, 20),
            (250, 450, 150, 20),
            (500, 450, 150, 20),
            (100, 350, 150, 20),
            (350, 350, 150, 20),
            (600, 350, 150, 20),
            (200, 250, 150, 20),
            (450, 250, 150, 20),
        ]
        
        for x, y, width, height in platforms_data:
            platform = Platform(x, y, width, height)
            self.all_sprites.add(platform)
            self.platforms.add(platform)
            
        # Coins
        for i in range(10):
            coin = Coin(random.randint(50, SCREEN_WIDTH - 50), 
                       random.randint(100, SCREEN_HEIGHT - 100))
            self.all_sprites.add(coin)
            self.coins.add(coin)
            
        # Enemies
        for i in range(3):
            enemy = Enemy(random.randint(100, SCREEN_WIDTH - 100), 
                         SCREEN_HEIGHT - 70)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
            
        # Goal
        goal = Goal(700, 200)
        self.all_sprites.add(goal)
        self.goals.add(goal)
            
    def create_level4(self):
        # World 2-1: Desert theme with pyramids
        platforms_data = [
            (100, 450, 200, 20),
            (150, 350, 100, 20),
            (200, 250, 100, 20),
            (500, 450, 200, 20),
            (450, 350, 100, 20),
            (400, 250, 100, 20),
            (300, 150, 200, 20),  # Pyramid top
        ]
        
        for x, y, width, height in platforms_data:
            platform = Platform(x, y, width, height, (210, 180, 140))  # Sand color
            self.all_sprites.add(platform)
            self.platforms.add(platform)
            
        # Coins
        for i in range(12):
            coin = Coin(random.randint(50, SCREEN_WIDTH - 50), 
                       random.randint(100, SCREEN_HEIGHT - 100))
            self.all_sprites.add(coin)
            self.coins.add(coin)
            
        # Enemies
        for i in range(4):
            enemy = Enemy(random.randint(100, SCREEN_WIDTH - 100), 
                         SCREEN_HEIGHT - 70)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
            
        # Goal
        goal = Goal(350, 100)
        self.all_sprites.add(goal)
        self.goals.add(goal)
            
    def create_level5(self):
        # World 2-2: Boss level - more challenging
        platforms_data = [
            (0, 450, 100, 20),
            (150, 450, 100, 20),
            (300, 450, 100, 20),
            (450, 450, 100, 20),
            (600, 450, 100, 20),
            (50, 350, 100, 20),
            (250, 350, 100, 20),
            (450, 350, 100, 20),
            (650, 350, 100, 20),
            (100, 250, 100, 20),
            (350, 250, 100, 20),
            (600, 250, 100, 20),
        ]
        
        for x, y, width, height in platforms_data:
            platform = Platform(x, y, width, height, (210, 180, 140))  # Sand color
            self.all_sprites.add(platform)
            self.platforms.add(platform)
            
        # Coins
        for i in range(15):
            coin = Coin(random.randint(50, SCREEN_WIDTH - 50), 
                       random.randint(100, SCREEN_HEIGHT - 100))
            self.all_sprites.add(coin)
            self.coins.add(coin)
            
        # Enemies
        for i in range(5):
            enemy = Enemy(random.randint(100, SCREEN_WIDTH - 100), 
                         SCREEN_HEIGHT - 70)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
            
        # Goal
        goal = Goal(700, 200)
        self.all_sprites.add(goal)
        self.goals.add(goal)
            
    def create_level6(self):
        # World 3-1: Sky world with floating platforms
        platforms_data = [
            (100, 450, 200, 20),
            (400, 400, 150, 20),
            (200, 350, 100, 20),
            (500, 300, 200, 20),
            (100, 250, 150, 20),
            (350, 200, 100, 20),
            (600, 150, 100, 20),
        ]
        
        for x, y, width, height in platforms_data:
            platform = Platform(x, y, width, height, (200, 200, 255))  # Light blue
            self.all_sprites.add(platform)
            self.platforms.add(platform)
            
        # Coins
        for i in range(10):
            coin = Coin(random.randint(50, SCREEN_WIDTH - 50), 
                       random.randint(100, SCREEN_HEIGHT - 100))
            self.all_sprites.add(coin)
            self.coins.add(coin)
            
        # Enemies
        for i in range(3):
            enemy = Enemy(random.randint(100, SCREEN_WIDTH - 100), 
                         SCREEN_HEIGHT - 70)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
            
        # Goal
        goal = Goal(650, 100)
        self.all_sprites.add(goal)
        self.goals.add(goal)
            
    def create_level7(self):
        # World 3-2: Penultimate challenge
        platforms_data = [
            (0, 450, 150, 20),
            (250, 450, 150, 20),
            (500, 450, 150, 20),
            (100, 350, 150, 20),
            (350, 350, 150, 20),
            (600, 350, 150, 20),
            (200, 250, 150, 20),
            (450, 250, 150, 20),
            (300, 150, 150, 20),
        ]
        
        for x, y, width, height in platforms_data:
            platform = Platform(x, y, width, height, (200, 200, 255))  # Light blue
            self.all_sprites.add(platform)
            self.platforms.add(platform)
            
        # Coins
        for i in range(12):
            coin = Coin(random.randint(50, SCREEN_WIDTH - 50), 
                       random.randint(100, SCREEN_HEIGHT - 100))
            self.all_sprites.add(coin)
            self.coins.add(coin)
            
        # Enemies
        for i in range(4):
            enemy = Enemy(random.randint(100, SCREEN_WIDTH - 100), 
                         SCREEN_HEIGHT - 70)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
            
        # Goal
        goal = Goal(700, 100)
        self.all_sprites.add(goal)
        self.goals.add(goal)
            
    def create_level8(self):
        # World 4-1: Final castle level
        platforms_data = [
            (0, 450, 100, 20),
            (150, 450, 100, 20),
            (300, 450, 100, 20),
            (450, 450, 100, 20),
            (600, 450, 100, 20),
            (700, 450, 100, 20),
            (50, 350, 100, 20),
            (250, 350, 100, 20),
            (450, 350, 100, 20),
            (650, 350, 100, 20),
            (100, 250, 100, 20),
            (350, 250, 100, 20),
            (600, 250, 100, 20),
            (200, 150, 100, 20),
            (500, 150, 100, 20),
            (350, 50, 100, 20),  # Top platform - goal
        ]
        
        for x, y, width, height in platforms_data:
            platform = Platform(x, y, width, height, (150, 150, 150))  # Gray for castle
            self.all_sprites.add(platform)
            self.platforms.add(platform)
            
        # Coins
        for i in range(20):  # More coins in final level
            coin = Coin(random.randint(50, SCREEN_WIDTH - 50), 
                       random.randint(100, SCREEN_HEIGHT - 100))
            self.all_sprites.add(coin)
            self.coins.add(coin)
            
        # Enemies
        for i in range(6):  # More enemies in final level
            enemy = Enemy(random.randint(100, SCREEN_WIDTH - 100), 
                         SCREEN_HEIGHT - 70)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
            
        # Goal
        goal = Goal(370, 10)
        self.all_sprites.add(goal)
        self.goals.add(goal)
    
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.player.jump()
                    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move_left()
        elif keys[pygame.K_RIGHT]:
            self.player.move_right()
        else:
            self.player.stop()
            
        self.all_sprites.update(self.platforms)
        
        # Check for coin collisions
        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        for coin in coin_hits:
            self.score += 10
            
        # Check for enemy collisions
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemy_hits:
            # If player is falling and hits enemy from above
            if self.player.vel_y > 0 and self.player.rect.bottom < enemy.rect.centery:
                enemy.kill()
                self.player.vel_y = JUMP_STRENGTH / 2  # Small bounce
                self.score += 100
            else:
                # Player gets hurt
                self.player.lives -= 1
                self.player.reset_position()
                if self.player.lives <= 0:
                    return "game_over"
                
        # Check if player reached the goal
        goal_hits = pygame.sprite.spritecollide(self.player, self.goals, False)
        if goal_hits:
            self.completed = True
            return "completed"
                
        return "playing"
    
    def draw(self, screen):
        # Different background colors based on world
        if self.level_number <= 3:
            screen.fill(SKY_BLUE)  # World 1 - Grass Land
        elif self.level_number <= 5:
            screen.fill((255, 220, 150))  # World 2 - Desert Hills
        elif self.level_number <= 7:
            screen.fill(LIGHT_BLUE)  # World 3 - Sky World
        else:
            screen.fill((200, 230, 255))  # World 4 - Ice Land
        
        # Draw clouds in the background for appropriate worlds
        if self.level_number <= 3 or self.level_number >= 6:
            for i in range(5):
                x = (i * 200 + pygame.time.get_ticks() // 100) % (SCREEN_WIDTH + 200) - 100
                y = 50 + i * 30
                pygame.draw.ellipse(screen, WHITE, (x, y, 100, 40))
                pygame.draw.ellipse(screen, WHITE, (x + 20, y - 20, 80, 40))
                pygame.draw.ellipse(screen, WHITE, (x + 40, y + 10, 60, 40))
        
        # Draw all sprites
        self.all_sprites.draw(screen)
        
        # Draw level number, score and lives
        font = pygame.font.SysFont(None, 36)
        level_text = font.render(f"Level: {self.level_number}", True, WHITE)
        screen.blit(level_text, (10, 10))
        
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 50))
        
        lives_text = font.render(f"Lives: {self.player.lives}", True, WHITE)
        screen.blit(lives_text, (10, 90))
        
        pygame.display.flip()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros 3-like Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.total_score = 0
        self.state = "overworld"  # "overworld", "level", "game_over", "victory"
        self.overworld = OverworldMap()
        self.current_level = None
        self.player_lives = 3
        self.game_completed = False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if self.state == "overworld":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.overworld.move("right")
                    elif event.key == pygame.K_LEFT:
                        self.overworld.move("left")
                    elif event.key == pygame.K_DOWN:
                        self.overworld.move("down")
                    elif event.key == pygame.K_UP:
                        self.overworld.move("up")
                    elif event.key == pygame.K_RETURN:
                        level_number = self.overworld.get_current_level()
                        self.current_level = Level(level_number, self.player_lives)
                        self.state = "level"
            elif self.state == "level":
                self.current_level.handle_events(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "overworld"
            elif self.state in ["game_over", "victory"]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()  # Reset game
                    elif event.key == pygame.K_q:
                        self.running = False
    
    def update(self):
        if self.state == "level":
            level_status = self.current_level.update()
            
            if level_status == "completed":
                # Add level score to total
                self.total_score += self.current_level.score
                self.player_lives = self.current_level.player.lives
                
                # Mark level as completed in overworld and unlock connected nodes
                self.overworld.complete_current_level()
                
                # Check if this was the final level
                if self.overworld.get_current_level() == 8:
                    self.state = "victory"
                    self.game_completed = True
                else:
                    self.state = "overworld"
                    
            elif level_status == "game_over":
                self.state = "game_over"
    
    def draw(self):
        if self.state == "overworld":
            self.screen.fill(LIGHT_BLUE)
            
            # Draw a simple background
            pygame.draw.rect(self.screen, (100, 200, 100), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
            
            # Draw title
            font = pygame.font.SysFont(None, 48)
            title_text = font.render("SUPER MARIO BROS 3", True, RED)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 20))
            
            # Draw world indicator
            current_world = self.overworld.nodes[self.overworld.current_node]["world"]
            world_text = font.render(f"WORLD {current_world}", True, BLUE)
            self.screen.blit(world_text, (SCREEN_WIDTH // 2 - world_text.get_width() // 2, 70))
            
            self.overworld.draw(self.screen)
            
            # Draw instructions and total score
            font = pygame.font.SysFont(None, 24)
            instructions = [
                "Use ARROWS to move between levels",
                "Press ENTER to start a level",
                "Press ESC in level to return to overworld",
                f"Total Score: {self.total_score}",
                f"Lives: {self.player_lives}"
            ]
            for i, line in enumerate(instructions):
                text = font.render(line, True, BLACK)
                self.screen.blit(text, (10, SCREEN_HEIGHT - 120 + i * 25))
                
        elif self.state == "level":
            self.current_level.draw(self.screen)
            
        elif self.state == "game_over":
            self.screen.fill(BLACK)
            font = pygame.font.SysFont(None, 72)
            game_over_text = font.render("GAME OVER", True, RED)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Final Score: {self.total_score}", True, WHITE)
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            
            restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
            
        elif self.state == "victory":
            self.screen.fill((0, 100, 0))
            font = pygame.font.SysFont(None, 72)
            victory_text = font.render("VICTORY!", True, YELLOW)
            self.screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Final Score: {self.total_score}", True, WHITE)
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            
            restart_text = font.render("Press R to Play Again or Q to Quit", True, WHITE)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
            
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
