import pygame
import sys
import random
import os
from lib.bird import Bird
from lib.pipe import Pipe
from lib.ground import Ground
from lib.button import Button
from lib.webcam import Webcam
from lib.sound import SoundManager

pygame.init()
pygame.mixer.init()

GLOBAL_SCREEN_WIDTH = 540
GLOBAL_SCREEN_HEIGHT = 1080
SCREEN_WIDTH = GLOBAL_SCREEN_WIDTH
SCREEN_HEIGHT = GLOBAL_SCREEN_HEIGHT

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Flappy Bird CV")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

GRASS_GREEN = (157, 227, 96)
GROUND_YELLOW = (228, 250, 145)
BIRD_RED = (202, 63, 30)

GRASS_DARK_GREEN = (134, 215, 68)
GROUND_DARK_YELLOW = (211, 244, 98)
BIRD_DARK_RED = (178, 49, 28)

PIPE_MIN_Y = 320
PIPE_MAX_Y = 860
PIPE_MIN_Y = max(200, PIPE_MIN_Y)
PIPE_MAX_Y = min(SCREEN_HEIGHT - 200, PIPE_MAX_Y)\

def load_font(font_path, font_name = "PixelifySans", font_style = "Regular"):
    return os.path.join(font_path, f"{font_name}-{font_style}.ttf")

def create_placeholder_sounds():
    sounds = {}
    jump_sound = pygame.mixer.Sound(buffer = bytes([0] * 44))
    sounds["beep"] = jump_sound
    sounds["button"] = jump_sound
    sounds["lose"] = jump_sound
    sounds["point"] = jump_sound
    sounds["backsound"] = jump_sound

    return sounds

def load_assets():
    assets = {}
    asset_path = "assets/images"

    sounds = {}
    sound_path = "assets/sounds"

    font_path = "assets/fonts"
    model_path = "assets/models"
    
    try:
        assets["bg"] = pygame.image.load(os.path.join(asset_path, "bg.png")).convert()
        assets["bg"] = pygame.transform.scale(assets["bg"], (SCREEN_WIDTH, SCREEN_HEIGHT))
        sounds["beep"] = pygame.mixer.Sound(os.path.join(sound_path, "beep.mp3"))
        sounds["button"] = pygame.mixer.Sound(os.path.join(sound_path, "button.mp3"))
        sounds["lose"] = pygame.mixer.Sound(os.path.join(sound_path, "lose.mp3"))
        sounds["point"] = pygame.mixer.Sound(os.path.join(sound_path, "point.mp3"))
        sounds["backsound"] = pygame.mixer.Sound(os.path.join(sound_path, "backsound.mp3"))
    except FileNotFoundError:
        print("Failed to load background image, using green background")

        assets["bg"] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        assets["bg"].fill((135, 206, 235))
        sounds = create_placeholder_sounds()
    
    bird_frames = []

    for i in range(1, 4):
        try:
            frame = pygame.image.load(os.path.join(asset_path, f"bird{i}.png")).convert_alpha()
            frame = pygame.transform.scale(frame, (50, 35))
            bird_frames.append(frame)
        except FileNotFoundError:
            print("Failed to load bird image animation")
    
    if not bird_frames:
        placeholder = pygame.Surface((50, 35), pygame.SRCALPHA)
        pygame.draw.ellipse(placeholder, YELLOW, (0, 0, 50, 35))
        pygame.draw.ellipse(placeholder, BLACK, (35, 10, 10, 10))
        pygame.draw.polygon(placeholder, RED, [(50, 17), (60, 12), (60, 22)])
        bird_frames = [placeholder]
    
    assets["bird_frames"] = bird_frames

    try:
        assets["pipe"] = pygame.image.load(os.path.join(asset_path, "pipe.png")).convert_alpha()
        assets["pipe"] = pygame.transform.scale(assets["pipe"], (80, 500))
    except FileNotFoundError:
        print("Failed to load pipe, creating pipe placeholder")

        assets["pipe"] = pygame.Surface((80, 500), pygame.SRCALPHA)
        pygame.draw.rect(assets["pipe"], GREEN, (0, 0, 80, 500))
        pygame.draw.rect(assets["pipe"], (0, 100, 0), (0, 0, 80, 500), 3)
    
    try:
        assets["ground"] = pygame.image.load(os.path.join(asset_path, "ground.png")).convert()
        assets["ground"] = pygame.transform.scale(assets["ground"], (SCREEN_WIDTH, 100))
    except FileNotFoundError:
        print("Failed to load pipe, creating pipe placeholder")

        assets["ground"] = pygame.Surface((SCREEN_WIDTH, 100))
        assets["ground"].fill((222, 184, 135))
    
    return assets, sounds, font_path, model_path

if __name__ == "__main__":
    assets, sounds, font_path, model_path = load_assets()
    clock = pygame.time.Clock()
    score_font, game_over_font, start_font, global_font = None, None, None, None
    webcam = Webcam(os.path.join(model_path, "haarcascade_frontalface_alt.xml"), GLOBAL_SCREEN_WIDTH, GLOBAL_SCREEN_HEIGHT, BIRD_RED, 2, 2, 15, pygame)
    use_webcam_bg = False
    webcam_init = webcam.init()
    sound_manager = SoundManager(sounds)

    if not webcam_init:
        print("Webcam not detected, using default background")
        use_webcam_bg = False
    else:
        use_webcam_bg = True
    
    try:
        score_font = pygame.font.Font(load_font(font_path, "PixelifySans", "Regular"), 32)
        game_over_font = pygame.font.Font(load_font(font_path, "PixelifySans", "Bold"), 56)
        start_font = pygame.font.Font(load_font(font_path, "PixelifySans", "Regular"), 32) 
        global_font = pygame.font.Font(load_font(font_path, "PixelifySans", "Regular"), 36) 
    except FileNotFoundError:
        score_font = pygame.font.SysFont("Arial", 32)
        game_over_font = pygame.font.SysFont("Arial", 56)
        start_font = pygame.font.SysFont("Arial", 32)
        global_font = pygame.font.SysFont("Arial", 36)
    
    def init_game():
        bird = Bird(100, SCREEN_HEIGHT // 2, assets["bird_frames"], pygame)
        ground = Ground(SCREEN_WIDTH, SCREEN_HEIGHT - 100, assets["ground"], pygame)
        pipes = []
        score = 0
        game_over = False
        game_started = False
        
        return bird, ground, pipes, score, game_over, game_started
    
    bird, ground, pipes, score, game_over, game_started = init_game()
    restart_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 60, "RESTART", GRASS_GREEN, GRASS_DARK_GREEN, global_font, pygame)
    start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 8, 200, 60, "START", GRASS_GREEN, GRASS_DARK_GREEN, start_font, pygame)
    quit_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 60, "QUIT", BIRD_RED, BIRD_DARK_RED, start_font, pygame)
    pipe_spawn_timer = 0
    pipe_spawn_interval = 1500
    running = True

    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not game_over:
                if not game_started:
                    start_button.check_hover(mouse_pos)
                    quit_button.check_hover(mouse_pos)

                    if start_button.is_clicked(mouse_pos, event):
                        sound_manager.play_timeout("button", volume = 0.7, loop = False, timeout = 1)
                        game_started = True
                    if quit_button.is_clicked(mouse_pos, event):
                        sound_manager.play_timeout("button", volume = 0.7, loop = False, timeout = 1)
                        running = False
            else:
                restart_button.check_hover(mouse_pos)

                if restart_button.is_clicked(mouse_pos, event):
                    sound_manager.play_timeout("button", volume = 0.7, loop = False, timeout = 1)
                    bird, ground, pipes, score, game_over, game_started = init_game()
        
        if not game_over and game_started:
            face_center = webcam.get_centroid()
            
            if face_center is not None:
                center_x, center_y = face_center
                game_height = SCREEN_HEIGHT
                bird_y = (center_y / webcam.webcam_height) * game_height
                bird_y = max(0, min(bird_y, SCREEN_HEIGHT))
                bird.set_position(int(bird_y))
        
        if not game_over and game_started:
            bird.update()
            ground.update()
            sound_manager.stop_all_except(["backsound", "beep", "button"])

            if current_time - pipe_spawn_timer > pipe_spawn_interval:
                gap_height = random.randint(PIPE_MIN_Y, PIPE_MAX_Y)
                pipes.append(Pipe(SCREEN_WIDTH, SCREEN_HEIGHT, gap_height, pygame))
                pipe_spawn_timer = current_time
            
            for pipe in pipes[:]:
                pipe.update()
                
                if not pipe.passed and pipe.x + 80 < bird.x:
                    pipe.passed = True
                    score += 1
                    sound_manager.play_timeout("beep", volume = 0.75, loop = False, timeout = 1)
                
                if pipe.x + 80 < 0:
                    pipes.remove(pipe)
            
            for pipe in pipes:
                if pipe.collide(bird):
                    game_over = True
            
            if ground.collide(bird):
                game_over = True
        
        if use_webcam_bg and webcam_init:
            webcam_bg = webcam.get_background()

            if webcam_bg is not None:
                screen.blit(webcam_bg, (0, 0))
            else:
                screen.blit(assets["bg"], (0, 0))
        else:
            screen.blit(assets["bg"], (0, 0))
        
        if game_started:
            for pipe in pipes:
                pipe.draw(screen, assets["pipe"])

        ground.draw(screen)
        bird.draw(screen)
        
        if game_started:
            score_text = global_font.render(f"Score: {score}", True, GROUND_DARK_YELLOW)
            screen.blit(score_text, (32, 16))
        
        if not game_started and not game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            title_text = game_over_font.render("FLAPPY BIRD CV", True, GROUND_DARK_YELLOW)
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
            
            instruction_text = global_font.render("Click START to play", True, GRASS_GREEN)
            screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))

            start_button.draw(screen, BLACK)
            quit_button.draw(screen, BLACK)

            sound_manager.stop_all_except(["backsound", "button"])
            sound_manager.play("backsound", loop = True)
        
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            game_over_text = game_over_font.render("GAME OVER", True, BIRD_RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
            
            final_score_text = global_font.render(f"Score: {score}", True, GROUND_DARK_YELLOW)
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))

            restart_button.draw(screen, BLACK)

            sound_manager.stop_all_except(["lose", "button"])
            sound_manager.play("lose")
        
        pygame.display.flip()
        clock.tick(60)
    
    webcam.destroy_all()
    pygame.quit()
    sys.exit()