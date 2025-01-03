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
        start_x = 20  # Starting x-coordinate for the first move

        for i, move in enumerate(moves_to_display):
            robot_color, direction, _ = move
            center_x = start_x + i * spacing_x
            center_y = history_start_y + 50  # Center the cross vertically in the history area

            # Draw the movement cross
            self.draw_movement_cross(robot_color, direction, (center_x, center_y))

            # Draw the direction label below the cross
            self.render_text(direction.capitalize(), (center_x - 10, center_y + 20),
                             color=self.robot_colors.get(robot_color, self.BLACK), font_size=16)

    def draw_target(self,target):
        position= target['position']
        y,x = position
        color = self.get_target_color(target['color'])

        rect_y = self.margin_y + x * self.cell_size
        rect_x = self.margin_x + y * self.cell_size

        # Create a transparent surface
        surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)

        # Define the target as a large triangle
        triangle_points = [
            (self.cell_size // 2, 10),  # Top-center point
            (10, self.cell_size - 10),  # Bottom-left point
            (self.cell_size - 10, self.cell_size - 10)  # Bottom-right point
        ]

        # Draw the triangle on the transparent surface
        pygame.draw.polygon(surface, color, triangle_points)  # Semi-transparent red

        # Blit the surface onto the main screen
        self.screen.blit(surface, (rect_y, rect_x))

    def draw_robot(self,board,player):
        for robot in board.robots:
            # Get robot color and position
            color = self.robot_colors.get(robot["color"], self.BLACK)  # Default to black if color not found
            robot_y, robot_x = robot["position"]  # Position is (row, column)

            # Calculate robot's screen position
            center_x = self.margin_x + robot_y * self.cell_size + self.cell_size // 2
            center_y = self.margin_y + robot_x * self.cell_size + self.cell_size // 2

            # Draw the robot as a circle
            pygame.draw.circle(self.screen, color, (center_y, center_x), self.cell_size // 3)

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

        pygame.display.flip()  # Update the display

    def show_menu(screen, width, height):
        """
        Displays the main menu where users can select options.
        """
        font = pygame.font.Font(None, 48)
        screen.fill((255, 255, 255))

        title = font.render("Rasende Roboter", True, (0, 0, 0))
        start_game = font.render("1. Launch Game", True, (0, 0, 0))
        show_rules = font.render("2. Rules", True, (0, 0, 0))

        screen.blit(title, (width // 2 - title.get_width() // 2, height // 4))
        screen.blit(start_game, (width // 2 - start_game.get_width() // 2, height // 2))
        screen.blit(show_rules, (width // 2 - show_rules.get_width() // 2, height // 2 + 50))

        pygame.display.flip()
        return "MENU"

    def show_rules(screen, width, height):
        """
        Displays the rules of the game.
        """
        font = pygame.font.Font(None, 36)
        screen.fill((255, 255, 255))

        rules = [
            "Rules:",
            "1. Select a robot to move.",
            "2. Navigate the robot to its target.",
            "3. The first player to solve a target wins.",
            "4. Game ends when all targets are solved.",
            "",
            "Press any key to return to the menu."
        ]

        y_offset = height // 4
        for line in rules:
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, y_offset))
            y_offset += 40

        pygame.display.flip()
        return "RULES"

    def select_game_mode(screen, width, height):
        """
        Displays the game mode selection screen.
        """
        font = pygame.font.Font(None, 36)
        screen.fill((255, 255, 255))

        modes = [
            "Select Game Mode:",
            "1. Human vs Human",
            "2. Human vs AI",
            "3. AI vs AI"
        ]

        y_offset = height // 4
        for line in modes:
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, y_offset))
            y_offset += 50

        pygame.display.flip()
        return "GAME_MODE"

    def select_target_number(screen, width, height, max_targets):
        """
        Displays a target selection screen.
        """
        font = pygame.font.Font(None, 36)
        screen.fill((255, 255, 255))

        prompt = f"Enter the number of targets (1-{max_targets}):"
        text = font.render(prompt, True, (0, 0, 0))
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 2))
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
            screen.fill((255, 255, 255))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2))
            input_display = font.render(input_number, True, (0, 0, 0))
            screen.blit(input_display, (width // 2 - input_display.get_width() // 2, height // 2 + 50))
            pygame.display.flip()
