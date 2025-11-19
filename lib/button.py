class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font, pygame):
        self.pygame = pygame
        self.font = font
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def draw(self, screen, main_color):
        color = self.hover_color if self.is_hovered else self.color
        self.pygame.draw.rect(screen, color, self.rect)
        self.pygame.draw.rect(screen, main_color, self.rect, 3)
        text_surface = self.font.render(self.text, True, main_color)
        text_rect = text_surface.get_rect(center = self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
    
    def is_clicked(self, pos, event):
        if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        
        return False