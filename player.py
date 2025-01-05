import copy

import pygame
import heapq
import collections


class Player:
    def __init__(self, name):
        """
        Initialise un joueur avec un nom, un score, un compteur de tours et une liste de mouvements.

        Args:
            name (str): Nom du joueur.
        """
        self.name = name
        self.score = 0
        self.turn = 1 # Numéro du tour du joueur
        self.moves = []  # Liste des mouvements effectués par le joueur
        self.selected_robot = None  # Robot actuellement sélectionné par le joueur

    def _state_to_tuple(self, state):
        """
        Convertit un état en un tuple hachable (dans le but d'optimiser  le temps)
        pour suivre les états visités. L'état inclut les positions des robots et la cible actuelle.

        Args:
            state (tuple): L'état sous la forme (robots, cible).

        Returns:
            tuple: Une représentation unique et hachable de l'état.
        """
        robots, target = state

        robots_tuple = tuple((tuple(r["position"]), r["color"]) for r in robots)
        target_tuple = (target["position"], target["color"])

        return robots_tuple + target_tuple

    def _tuple_to_state(self, state_tuple):
        """
            Convertit une représentation sous forme de tuple en une structure d'état.

            Args:
                state_tuple (tuple): Représentation tuple de l'état.

            Returns:
                tuple: Un état sous forme de (robots, cible).
            """
        robots_tuple = state_tuple[:-2]
        target_tuple = state_tuple[-2:]

        # Reconstruit les robots et la cible à partir du tuple
        robots = [{"position": pos, "color": color} for pos, color in robots_tuple]
        target = {"position": target_tuple[0], "color": target_tuple[1]}
        return robots, target


    def set_board(self, board):
        """
         Associe un plateau de jeu au joueur.

         Args:
             board (Board): Le plateau de jeu à associer.
         """
        self.board = board

    def increment_turn(self):
        """
           Incrémente le compteur de tours du joueur.
        """
        self.turn += 1

    def resetMoves(self):
        """
        Réinitialise les mouvements du joueur et le robot sélectionné.
        """
        self.moves.clear()
        self.selected_robot = None

class HumanPlayer(Player):
    def __init__(self, name):
        """
          Initialise un joueur humain.

          Args:
              name (str): Nom du joueur humain.
          """
        super().__init__(name)

    def handle_click(self, position):
        """
         Gère un clic de souris pour sélectionner un robot.

         Args:
             position (tuple): Coordonnées (y, x) de la case cliquée.

         Returns:
             bool: True si un robot est sélectionné, False sinon.
         """
        for robot in self.board.robots:
            ry, rx = robot["position"]
            if (ry, rx) == position: # On vérifie si les positions du robots correspondent à celle du click
                self.selected_robot = robot
                print(f"Selected robot: {robot['color']}")
                return True
        print("No robot selected")
        return False

    def handle_keypress(self, key):
        """
         Gère les touches directionnelles pour déplacer le robot sélectionné.

         Args:
             key (pygame.Key): Touche pressée.

         Returns:
             str: Direction du mouvement si possible, sinon None.
         """
        if not self.selected_robot:
            print("No robot selected to move")
            return False

        # On attribue la direction en fonction de la flèche
        direction_map = {
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right",
        }
        direction = direction_map.get(key)
        if direction:
            # Tente de déplacer le robot dans la direction donnée
            moved = self.board.moveARobotWithDirection(self.selected_robot, direction)
            if moved:
                return direction
            else:
                print("Move not possible")

    def play(self, events, margin_x, margin_y, cell_size):
        """
        Gère le tour d'un joueur humain en traitant les événements.

        Args:
            events (list): Liste des événements utilisateur.
            margin_x (int): Marge horizontale pour centrer le plateau.
            margin_y (int): Marge verticale pour centrer le plateau.
            cell_size (int): Taille d'une cellule du plateau.

        Returns:
            str: Résultat du tour ("RESET", "SOLVED", ou None).
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Convertit le clic en position sur le plateau
                mouse_y, mouse_x = event.pos
                board_y = (mouse_y - margin_y) // cell_size  # Conversion y -> ligne
                board_x = (mouse_x - margin_x) // cell_size  # Conversion x -> colonne
                if 0 <= board_x < self.board.BOARD_SIZE and 0 <= board_y < self.board.BOARD_SIZE:
                    if self.board.board[board_y][board_x]["type"] == "M":
                        # Réinitialise si une case centrale est cliquée
                        print("M")
                        self.moves.clear()
                        return "RESET"
                    # Gère la sélection d'un robot
                    self.handle_click((board_x, board_y))


            elif event.type == pygame.KEYDOWN:
                # Gère les touches directionnelles
                direction = self.handle_keypress(event.key)
                if direction:
                    # Ajoute le mouvement à l'historique
                    self.moves.append((self.selected_robot["color"], direction, self.selected_robot["position"]))
                    print(f"Moved robot {self.selected_robot['color']} {direction}")
                    self.board.printBoard()

                    # Vérifie si la cible actuelle est atteinte
                    if self.board.is_robot_on_current_target():
                        print(f"Player {self.name} solved target {self.board.get_current_target()}")
                        return "SOLVED"  # Indique que la cible est atteinte


class BFSPlayer(Player):
    def __init__(self, name):
        """
        Initialise un joueur utilisant l'algorithme de recherche en largeur (BFS).

        Args:
            name (str): Nom du joueur.
        """
        super().__init__(name)

    def play(self):
        """
        Exécute l'algorithme BFS pour trouver une solution au problème de déplacement des robots.

        Yields:
            str: "CALCULATING" lorsque l'algorithme est en cours de calcul.
            str: "SOLVED" si une solution est trouvée.
            str: "NO_SOLUTION" si aucune solution n'est trouvée.
        """

        # Initialisation de l'état de départ (donc on met la liste de robots, avec l'objectif)
        start_state = (self.board.robots, self.board.get_current_target())
        queue = collections.deque([(start_state, [])])  # On rajoute à notre liste l'état
        visited = set() # Ensemble des états déjà visités

        # Ajout du premier état aux états visités
        start_state_tuple = self._state_to_tuple(start_state)
        visited.add(start_state_tuple)

        while queue:
            yield "CALCULATING"  # Indique que le calcul est en cours

            # On récupère le premier état dans la file
            current_state, path = queue.popleft()
            robots, target = current_state

            # On vérifie si la cible est atteinte
            for robot in robots:
                if robot["position"] == target["position"] and robot["color"] == target["color"]:
                    # Si la solution est trouvée, on l'affiche et on retourne "SOLVED"
                    print("Solution trouvée avec les mouvements :", path)
                    for move in path:
                        print(f"Déplacement : Robot {move[0]} vers {move[1]} jusqu'à {move[2]}")
                    self.moves = path # On stocke les mouvements dans l'historiques
                    yield "SOLVED"
                    return

            # Génération des états suivants
            for robot in robots:
                # Récupère les mouvements possibles pour ce robot
                possible_moves = self.board.getPossibleMovesOfRobot(robot["position"], robots)
                for direction, new_position in possible_moves.items():
                    if new_position:
                        # Pour chaque nouvelle position possibles, on crée un nouvel état avec le robot déplacé
                        new_robots = [
                            {"color": r["color"], "position": new_position if r == robot else r["position"]}
                            for r in robots
                        ]
                        new_state = (new_robots, target)
                        new_state_tuple = self._state_to_tuple(new_state)

                        # Ajoute le nouvel état à la file s'il n'a pas encore été visité
                        if new_state_tuple not in visited:
                            visited.add(new_state_tuple)
                            queue.append((new_state, path + [(robot["color"], direction, new_position)]))

        print("Aucune solution trouvée.")
        yield "NO_SOLUTION"  # Dans le cas où on ne trouve pas de solution


class AStartPlayer(Player):
    def __init__(self, name):
        """
        Initialise un joueur utilisant l'algorithme A* pour résoudre le problème.

        Args:
            name (str): Nom du joueur.
        """
        super().__init__(name)

    def play(self):
        """
        Exécute l'algorithme A* pour trouver une solution optimale au problème.

        Yields:
            str: "CALCULATING" lorsque l'algorithme est en cours.
            str: "SOLVED" si une solution est trouvée.
            str: "NO_SOLUTION" si aucune solution n'est trouvée.
        """

        # État de départ : positions des robots et cible actuelle
        start_state = (self.board.robots, self.board.get_current_target())

        # File de priorité pour gérer les états ouverts (avec heapq pour A*)
        opened = []
        heapq.heappush(opened, (0, self._state_to_tuple(start_state), [])) # (coût, état, chemin)

        # Ensemble pour stocker les états déjà explorés
        closed = set()

        def heuristic(robot_position, target_position):
            """
             Fonction heuristique basée sur la distance de Manhattan.

             Args:
                 robot_position (tuple): Position actuelle du robot (y, x).
                 target_position (tuple): Position de la cible (y, x).

             Returns:
                 int: Distance estimée entre le robot et la cible.
             """
            ry, rx = robot_position
            ty, tx = target_position
            return abs(ry - ty) + abs(rx - tx)

        # Tant que il y'a des possibilités dans la liste opened
        while opened:
            yield "CALCULATING"

            # Dépile l'état avec le coût le plus faible
            cost, current_state_tuple, path = heapq.heappop(opened)

            # Conversion du tuple en structure d'état exploitable
            current_state = self._tuple_to_state(current_state_tuple)
            robots, target = current_state

            for robot in robots:
                # Vérifie si un robot atteint la cible
                if robot["position"] == target["position"] and robot["color"] == target["color"]:
                    print("Solution trouvée avec les mouvements :", path)
                    for move in path:
                        print(f"Déplacement : Robot {move[0]} vers {move[1]} jusqu'à {move[2]}")
                    self.moves = path
                    yield "SOLVED"  # Retourne que la solution est trouvée
                    return

            # Génère les états suivants pour chaque mouvement possible
            for robot in robots:
                # Obtenir les mouvements possibles pour ce robot
                possible_moves = self.board.getPossibleMovesOfRobot(robot["position"],robots)
                for direction, new_position in possible_moves.items():
                    if new_position:
                        # Si le déplacement est valide ça crée un nouvel état avec le robot déplacé
                        new_robots = copy.deepcopy(robots)
                        for r in new_robots:
                            if r["color"] == robot["color"]:
                                r["position"] = new_position

                        new_state = (new_robots, target)
                        new_state_tuple = self._state_to_tuple(new_state)  # On reconvertit en tuple pour optimiser

                        # Vérifie si cet état a déjà été exploré
                        if new_state_tuple not in closed:
                            closed.add(new_state_tuple) # Marque l'état comme visité
                            # Calcule le coût total (g + h) -> chaque déplacement vaut le cout de 1
                            new_cost = cost + 1 + heuristic(new_position, target["position"])

                            # Ajoute le nouvel état à la file ouverte
                            heapq.heappush(opened, (
                            new_cost, new_state_tuple, path + [(robot["color"], direction, new_position)]))

        yield "NO_SOLUTION" # Si la file est vide et aucune solution n'est trouvée
