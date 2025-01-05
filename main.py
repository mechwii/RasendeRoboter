from game_window import GameWindow
from board import Board
from configurations import configurations
from player import HumanPlayer, AStartPlayer, BFSPlayer
from menu_window import MenuWindow
import pygame
import time

# Constante pour l'affichage graphique
BOARD_SIZE = 16
CELL_SIZE = 40
WIDTH = 1200
HEIGHT = 776
MARGIN_X = (WIDTH - BOARD_SIZE * CELL_SIZE) // 6
MARGIN_Y = (HEIGHT - BOARD_SIZE * CELL_SIZE) // 2


def main():
    pygame.init()

    index = 2 # Index de la configuration choisie (modifiable selon les besoins)

    menu = MenuWindow(WIDTH, HEIGHT)
    state = menu.show_menu()
    game_mode = ""
    players = []

    # Boucle pour gérer le menu
    while state != "GAME":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if state == "GAME":
            break

        elif state == "GAME_MODE":
            # Sélection du mode de jeu
            game_mode = menu.select_game_mode_with_graphics()

            if game_mode == "HUMAN_VS_HUMAN":
                players = [HumanPlayer("Player 1"), HumanPlayer("Player 2")]
                state = "TARGET_SELECTION"

            elif game_mode == "HUMAN_VS_AI":
                # Mode humain contre IA avec sélection du type d'IA
                ai_type = menu.select_ai("Choisissez l'IA pour le mode Humain vs IA")
                if ai_type == "BFS":
                    players = [HumanPlayer("Player 1"), BFSPlayer(ai_type)]
                elif ai_type == "A*":
                    players = [HumanPlayer("Player 1"), AStartPlayer(ai_type)]
                state = "TARGET_SELECTION"

            elif game_mode == "AI_VS_AI":
                # Mode IA contre IA avec sélection des deux types d'IA
                ai_type_1 = menu.select_ai("Choisissez la première IA pour le mode IA vs IA")
                ai_type_2 = menu.select_ai("Choisissez la deuxième IA pour le mode IA vs IA")

                if ai_type_1 == "BFS":
                    player1 = BFSPlayer(ai_type_1 + " 1")
                elif ai_type_1 == "A*":
                    player1 = AStartPlayer(ai_type_1 + " 1")


                if ai_type_2 == "BFS":
                    player2 = BFSPlayer(ai_type_2 + " 2")
                elif ai_type_2 == "A*":
                    player2 = AStartPlayer(ai_type_2 + " 2")

                players = [player1, player2]
                state = "TARGET_SELECTION"

        elif state == "TARGET_SELECTION":
            # On choisit le nombre de cible
            max_targets = len(configurations[index]["targets"])
            num_targets = menu.select_target_number(max_targets)
            state = "GAME"

    # On initialise le jeu
    board_config = configurations[index]
    board = Board(board_config, BOARD_SIZE)
    game_window = GameWindow(WIDTH, HEIGHT, CELL_SIZE, MARGIN_Y, MARGIN_X)

    for player in players:
        player.set_board(board)

    current_player_index = 0

    # On met des générateurs avec l'utilisation de yield afin de permettre au programme de ne pas freeze
    ai_generator = None

    print(board.get_current_target())

    while game_window.running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                game_window.running = False

        current_player = players[current_player_index]

        # Le cas ou le joueur est de type humain (on a besoin de paramètre pour l'interface graphique)
        if isinstance(current_player, HumanPlayer):
            move_result = current_player.play(events, MARGIN_X, MARGIN_Y, CELL_SIZE)
        else:
            # Dans le cas ou c'est une IA
            if not ai_generator:
                start_time = time.time()  # On prend le temps pour les comparer
                ai_generator = current_player.play()  # Appel de la méthode de lancement d'IA
            try:
                ai_result = next(ai_generator)
                # Plusieurs états sont disponibles pour voir l'avancée de l'IA
                if ai_result == "CALCULATING":
                    # Pour chaque solution étudié elle printera "Calculating" histoire qu'on sait qu'elle est
                    # en marche
                    print("Calculating : ")
                if ai_result == "SOLVED":
                    # L'IA a trouvé une solution
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    print(f"AI solved the problem in {elapsed_time:.2f} seconds.")

                    # Réinitialise le générateur
                    ai_generator = None

                    #On exécute les mouvements de l'IA mais on s'assure que l'utilisateur peut quitter si
                    # il le souhaite
                    for move in current_player.moves:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                exit()
                        color, direction, position = move
                        robot = next(robot for robot in board.robots if robot["color"] == color)
                        board.moveARobotWithDirection(robot, direction)
                        game_window.update_display(board, current_player)
                        time.sleep(3) # On met une pause parceque l'IA est trop rapide
                    move_result = "SOLVED"
                else:
                    move_result = None
            # Dans le cas ou l'IA n'a pas trouvé de solution
            except StopIteration:
                ai_generator = None

        # Dans le cas on le joueur reset, on reinitialise ses coups
        if move_result == "RESET":
            board.resetToInitialConfig()
        elif move_result == "SOLVED":
            # Si un joueur atteint la cible
            if isinstance(current_player, HumanPlayer):
                # On met une petite pause pour voir le mouvement
                game_window.update_display(board, current_player)
                time.sleep(0.1)
            players[current_player_index].increment_turn()

            # Passe au joueur suivant
            ex_index = current_player_index
            current_player_index = (current_player_index + 1) % len(players)



            if players[ex_index].turn == players[current_player_index].turn:
                # Détermine le gagnant du tour en fonction du nombre de mouvements (en cas d'égalité c'est le premier joueur qui gagne)
                winner = players[current_player_index] if len(players[current_player_index].moves) <= len(
                    players[ex_index].moves) else players[ex_index]

                # Passe à la cible suivante
                winner.score += 1 # Incrémente le score du gagnant
                game_window.show_popup(winner.name, len(winner.moves))

                board.advance_to_next_target()

                # Si on a résolu toutes les cibles on affiche les gagnants
                if board.current_target_index >= num_targets:
                    game_window.show_end_screen(players)
                    break

                # On réinitialise les mouvements
                players[ex_index].resetMoves()
                players[current_player_index].resetMoves()

                # On prend la configuration du gagnant
                winner_configuration = winner.board.getRobotPosition()

                # On s'assure que tous les joueurs on la même configuration
                for p in players:
                    p.board.setNewConfig(winner_configuration)

                game_window.update_display(board, players[current_player_index])
            else:
                board.resetToInitialConfig()

        # On actualise l'écran de jeu
        game_window.update_display(board, current_player)


if __name__ == "__main__":
    main()