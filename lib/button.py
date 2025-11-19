class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font, pygame, 

        # Border radius         
        radius=20,

        # Border normal
        border_color=(0,0,0),
        border_width=3,

        # Border 3D
        shadow_offset=6,
        shadow_color=(20,20,20)
    ):
        self.pygame = pygame
        self.font = font
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

        self.radius = radius
        self.border_color = border_color
        self.border_width = border_width

        # 3D properties
        self.shadow_offset = shadow_offset
        self.shadow_color = shadow_color
    
    def draw(self, screen, text_color):

        # Color change on hover
        color = self.hover_color if self.is_hovered else self.color

        shadow_rect = self.rect.move(self.shadow_offset, self.shadow_offset)
        self.pygame.draw.rect(
            screen,
            self.shadow_color,
            shadow_rect,
            border_radius=self.radius
        )

        self.pygame.draw.rect(
            screen,
            color,
            self.rect,
            border_radius=self.radius
        )

        if self.border_width > 0:
            self.pygame.draw.rect(
                screen,
                self.border_color,
                self.rect,
                width=self.border_width,
                border_radius=self.radius
            )
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
    
    def is_clicked(self, pos, event):
        return (
            event.type == self.pygame.MOUSEBUTTONDOWN and
            event.button == 1 and
            self.rect.collidepoint(pos)
        )
