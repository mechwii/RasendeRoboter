import pygame
import random
import os

class MenuWindow:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)

        # Load and scale background image
        self.background = self.load_scaled_image(os.path.join("img", "accueil.png"), (self.width, self.height))

        # Load circle images
        self.circle_images = {
            "r": pygame.image.load(os.path.join("img", "r_r.png")),
            "b": pygame.image.load(os.path.join("img", "r_b.png")),
            "j": pygame.image.load(os.path.join("img", "r_j.png")),
            "v": pygame.image.load(os.path.join("img", "r_v.png")),
        }

        self.game_mode_images = {
            "mode_1": pygame.image.load(os.path.join("img", "mode_1.png")),
            "mode_2": pygame.image.load(os.path.join("img", "mode_2.png")),
            "mode_3": pygame.image.load(os.path.join("img", "mode_3.png")),
        }

        # Initialize bouncing circles with images
        self.circles = [
            {
                "position": [random.randint(50, width - 50), random.randint(50, height - 50)],
                "velocity": [random.choice([-3, 3]), random.choice([-3, 3])],
                "image": random.choice(list(self.circle_images.values())),
                "angle": 0,  # Initial rotation angle
                "rotation_speed": random.uniform(-2, 2),  # Speed of rotation
            }
            for _ in range(8)  # Number of moving circles
        ]

    def load_scaled_image(self, image_path, target_size):
        """
        Load an image and scale it to fit the target size while maintaining aspect ratio.
        """
        image = pygame.image.load(image_path)
        image_rect = image.get_rect()
        target_width, target_height = target_size

        # Calculate scale factors for maintaining aspect ratio
        scale_x = target_width / image_rect.width
        scale_y = target_height / image_rect.height
        scale_factor = min(scale_x, scale_y)

        # Calculate new dimensions
        new_width = int(image_rect.width * scale_factor)
        new_height = int(image_rect.height * scale_factor)

        # Scale the image
        return pygame.transform.smoothscale(image, (new_width, new_height))

    def update_circles(self):
        """
        Update positions of circles, handle bouncing off walls, and rotate them slightly.
        """
        for circle in self.circles:
            # Update position
            circle["position"][0] += circle["velocity"][0]
            circle["position"][1] += circle["velocity"][1]

            # Bounce off walls
            if circle["position"][0] <= 0 or circle["position"][0] + circle["image"].get_width() >= self.width:
                circle["velocity"][0] *= -1
            if circle["position"][1] <= 0 or circle["position"][1] + circle["image"].get_height() >= self.height:
                circle["velocity"][1] *= -1

            # Update rotation angle
            circle["angle"] = (circle["angle"] + circle["rotation_speed"]) % 360

    def draw_circles(self):
        """
        Draw bouncing and rotating circles with images on the screen.
        """
        for circle in self.circles:
            rotated_image = pygame.transform.rotate(circle["image"], circle["angle"])
            image_rect = rotated_image.get_rect(center=(circle["position"][0], circle["position"][1]))
            self.screen.blit(rotated_image, image_rect.topleft)

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
        Displays the main menu with a stylized button, animated images, and a scaled background.
        """
        running = True
        while running:
            mouse_position = pygame.mouse.get_pos()

            # Update circle positions and rotations
            self.update_circles()

            # Draw background image centered
            self.screen.fill((0, 0, 0))  # Black background for padding
            bg_rect = self.background.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(self.background, bg_rect.topleft)

            # Draw bouncing and rotating circles
            self.draw_circles()

            # Render Play button
            button_position = (self.width // 2 - 150, self.height // 2 + 100)  # Lowered button
            play_hovered = self.render_button(
                "Play",
                button_position,
                (13, 128, 200),  # Base color (0D80C8)
                (20, 150, 220),  # Hover color (lighter shade)
                mouse_position,
            )

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_hovered:
                        return "GAME_MODE"  # Transition to game state

    def select_game_mode_with_graphics(self):
        """
        Displays the game mode selection screen with graphics, rectangles, and footer.
        """
        running = True
        selected_mode = None  # Default to None until a mode is selected

        while running:
            self.screen.fill((255, 255, 255))  # Background color

            # Render the title
            title = self.font.render("Choisissez le mode", True, (0, 0, 0))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

            # Define dimensions for rectangles and calculate positions dynamically
            rect_width, rect_height = 200, 250
            spacing = 50  # Space between rectangles
            total_width = 3 * rect_width + 2 * spacing  # Total width of all rectangles and spaces
            start_x = (self.width - total_width) // 2  # Starting x-coordinate for the first rectangle
            rect_y = self.height // 2 - rect_height // 2  # Center rectangles vertically

            # Mode texts
            mode_texts = ["Humain vs Humain", "Humain vs IA", "IA vs IA"]
            mode_keys = ["mode_1", "mode_2", "mode_3"]

            # Draw rectangles, images, and text
            mouse_position = pygame.mouse.get_pos()

            for i, mode_key in enumerate(mode_keys):
                rect_x = start_x + i * (rect_width + spacing)

                # Draw gray rectangle
                rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
                pygame.draw.rect(self.screen, (200, 200, 200), rect)  # Gray background

                # Draw hover effect (blue border when mouse is over)
                if rect.collidepoint(mouse_position):
                    pygame.draw.rect(self.screen, (0, 128, 255), rect, 3)  # Blue border for hover

                # Draw the image centered within the rectangle
                image = self.game_mode_images[mode_key]
                image_rect = image.get_rect(center=(rect_x + rect_width // 2, rect_y + 100))
                self.screen.blit(image, image_rect.topleft)

                # Render the mode text below the image
                text = self.small_font.render(mode_texts[i], True, (0, 0, 0))
                text_rect = text.get_rect(center=(rect_x + rect_width // 2, rect_y + 200))
                self.screen.blit(text, text_rect)

            # Render footer with blue background
            footer_height = 50
            pygame.draw.rect(self.screen, (13, 128, 200),
                             (0, self.height - footer_height, self.width, footer_height))  # Blue background
            footer_text = self.small_font.render("Ce jeu est proposé dans le cadre de l'UE IA41", True,
                                                 (255, 255, 255))  # White text
            footer_text_rect = footer_text.get_rect(center=(self.width // 2, self.height - footer_height // 2))
            self.screen.blit(footer_text, footer_text_rect)

            pygame.display.flip()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                # Detect clicks and select mode
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button clicked
                    for i, mode_key in enumerate(mode_keys):
                        rect_x = start_x + i * (rect_width + spacing)
                        rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)

                        if rect.collidepoint(event.pos):  # Check if click is inside the rectangle
                            selected_mode = mode_key

            # Return the selected mode
            if selected_mode:
                if selected_mode == "mode_1":
                    print("1")
                    return "HUMAN_VS_HUMAN"
                elif selected_mode == "mode_2":
                    print("2")
                    return "HUMAN_VS_AI"
                elif selected_mode == "mode_3":
                    print("3")
                    return "AI_VS_AI"

    def select_ai(self, prompt):
        """
        Displays a menu to select an AI type.
        :param prompt: Text to display as the selection prompt.
        :return: The chosen AI type as a string.
        """
        running = True

        while running:
            self.screen.fill((255, 255, 255))  # Background color

            # Render the prompt
            title = self.font.render(prompt, True, (0, 0, 0))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

            # Define button dimensions and positions
            button_width, button_height = 500, 60
            spacing = 20
            total_height = 3 * button_height + 2 * spacing  # Total height of all buttons and spaces
            start_y = (self.height // 2 - total_height // 2)  # Starting y-coordinate for the first button
            button_x = (self.width // 2 - button_width // 2)

            # Define button labels and AI types
            ai_options = [
                ("Recherche en largeur", "BFS"),
                ("A*", "A*")
            ]

            # Draw buttons
            mouse_position = pygame.mouse.get_pos()
            buttons = []  # Store button rectangles and associated AI types

            for i, (label, ai_type) in enumerate(ai_options):
                button_y = start_y + i * (button_height + spacing)
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                buttons.append((button_rect, ai_type))  # Add button rect and AI type to list

                # Draw button background
                pygame.draw.rect(self.screen, (200, 200, 200), button_rect)  # Gray button

                # Draw hover effect
                if button_rect.collidepoint(mouse_position):
                    pygame.draw.rect(self.screen, (0, 128, 255), button_rect, 3)  # Blue border

                # Render button label
                label_surface = self.font.render(label, True, (0, 0, 0))
                label_rect = label_surface.get_rect(center=button_rect.center)
                self.screen.blit(label_surface, label_rect)

            # Render footer with blue background
            footer_height = 50
            pygame.draw.rect(self.screen, (13, 128, 200),
                             (0, self.height - footer_height, self.width, footer_height))  # Blue background
            footer_text = self.small_font.render("Ce jeu est proposé dans le cadre de l'UE IA41", True,
                                                 (255, 255, 255))  # White text
            footer_text_rect = footer_text.get_rect(center=(self.width // 2, self.height - footer_height // 2))
            self.screen.blit(footer_text, footer_text_rect)

            pygame.display.flip()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button clicked
                    for button_rect, ai_type in buttons:
                        if button_rect.collidepoint(event.pos):  # Check if click is inside a button
                            return ai_type  # Return the selected AI type


    def select_target_number(self, max_targets):
        """
        Displays the target selection screen in the same style with footer.
        :param max_targets: Maximum number of targets to choose from.
        :return: The selected number of targets.
        """
        running = True

        while running:
            self.screen.fill((255, 255, 255))  # Background color

            # Render the prompt
            title = self.font.render("Choisissez le nombre de cibles", True, (0, 0, 0))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

            # Define button dimensions and positions
            button_width, button_height = 500 // max_targets, 60
            spacing = 20
            total_width = max_targets * button_width + (
                        max_targets - 1) * spacing  # Total width of all buttons and spaces
            start_x = (self.width - total_width) // 2  # Starting x-coordinate for the first button
            button_y = self.height // 2 - button_height // 2  # Center buttons vertically

            # Create buttons for each target number
            buttons = []
            for i in range(1, max_targets + 1):
                button_x = start_x + (i - 1) * (button_width + spacing)
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                buttons.append((button_rect, i))  # Store button rect and target number

                # Draw button background
                pygame.draw.rect(self.screen, (200, 200, 200), button_rect)  # Gray button

                # Draw button label
                label_surface = self.font.render(str(i), True, (0, 0, 0))
                label_rect = label_surface.get_rect(center=button_rect.center)
                self.screen.blit(label_surface, label_rect)

            # Hover effect
            mouse_position = pygame.mouse.get_pos()
            for button_rect, _ in buttons:
                if button_rect.collidepoint(mouse_position):
                    pygame.draw.rect(self.screen, (0, 128, 255), button_rect, 3)  # Blue border for hover

            # Render footer with blue background
            footer_height = 50
            pygame.draw.rect(self.screen, (13, 128, 200),
                             (0, self.height - footer_height, self.width, footer_height))  # Blue background
            footer_text = self.small_font.render("Ce jeu est proposé dans le cadre de l'UE IA41", True,
                                                 (255, 255, 255))  # White text
            footer_text_rect = footer_text.get_rect(center=(self.width // 2, self.height - footer_height // 2))
            self.screen.blit(footer_text, footer_text_rect)

            pygame.display.flip()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button clicked
                    for button_rect, target_number in buttons:
                        if button_rect.collidepoint(event.pos):  # Check if click is inside a button
                            return target_number  # Return the selected number of targets

