class Bird:
    def __init__(self, x, y, frames, pygame):
        self.x = x
        self.y = y
        self.pygame = pygame
        self.frames = frames
        self.current_frame = 0
        self.animation_speed = 0.2
        self.animation_counter = 0
        self.rect = self.pygame.Rect(x, y, 50, 35)
        self.target_y = y
        self.current_y = y
        self.position_transition_speed = 0.1
        self.angle = 0
        self.target_angle = 0
        self.angle_transition_speed = 0.2
        self.last_y = y
        self.movement_threshold = 2
    
    def set_position(self, new_target_y):
        self.target_y = new_target_y
    
    def update(self):
        position_diff = self.target_y - self.current_y

        if abs(position_diff) > 0.5:
            self.current_y += position_diff * self.position_transition_speed
        else:
            self.current_y = self.target_y

        self.y = self.current_y
        y_movement = self.current_y - self.last_y

        if y_movement < -self.movement_threshold:
            self.target_angle = -30
        elif y_movement > self.movement_threshold:
            self.target_angle = 30
        else:
            self.target_angle = 0
        
        angle_diff = self.target_angle - self.angle

        if abs(angle_diff) > 0.1:
            self.angle += angle_diff * self.angle_transition_speed
        else:
            self.angle = self.target_angle

        self.angle = max(-30, min(self.angle, 30))
        self.animation_counter += self.animation_speed

        if self.animation_counter >= 1:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.animation_counter = 0
        
        self.last_y = self.current_y
        self.rect.y = self.y
    
    def draw(self, screen):
        rotated_bird = self.pygame.transform.rotate(self.frames[self.current_frame], -self.angle)
        new_rect = rotated_bird.get_rect(center = self.frames[self.current_frame].get_rect(topleft = (self.x, self.y)).center)
        screen.blit(rotated_bird, new_rect.topleft)
    
    def get_mask(self):
        return self.pygame.mask.from_surface(self.frames[self.current_frame])