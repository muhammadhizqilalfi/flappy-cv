class Pipe:
    def __init__(self, x, screen_height, gap_height, pygame, pipe_width = 78, pipe_height = 1080):
        self.x = x
        self.screen_height = screen_height
        self.pygame = pygame
        self.gap_height = gap_height
        self.gap_size = 200
        self.speed = 3
        self.passed = False
        self.pipe_width = pipe_width
        self.pipe_height = pipe_height
        self.top_pipe_rect = self.pygame.Rect(x, 0, pipe_width, gap_height - self.gap_size // 2)
        self.bottom_pipe_rect = self.pygame.Rect(x, gap_height + self.gap_size // 2, pipe_width,  screen_height - (gap_height + self.gap_size // 2))
    
    def update(self):
        self.x -= self.speed
        self.top_pipe_rect.x = self.x
        self.bottom_pipe_rect.x = self.x
    
    def draw(self, screen, pipe_img):
        scaled_pipe_img = self.pygame.transform.scale(pipe_img, (self.pipe_width, self.pipe_height))
        top_pipe = self.pygame.transform.flip(scaled_pipe_img, False, True)
        top_pipe_y = self.top_pipe_rect.height - self.pipe_height
        screen.blit(top_pipe, (self.x, top_pipe_y))
        screen.blit(scaled_pipe_img, (self.x, self.bottom_pipe_rect.y))
    
    def collide(self, bird):
        bird_mask = bird.get_mask()

        top_mask = self.pygame.mask.Mask((self.pipe_width, self.pipe_height))
        top_mask.fill()
        
        bottom_mask = self.pygame.mask.Mask((self.pipe_width, self.pipe_height))
        bottom_mask.fill()
        
        top_offset = (self.x - bird.x, (self.top_pipe_rect.height - self.pipe_height) - bird.y)
        bottom_offset = (self.x - bird.x, self.bottom_pipe_rect.y - bird.y)
        
        top_collision = bird_mask.overlap(top_mask, top_offset)
        bottom_collision = bird_mask.overlap(bottom_mask, bottom_offset)
        
        return top_collision or bottom_collision