from game_window import GameWindow
from board import Board
from configurations import configurations
from player import HumanPlayer, AStartPlayer, BFSPlayer, BestFirstSearchPlayer, DijkstraPlayer
from menu_window import MenuWindow
import pygame
import time

# Constants for screen dimensions and board settings
BOARD_SIZE = 16
CELL_SIZE = 40
WIDTH = 1200
HEIGHT = 776
MARGIN_X = (WIDTH - BOARD_SIZE * CELL_SIZE) // 6
MARGIN_Y = (HEIGHT - BOARD_SIZE * CELL_SIZE) // 2


def main():
    pygame.init()

    index = 2

    # Initialize MenuWindow
    menu = MenuWindow(WIDTH, HEIGHT)
    state = menu.show_menu()
    game_mode = ""
    players = []  # Initialize players to avoid reference errors later

    while state != "GAME":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if state == "GAME":
            break

        elif state == "GAME_MODE":
            # Select the game mode
            game_mode = menu.select_game_mode_with_graphics()

            if game_mode == "HUMAN_VS_HUMAN":
                # Set up human players
                players = [HumanPlayer("Player 1"), HumanPlayer("Player 2")]
                state = "TARGET_SELECTION"  # Move to target selection only after setting players

            elif game_mode == "HUMAN_VS_AI":
                # Select an AI type for the second player
                ai_type = menu.select_ai("Choisissez l'IA pour le mode Humain vs IA")
                if ai_type == "BFS":
                    players = [HumanPlayer("Player 1"), BFSPlayer(ai_type)]
                elif ai_type == "BestFirst":
                    players = [HumanPlayer("Player 1"), BestFirstSearchPlayer(ai_type)]
                elif ai_type == "A*":
                    players = [HumanPlayer("Player 1"), AStartPlayer(ai_type)]
                elif ai_type == "Djikstra":
                    players = [HumanPlayer("Player 1"), DijkstraPlayer(ai_type)]
                state = "TARGET_SELECTION"  # Move to target selection only after AI is selected

            elif game_mode == "AI_VS_AI":
                # Select AI types for both players
                ai_type_1 = menu.select_ai("Choisissez la première IA pour le mode IA vs IA")
                ai_type_2 = menu.select_ai("Choisissez la deuxième IA pour le mode IA vs IA")

                if ai_type_1 == "BFS":
                    player1 = BFSPlayer(ai_type_1 + " 1")
                elif ai_type_1 == "BestFirst":
                    player1 = BestFirstSearchPlayer(ai_type_1 + " 1")
                elif ai_type_1 == "A*":
                    player1 = AStartPlayer(ai_type_1 + " 1")
                elif ai_type_1 == "Djikstra":
                    player1 = DijkstraPlayer(ai_type_1 + " 1")

                if ai_type_2 == "BFS":
                    player2 = BFSPlayer(ai_type_2 + " 2")
                elif ai_type_2 == "BestFirst":
                    player2 = BestFirstSearchPlayer(ai_type_2 + " 2")
                elif ai_type_2 == "A*":
                    player2 = AStartPlayer(ai_type_2 + " 2")
                elif ai_type_2 == "Djikstra":
                    player2 = DijkstraPlayer(ai_type_2 + " 2")


                players = [player1, player2]
                state = "TARGET_SELECTION"  # Move to target selection only after both AIs are selected

        elif state == "TARGET_SELECTION":
            # Select the number of targets
            max_targets = len(configurations[index]["targets"])
            num_targets = menu.select_target_number(max_targets)
            state = "GAME"  # Once targets are selected, move to the game

    # Initialize game components after menu selection
    board_config = configurations[index]
    board = Board(board_config, BOARD_SIZE)
    game_window = GameWindow(WIDTH, HEIGHT, CELL_SIZE, MARGIN_Y, MARGIN_X)

    for player in players:
        player.set_board(board)

    current_player_index = 0
    ai_generator = None

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

            winner = players[ex_index] if len(players[ex_index].moves) <= len(players[current_player_index].moves) else \
            players[current_player_index]

            if players[ex_index].turn == players[current_player_index].turn:
                # Advance to the next target
                winner.score += 1
                game_window.show_popup(winner.name, len(winner.moves))

                board.advance_to_next_target()

                # Check if all targets are solved
                if board.current_target_index >= num_targets:
                    game_window.show_end_screen(players)
                    break

                players[ex_index].resetMoves()
                players[current_player_index].resetMoves()

                winner_configuration = winner.board.getRobotPosition()

                for p in players:
                    p.board.setNewConfig(winner_configuration)


                game_window.update_display(board, players[current_player_index])
            else:
                board.resetToInitialConfig()


        # Update the display
        game_window.update_display(board, current_player)


if __name__ == "__main__":
    main()
