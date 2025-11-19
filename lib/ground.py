class Ground:
    def __init__(self, x, y, ground_img, pygame):
        self.x = x
        self.y = y
        self.pygame = pygame
        self.x1 = 0
        self.x2 = self.x
        self.speed = 3
        self.image = ground_img
        self.rect = self.pygame.Rect(0, y, self.x, 100)
    
    def update(self):
        self.x1 -= self.speed
        self.x2 -= self.speed
        
        if self.x1 + self.x < 0:
            self.x1 = self.x2 + self.x
        
        if self.x2 + self.x < 0:
            self.x2 = self.x1 + self.x
    
    def draw(self, screen):
        screen.blit(self.image, (self.x1, self.y))
        screen.blit(self.image, (self.x2, self.y))
    
    def collide(self, bird):
        return bird.rect.bottom >= self.rect.top