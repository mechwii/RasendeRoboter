from game_window import GameWindow
from board import Board
from configurations import configurations
from player import HumanPlayer, AStartPlayer, BFSPlayer, BestFirstSearchPlayer
from menu_window import MenuWindow
import pygame
import time

# Constants for screen dimensions and board settings
BOARD_SIZE = 16
CELL_SIZE = 40
WIDTH = 1200
HEIGHT = 800
MARGIN_X = (WIDTH - BOARD_SIZE * CELL_SIZE) // 6
MARGIN_Y = (HEIGHT - BOARD_SIZE * CELL_SIZE) // 2


def main():
    pygame.init()

    # Initialize MenuWindow
    menu = MenuWindow(WIDTH, HEIGHT)
    state = menu.show_menu()

    # Handle menu navigation
    while state != "GAME":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if state == "MENU":
                    if event.key == pygame.K_1:  # Launch Game
                        state = menu.select_game_mode()
                elif state == "RULES":
                    state = menu.show_menu()
                elif state == "GAME_MODE":
                    if event.key == pygame.K_1:  # Human vs Human
                        players = [HumanPlayer("Player 1"), BidirectionalSearchPlayer("Player 2")]
                        state = "TARGET_SELECTION"
                    elif event.key in [pygame.K_2, pygame.K_3]:
                        print("AI functionality not yet implemented.")
                        state = menu.show_menu()
                elif state == "TARGET_SELECTION":
                    max_targets = len(configurations[0]["targets"])
                    num_targets = menu.select_target_number(max_targets)
                    state = "GAME"

    # Initialize game components after menu selection
    board_config = configurations[2]
    board = Board(board_config, BOARD_SIZE)
    game_window = GameWindow(WIDTH, HEIGHT, CELL_SIZE, MARGIN_Y, MARGIN_X)

    for player in players:
        player.set_board(board)

    current_player_index = 0
    ai_generator = None  # For AI incremental computation

    print(board.get_current_target())

    # Main game loop
    while game_window.running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                game_window.running = False

        # Get the current player
        current_player = players[current_player_index]

        # Handle Human Player
        if isinstance(current_player, HumanPlayer):
            move_result = current_player.play(events, MARGIN_X, MARGIN_Y, CELL_SIZE)
        else:
            # Handle AI Player
            if not ai_generator:
                ai_generator = current_player.play()  # Initialize BFS generator
            try:
                ai_result = next(ai_generator)
                if ai_result == "CALCULATING":
                    print("Calculating : ")
                if ai_result == "SOLVED":
                    print("SOLVED")
                    ai_generator = None  # Reset generator after solving
                    for move in current_player.moves:
                        time.sleep(3)
                        color, direction, position = move
                        robot = next(robot for robot in board.robots if robot["color"] == color)
                        board.moveARobotWithDirection(robot, direction)
                        game_window.update_display(board, current_player)
                    move_result = "SOLVED"
                else:
                    move_result = None
            except StopIteration:
                ai_generator = None

        # Handle game events
        if move_result == "RESET":
            board.resetToInitialConfig()
        elif move_result == "SOLVED":
            if isinstance(current_player, HumanPlayer):
                game_window.update_display(board, current_player)
                time.sleep(0.01)
            players[current_player_index].increment_turn()
            # Switch to the next player
            ex_index = current_player_index
            current_player_index = (current_player_index + 1) % len(players)

            if players[ex_index].turn == players[current_player_index].turn:
                # Advance to the next target
                if len(players[ex_index].moves) <= len(players[current_player_index].moves):
                    players[ex_index].score += 1
                else:
                    players[current_player_index].score += 1
                board.advance_to_next_target()
                players[ex_index].resetMoves()
                players[current_player_index].resetMoves()
                game_window.update_display(board, players[current_player_index])
            else:
                board.resetToInitialConfig()

            # Check if all targets are solved
            if board.current_target_index >= num_targets:
                print("All targets solved! Game over.")
                print(current_player.moves)
                game_window.running = False
                break

        # Update the display
        game_window.update_display(board, current_player)


if __name__ == "__main__":
    main()
