
import pygame
import sys
import random
import os

pygame.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE =  (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)

# Game dynamics OBSTACLES = PIPE
GRAVITY = 0.8
JUMP_STRENGTH = -10
PIPE_SPEED = 3
PIPE_WIDTH = 50
PIPE_GAP = 115

MIN_PIPE_SPAWN_INTERVAL = 900
MAX_PIPE_SPAWN_INTERVAL = 1800

# SCREEN
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE, vsync = 1)
pygame.display.set_caption("Escape Earth!")
SPAWNPIPE = pygame.USEREVENT

# High score func
def load_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt",  "r") as f:
            try:
                return int(f.read())
            except ValueError:
                return 0
    else:
        return 0
def save_high_score(score):
    with open("highscore.txt",  "w") as f:
        f.write(str(score))
high_score = load_high_score()

def create_cityscape_surface(width, height):
    surface = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
    surface.fill((0, 0, 0, 0))
    building_color = (50, 50, 50)
    num_buildings = 8
    building_width = width // num_buildings
    for i in range(num_buildings):
        b_height = random.randint(height // 2, height)
        x_pos = i * building_width + random.randint(0, building_width // 2)
        y_pos = height - b_height
        pygame.draw.rect(surface, building_color, (x_pos, y_pos, building_width, b_height))
    return surface

def create_star_field_surface(width, height, num_stars=50):
    surface = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
    surface.fill((0, 0, 0, 0))
    for _ in range(num_stars):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        radius = random.randint(1, 2)
        pygame.draw.circle(surface, YELLOW, (x, y), radius)
    return surface

def create_ufo_sprite():
    sprite = pygame.Surface((30, 30), pygame.SRCALPHA).convert_alpha()
    pygame.draw.ellipse(sprite, (192, 192, 192), (0, 10, 30, 15))
    pygame.draw.ellipse(sprite, (220, 220, 220), (8, 0, 14, 14))
    return sprite

# Sprite template
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_ufo_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = 0

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += self.velocity

    def flap(self):
        self.velocity = JUMP_STRENGTH

# OBSTACLE DEFINITION

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = PIPE_WIDTH
        self.gap = PIPE_GAP
        self.set_height()
        self.passed = False

    def set_height(self):
        self.gap_y = random.randint(self.gap + 20, SCREEN_HEIGHT - self.gap - 20)
        self.top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y - self.gap // 2)
        self.bottom_rect = pygame.Rect(self.x, self.gap_y + self.gap // 2, self.width, SCREEN_HEIGHT - (self.gap_y + self.gap // 2))

    def update(self, speed):
        self.x -= speed
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.top_rect)
        pygame.draw.rect(surface, GRAY, self.bottom_rect)

# Hitting obstacles func
def check_collision(bird, pipes):
    for pipe in pipes:
        if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
            return True
    if bird.rect.top <= 0 or bird.rect.bottom >= SCREEN_HEIGHT:
        return True
    return False

def show_menu():
    menu_running = True
    clock = pygame.time.Clock()
    # Fonts for title and how to play
    title_font = pygame.font.SysFont("Arial", 48)
    text_font = pygame.font.SysFont("Arial", 24)

    # Button rect
    button_rect = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50), (200, 50))
    button_color = GREEN

    while menu_running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Spacebar to start
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    menu_running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    menu_running = False

        #Menu for text + background
        screen.fill(BLACK)

        title_text = title_font.render("Escape Earth!", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title_text, title_rect)

        instruction_text = text_font.render("Press Space to Begin", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(instruction_text, instruction_rect)

        pygame.draw.rect(screen, button_color, button_rect)
        button_text = text_font.render("START", True, BLACK)
        button_text_rect = button_text.get_rect(center=(button_rect.center))
        screen.blit(button_text, button_text_rect)

        pygame.display.flip()


def show_game_over():
    game_over_running = True
    clock = pygame.time.Clock()
    game_over_font = pygame.font.SysFont("Arial", 48)
    button_font = pygame.font.SysFont("Arial", 24)

    # Play again / quit btn
    play_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
    quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)

    while game_over_running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "play"
                elif event.key == pygame.K_ESCAPE:
                    return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_button_rect.collidepoint(mouse_pos):
                    return "play"
                if quit_button_rect.collidepoint(mouse_pos):
                    return "quit"

        screen.fill(BLACK)
        game_over_text = game_over_font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(game_over_text, game_over_rect)

        pygame.draw.rect(screen, GREEN, play_button_rect)
        play_text = button_font.render("PLAY AGAIN", True, BLACK)
        play_text_rect = play_text.get_rect(center=play_button_rect.center)
        screen.blit(play_text, play_text_rect)

        pygame.draw.rect(screen, GREEN, quit_button_rect)
        quit_text = button_font.render("QUIT", True, BLACK)
        quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)
        screen.blit(quit_text, quit_text_rect)

        pygame.display.flip()

# Loop
def main():
    clock = pygame.time.Clock()

    bird = Bird(100, SCREEN_HEIGHT // 2)
    bird_group = pygame.sprite.GroupSingle(bird)
    pipes = []
    score = 0
    difficulty_level = 0
    current_pipe_speed = PIPE_SPEED
    score_font = pygame.font.SysFont("Arial", 24)

    city_height = 100
    city_surface = create_cityscape_surface(SCREEN_WIDTH, city_height)
    star_field_height = 150
    star_field_surface = create_star_field_surface(SCREEN_WIDTH, star_field_height, num_stars=50)
    star_field_top = 150
    background_scroll = 0
    star_scroll = 0
    city_scroll_speed = 1
    star_scroll_speed = 0.3
    pygame.time.set_timer(SPAWNPIPE, random.randint(MIN_PIPE_SPAWN_INTERVAL, MAX_PIPE_SPAWN_INTERVAL))
    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.flap()
            if event.type == pygame.MOUSEBUTTONDOWN:
                bird.flap()
            if event.type == SPAWNPIPE:
                pipes.append(Pipe(SCREEN_WIDTH))
                pygame.time.set_timer(SPAWNPIPE, random.randint(MIN_PIPE_SPAWN_INTERVAL, MAX_PIPE_SPAWN_INTERVAL))

        bird_group.update()
        for pipe in pipes:
            pipe.update(current_pipe_speed)

        pipes[:] = [pipe for pipe in pipes if pipe.x + pipe.width > 0]

        # Checks if passes pipe to update score
        for pipe in pipes:
            if not pipe.passed and pipe.x + pipe.width < bird.rect.left:
                pipe.passed  = True
                score += 1
                if score // 5  > difficulty_level:
                    difficulty_level = score // 5
                    current_pipe_speed += 0.5

        if check_collision(bird, pipes):
            print("Good run")
            running = False

        background_scroll = (background_scroll + city_scroll_speed) % SCREEN_WIDTH
        star_scroll = (star_scroll + star_scroll_speed) % SCREEN_WIDTH

        screen.fill(BLACK)
        screen.blit(star_field_surface, (-star_scroll, star_field_top))
        screen.blit(star_field_surface, (SCREEN_WIDTH - background_scroll, SCREEN_HEIGHT - city_height))

        screen.blit(city_surface, (-background_scroll, SCREEN_HEIGHT - city_height))
        screen.blit(city_surface, (SCREEN_WIDTH - background_scroll, SCREEN_HEIGHT - city_height))

        bird_group.draw(screen)
        for pipe in pipes:
            pipe.draw(screen)
        score_text = score_font.render("Score: " + str(score), True, GREEN)
        screen.blit(score_text, (10, 10))
        high_score_text = score_font.render("High Score: " + str(high_score), True, GREEN)
        screen.blit(high_score_text, (10, 40))
        pygame.display.flip()
    return score

if __name__ == "__main__":
    show_menu()
    while True:
        final_score = main()
        if final_score > high_score:
            high_score = final_score
            save_high_score(high_score)
        result = show_game_over()
        if result == "play":
            continue
        else:
            pygame.quit()
            sys.exit()
