import pygame

class MenuWindow:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.font = pygame.font.Font(None, 48)

    def render_button(self, text, position, base_color, hover_color, mouse_position):
        """
        Render a button with hover effect.
        """
        button_rect = pygame.Rect(position[0], position[1], 300, 60)  # Fixed button size
        is_hovered = button_rect.collidepoint(mouse_position)

        # Set button color based on hover status
        color = hover_color if is_hovered else base_color

        # Draw button rectangle
        pygame.draw.rect(self.screen, color, button_rect, border_radius=10)

        # Render text on button
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)

        return is_hovered  # Return hover status for action handling

    def show_menu(self):
        """
        Displays the main menu with a stylized button.
        """
        running = True
        while running:
            mouse_position = pygame.mouse.get_pos()

            # Fill screen with background color
            self.screen.fill((50, 50, 50))  # Dark gray background

            # Render title
            title = self.font.render("Rasende Roboter", True, (255, 255, 255))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 4))

            # Render buttons
            play_hovered = self.render_button("Play", (self.width // 2 - 150, self.height // 2), (100, 100, 255),
                                              (150, 150, 255), mouse_position)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_hovered:
                        return "GAME"  # Transition to game state

    def show_rules(self):
        """
        Displays the rules of the game.
        """
        self.screen.fill((255, 255, 255))
        rules = [
            "Rules:",
            "1. Select a robot to move.",
            "2. Navigate the robot to its target.",
            "3. The first player to solve a target wins.",
            "4. Game ends when all targets are solved.",
            "",
            "Press any key to return to the menu."
        ]

        y_offset = self.height // 4
        for line in rules:
            text = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(text, (self.width // 2 - text.get_width() // 2, y_offset))
            y_offset += 40

        pygame.display.flip()
        return "RULES"

    def select_game_mode(self):
        """
        Displays the game mode selection screen.
        """
        self.screen.fill((255, 255, 255))
        modes = [
            "Select Game Mode:",
            "1. Human vs Human",
            "2. Human vs AI",
            "3. AI vs AI"
        ]

        y_offset = self.height // 4
        for line in modes:
            text = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(text, (self.width // 2 - text.get_width() // 2, y_offset))
            y_offset += 50

        pygame.display.flip()
        return "GAME_MODE"

    def select_target_number(self, max_targets):
        """
        Displays the target selection screen.
        """
        self.screen.fill((255, 255, 255))
        prompt = f"Enter the number of targets (1-{max_targets}):"
        text = self.font.render(prompt, True, (0, 0, 0))
        self.screen.blit(text, (self.width // 2 - text.get_width() // 2, self.height // 2))
        pygame.display.flip()

        input_number = ""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and input_number.isdigit():
                        target_count = int(input_number)
                        if 1 <= target_count <= max_targets:
                            return target_count
                    elif event.key == pygame.K_BACKSPACE:
                        input_number = input_number[:-1]
                    else:
                        input_number += event.unicode

            # Update display with user input
            self.screen.fill((255, 255, 255))
            self.screen.blit(text, (self.width // 2 - text.get_width() // 2, self.height // 2))
            input_display = self.font.render(input_number, True, (0, 0, 0))
            self.screen.blit(input_display, (self.width // 2 - input_display.get_width() // 2, self.height // 2 + 50))
            pygame.display.flip()
