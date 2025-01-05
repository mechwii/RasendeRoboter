import pygame


class GameWindow:
    WHITE = (255, 255, 255)  # White
    LIGHT_GRAY = (200, 200, 200)  # Light Gray
    BLACK = (0, 0, 0)  # Black

    def __init__(self, width, height, cell_size, margin_y, margin_x):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Rasende Roboter")
        self.running = True

        # Board size and centering
        self.cell_size = cell_size
        self.margin_x = margin_x
        self.margin_y = margin_y

        self.player_name = ""

        self.robot_colors = {
            "Re": (255, 0, 0),  # Red
            "Bl": (0, 0, 255),  # Blue
            "Gr": (0, 255, 0),  # Green
            "Ye": (255, 255, 0)  # Yellow
        }
        self.robot_images = {
            "Re": pygame.image.load("img/r_r.png"),  # Robot rouge
            "Bl": pygame.image.load("img/r_b.png"),  # Robot bleu
            "Gr": pygame.image.load("img/r_v.png"),  # Robot vert
            "Ye": pygame.image.load("img/r_j.png"),  # Robot jaune
        }

        # Charger les images des cibles
        self.target_images = {
            "Re": pygame.image.load("img/o_r.png"),  # Cible rouge
            "Bl": pygame.image.load("img/o_b.png"),  # Cible bleue
            "Gr": pygame.image.load("img/o_v.png"),  # Cible verte
            "Ye": pygame.image.load("img/o_j.png"),  # Cible jaune
        }

    def get_target_color(self, color):
        if color == "Re" :
            return 255, 0, 0
        if color == "Bl" :
            return 0, 0, 255
        if color == "Gr" :
            return 0, 255,0
        if color == "Ye" :
            return 255, 255, 0
        return 0, 0, 0

    def render_text(self, text, position, color=(0, 0, 0), font_size=24):
        """
        Render text at a given position.
        """
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, position)

    def handle_events(self):
        """
        Handles Pygame events like quitting the game.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def draw_movement_cross(self, robot_color, direction, position):
        """
        Draws a small cross showing the direction of movement.
        """
        center_y, center_x = position
        color = self.robot_colors.get(robot_color, self.BLACK)  # Default to black if unknown

        # Define line length for the history cross
        line_length = 10

        if direction == "up":
            pygame.draw.line(self.screen, color, (center_y, center_x), (center_y, center_x - line_length), 3)
        elif direction == "down":
            pygame.draw.line(self.screen, color, (center_y, center_x), (center_y, center_x + line_length), 3)
        elif direction == "left":
            pygame.draw.line(self.screen, color, (center_y, center_x), (center_y - line_length, center_x), 3)
        elif direction == "right":
            pygame.draw.line(self.screen, color, (center_y, center_x), (center_y + line_length, center_x), 3)

    def render_moves_history(self, player):
        """
        Renders a visual history of moves at the bottom of the screen.
        """
        history_start_y = self.screen.get_height() - 100  # Adjust this value for the height of the history section
        max_moves_to_display = 10  # Limit the number of moves shown

        # Take the last `max_moves_to_display` moves
        moves_to_display = player.moves[-max_moves_to_display:]

        # Define spacing for the moves
        spacing_x = 50  # Horizontal space between each move
        start_x = 16 * self.cell_size + self.margin_x  # Starting x-coordinate for the first move

        for i, move in enumerate(moves_to_display):
            robot_color, direction, _ = move
            center_x = start_x + i * spacing_x
            center_y = history_start_y + 50  # Center the cross vertically in the history area

            # Draw the movement cross
            self.draw_movement_cross(robot_color, direction, (center_x, center_y))

            # Draw the direction label below the cross
            self.render_text(direction.capitalize(), (center_x - 10, center_y + 20),
                             color=self.robot_colors.get(robot_color, self.BLACK), font_size=16)


    def draw_target(self, target):
        position = target['position']
        y, x = position
        target_image = self.target_images.get(target['color'])
        if target_image:
            # Redimensionner l'image pour s'adapter à la taille de la cellule
            scaled_image = pygame.transform.scale(target_image, (self.cell_size, self.cell_size))

            rect_y = self.margin_y + x * self.cell_size
            rect_x = self.margin_x + y * self.cell_size

            # Dessiner l'image de la cible
            self.screen.blit(scaled_image, (rect_y, rect_x))

    def draw_robot(self, board, player):
        for robot in board.robots:
            # Récupérer la couleur et la position du robot
            robot_image = self.robot_images.get(robot["color"])
            if robot_image:
                # Redimensionner l'image pour s'adapter à la taille de la cellule
                scaled_image = pygame.transform.scale(robot_image, (self.cell_size, self.cell_size))

                robot_y, robot_x = robot["position"]
                rect_x = self.margin_x + robot_y * self.cell_size
                rect_y = self.margin_y + robot_x * self.cell_size

                # Dessiner l'image du robot
                self.screen.blit(scaled_image, (rect_y, rect_x))

        self.render_moves_history(player)

    def update_display(self, board, player):
        """
        Renders the board, walls, robots, and updates the display.
        """
        self.screen.fill(self.WHITE)
        self.render_text(f"{player.name}: {len(player.moves)} moves         Score: {player.score}", (10, 10))


        for y in range(board.BOARD_SIZE):  # Rows

            for x in range(board.BOARD_SIZE):  # Columns
                cell = board.board[y][x]

                # Calculate cell position with margins
                rect_x = self.margin_x + y * self.cell_size  # Column affects horizontal position
                rect_y = self.margin_y + x * self.cell_size  # Row affects vertical position

                rect = pygame.Rect(rect_y, rect_x, self.cell_size, self.cell_size)

                # Draw the cell
                pygame.draw.rect(self.screen, self.WHITE, rect)  # Cell background
                pygame.draw.rect(self.screen, self.LIGHT_GRAY, rect, 1)  # Grid lines

                # Draw walls in the cell
                if "T" in cell["walls"]:  # Top wall
                    pygame.draw.line(self.screen, self.BLACK, (rect_y, rect_x), (rect_y + self.cell_size, rect_x), 4)
                if "B" in cell["walls"]:  # Bottom wall
                    pygame.draw.line(self.screen, self.BLACK, (rect_y, rect_x + self.cell_size),
                                     (rect_y + self.cell_size, rect_x + self.cell_size), 8)
                if "L" in cell["walls"]:  # Left wall
                    pygame.draw.line(self.screen, self.BLACK, (rect_y, rect_x), (rect_y, rect_x + self.cell_size), 4)
                if "R" in cell["walls"]:  # Right wall
                    pygame.draw.line(self.screen, self.BLACK, (rect_y + self.cell_size, rect_x),
                                     (rect_y + self.cell_size, rect_x + self.cell_size), 8)



                # Draw middle cells
                if cell["type"] == "M":
                    pygame.draw.rect(self.screen, self.BLACK, rect)

        self.draw_target(board.get_current_target() )
        self.draw_robot(board,player)
        self.render_text("Reset", (16 * self.cell_size / 2  + self.margin_x - 45, 16 * self.cell_size / 2 + self.margin_y + 20), color=self.WHITE)

        pygame.display.flip()  # Update the display

    def show_popup(self, winner_name, num_moves):
        """
        Displays a modern popup message announcing the winner of the turn.
        :param winner_name: Name of the winning player.
        :param num_moves: Number of moves the winner used.
        """
        popup_width, popup_height = 400, 250
        popup_x = (self.screen.get_width() - popup_width) // 2
        popup_y = (self.screen.get_height() - popup_height) // 2

        # Popup rectangle
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        # Background with rounded corners
        pygame.draw.rect(self.screen, (50, 50, 50), popup_rect, border_radius=20)  # Dark gray background
        pygame.draw.rect(self.screen, (0, 128, 255), popup_rect.inflate(-8, -8), 2, border_radius=20)  # Blue border

        # Add a line separator
        line_y = popup_y + popup_height // 2
        pygame.draw.line(self.screen, (200, 200, 200), (popup_x + 20, line_y), (popup_x + popup_width - 20, line_y), 2)

        # Title text
        font_title = pygame.font.Font(None, 48)
        title_text = font_title.render(" Tour Gagné ! ", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(popup_x + popup_width // 2, popup_y + 50))
        self.screen.blit(title_text, title_rect.topleft)

        # Winner's name and number of moves
        font_body = pygame.font.Font(None, 36)
        winner_text = font_body.render(f"Joueur : {winner_name}", True, (255, 255, 255))
        moves_text = font_body.render(f"Nombre de coups : {num_moves}", True, (255, 255, 255))

        winner_rect = winner_text.get_rect(center=(popup_x + popup_width // 2, line_y + 30))
        moves_rect = moves_text.get_rect(center=(popup_x + popup_width // 2, line_y + 80))

        self.screen.blit(winner_text, winner_rect.topleft)
        self.screen.blit(moves_text, moves_rect.topleft)

        # Display everything
        pygame.display.flip()

        # Wait for a short duration
        pygame.time.wait(3000)  # 3 seconds

    def show_end_screen(self, players):
        """
        Displays the end screen showing the players' scores in descending order with modern aesthetics.
        :param players: List of player objects with their scores.
        """
        # Sort players by score in descending order
        sorted_players = sorted(players, key=lambda p: p.score, reverse=True)

        running = True

        while running:
            self.screen.fill((20, 20, 20))  # Dark background

            # Title
            font_title = pygame.font.Font(None, 70)
            title_text = font_title.render(" Fin du Jeu ! ", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 100))
            self.screen.blit(title_text, title_rect.topleft)

            # List of players and their scores
            font_body = pygame.font.Font(None, 50)
            start_y = 200
            line_spacing = 60

            for i, player in enumerate(sorted_players):
                text = font_body.render(f"{i + 1}. {player.name} : {player.score} points", True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.screen.get_width() // 2, start_y + i * line_spacing))
                self.screen.blit(text, text_rect.topleft)

            # Quit button
            button_width, button_height = 250, 70
            button_x = (self.screen.get_width() - button_width) // 2
            button_y = start_y + len(sorted_players) * line_spacing + 50

            quit_button = pygame.Rect(button_x, button_y, button_width, button_height)

            # Mouse hover effect
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = quit_button.collidepoint(mouse_pos)
            button_color = (0, 150, 255) if is_hovered else (0, 128, 255)

            pygame.draw.rect(self.screen, button_color, quit_button, border_radius=15)  # Blue button
            pygame.draw.rect(self.screen, (255, 255, 255), quit_button, 3, border_radius=15)  # White border

            # Quit button text
            quit_text = font_body.render("Quitter", True, (255, 255, 255))
            quit_text_rect = quit_text.get_rect(center=quit_button.center)
            self.screen.blit(quit_text, quit_text_rect.topleft)

            pygame.display.flip()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                    if quit_button.collidepoint(event.pos):
                        pygame.quit()
                        exit()

