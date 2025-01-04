import copy
import random

import pygame
import heapq
import collections




class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.turn = 1
        self.moves = []
        self.selected_robot = None

    def _state_to_tuple(self, state):
        """
        Converts the state into a hashable tuple for visited state tracking.
        A state includes the positions of all robots and the current target.

        Args:
            state (tuple): The state as (robots, target).

        Returns:
            tuple: A unique representation of the state.
        """
        robots, target = state

        # Sort robots by color to ensure consistency in representation
        robots_tuple = tuple(sorted((robot["position"], robot["color"]) for robot in robots))

        # Include target position and color
        target_tuple = (target["position"], target["color"])

        return robots_tuple + target_tuple

    def set_board(self, board):
        self.board = board

    def increment_turn(self):
        self.turn += 1

    def resetMoves(self):
        self.moves.clear()
        self.selected_robot = None

class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def handle_click(self, position):
        """
        Handles a mouse click to select a robot.
        `position` is a tuple of (y, x) coordinates from the click (row, col).
        """
        for robot in self.board.robots:
            ry, rx = robot["position"]  # Robot position is (row, column)
            if (ry, rx) == position:  # Check if the click matches the robot's position
                self.selected_robot = robot
                print(f"Selected robot: {robot['color']}")
                return True
        print("No robot selected")
        return False

    def handle_keypress(self, key):
        """
        Handles key presses to move the selected robot.
        """
        if not self.selected_robot:
            print("No robot selected to move")
            return False

        direction_map = {
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right",
        }
        direction = direction_map.get(key)
        if direction:
            moved = self.board.moveARobotWithDirection(self.selected_robot, direction)
            if moved:
                return direction
            else:
                print("Move not possible")

    def play(self, events, margin_x, margin_y, cell_size):
        """
        Handles human player's turn by processing events.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Convert click to board position
                mouse_y, mouse_x = event.pos
                board_y = (mouse_y - margin_y) // cell_size  # Swap x -> y for consistency
                board_x = (mouse_x - margin_x) // cell_size  # Swap y -> x for consistency
                if 0 <= board_x < self.board.BOARD_SIZE and 0 <= board_y < self.board.BOARD_SIZE:
                    if self.board.board[board_y][board_x]["type"] == "M":
                        print("M")
                        self.moves.clear()
                        return "RESET"
                    self.handle_click((board_x, board_y))


            elif event.type == pygame.KEYDOWN:
                direction = self.handle_keypress(event.key)
                if direction:
                    self.moves.append((self.selected_robot["color"], direction, self.selected_robot["position"]))
                    print(f"Moved robot {self.selected_robot['color']} {direction}")
                    self.board.printBoard()
                    # Check if the current target is solved
                    if self.board.is_robot_on_current_target():
                        print(f"Player {self.name} solved target {self.board.get_current_target()}")
                        return "SOLVED"  # Signal that the target is solved


class BFSPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def play(self):
        # Initialisation
        start_state = (self.board.robots, self.board.get_current_target())
        queue = collections.deque([(start_state, [])])  # (state, path)
        visited = set()

        while queue:
            yield "CALCULATING"  # Indique que le calcul est en cours

            # Déqueue un état
            (current_state, path) = queue.popleft()
            robots, target = current_state

            # Marquer comme visité
            current_state_tuple = self._state_to_tuple(current_state)
            if current_state_tuple in visited:
                continue
            visited.add(current_state_tuple)

            # Vérifie si la cible est atteinte
            for robot in robots:
                if robot["position"] == target["position"] and robot["color"] == target["color"]:
                    print("Solution trouvée avec les mouvements :", path)
                    for move in path:
                        print(f"Déplacement : Robot {move[0]} vers {move[1]} jusqu'à {move[2]}")
                    self.moves = path
                    yield "SOLVED"  # Solution trouvée
                    return

            # Générer les mouvements possibles
            for robot in robots:
                possible_moves = self.board.getPossibleMovesOfRobot(robot["position"], robots)
                for direction, new_position in possible_moves.items():
                    if new_position:
                        # Créer un nouvel état
                        new_robots = [
                            {"color": r["color"], "position": new_position if r == robot else r["position"]}
                            for r in robots
                        ]
                        new_state = (new_robots, target)

                        # Vérifier si l'état a déjà été visité
                        new_state_tuple = self._state_to_tuple(new_state)
                        if new_state_tuple not in visited:
                            queue.append((new_state, path + [(robot["color"], direction, new_position)]))

        print("Aucune solution trouvée.")
        yield "NO_SOLUTION"  # Si aucune solution n'est trouvée

    def _state_to_tuple(self, state):
        """
        Convertir un état en une représentation tuple pour Visited.
        """
        robots, target = state
        robots_tuple = tuple((r["position"], r["color"]) for r in robots)
        target_tuple = (target["position"], target["color"])
        return robots_tuple + target_tuple



class AStartPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def play(self):
        start_state = (self.board.robots, self.board.get_current_target())
        opened = []
        heapq.heappush(opened, (0, self._state_to_tuple(start_state), []))  # Use tuple representation
        closed = set()

        def heuristic(robot_position, target_position):
            # Distance de Manhattan comme heuristique
            ry, rx = robot_position
            ty, tx = target_position
            return abs(ry - ty) + abs(rx - tx)

        while opened:
            yield "CALCULATING"  # Indique que le calcul est en cours

            cost, current_state_tuple, path = heapq.heappop(opened)

            # Convert the tuple back to structured data for processing
            current_state = self._tuple_to_state(current_state_tuple)
            robots, target = current_state

            # Vérifie si la cible est atteinte
            for robot in robots:
                if robot["position"] == target["position"] and robot["color"] == target["color"]:
                    # Ajout de logs pour valider les mouvements
                    print("Solution trouvée avec les mouvements :", path)
                    for move in path:
                        print(f"Déplacement : Robot {move[0]} vers {move[1]} jusqu'à {move[2]}")
                    self.moves = path
                    yield "SOLVED"  # Indique que la solution est trouvée
                    return

            # Génère les mouvements possibles
            for robot in robots:
                possible_moves = self.board.getPossibleMovesOfRobot(robot["position"],robots)
                for direction, new_position in possible_moves.items():
                    if new_position:
                        new_robots = copy.deepcopy(robots)
                        for r in new_robots:
                            if r["color"] == robot["color"]:
                                r["position"] = new_position

                        new_state = (new_robots, target)
                        new_state_tuple = self._state_to_tuple(new_state)  # Convert to tuple

                        if new_state_tuple not in closed:
                            closed.add(new_state_tuple)
                            #new_cost = cost + len(path) + heuristic(new_position, target["position"])
                            new_cost = cost + 1 + heuristic(new_position, target["position"])

                            heapq.heappush(opened, (
                            new_cost, new_state_tuple, path + [(robot["color"], direction, new_position)]))

        yield "NO_SOLUTION"  # Si aucune solution n'est trouvée

    def _tuple_to_state(self, state_tuple):
        """
        Convert a tuple representation back into a state structure.
        """
        robots_tuple = state_tuple[:-2]
        target_tuple = state_tuple[-2:]
        robots = [{"position": pos, "color": color} for pos, color in robots_tuple]
        target = {"position": target_tuple[0], "color": target_tuple[1]}
        return robots, target


class BestFirstSearchPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def play(self):
        # Initialisation de Open
        start_state = (self.board.robots, self.board.get_current_target())
        open_list = []  # File de priorité basée sur l'heuristique
        heapq.heappush(open_list, (self.heuristic(start_state[0], start_state[1]), self._state_to_tuple(start_state), []))
        visited = set()

        while open_list:
            yield "CALCULATING"  # Indique que le calcul est en cours

            # Extraire le nœud avec l'heuristique minimale
            _, current_state_tuple, path = heapq.heappop(open_list)
            current_state = self._tuple_to_state(current_state_tuple)
            robots, target = current_state

            # Vérifie si la cible est atteinte
            for robot in robots:
                if robot["position"] == target["position"] and robot["color"] == target["color"]:
                    print("Solution trouvée avec les mouvements :", path)
                    for move in path:
                        print(f"Déplacement : Robot {move[0]} vers {move[1]} jusqu'à {move[2]}")
                    self.moves = path
                    yield "SOLVED"  # Solution trouvée
                    return

            # Marquer l'état comme visité
            visited.add(current_state_tuple)

            # Générer les mouvements possibles pour chaque robot
            for robot in robots:
                possible_moves = self.board.getPossibleMovesOfRobot(robot["position"], robots)
                for direction, new_position in possible_moves.items():
                    if new_position:
                        # Créer un nouvel état
                        new_robots = copy.deepcopy(robots)
                        for r in new_robots:
                            if r["color"] == robot["color"]:
                                r["position"] = new_position

                        new_state = (new_robots, target)
                        new_state_tuple = self._state_to_tuple(new_state)

                        if new_state_tuple not in visited:
                            # Ajouter à la file avec l'heuristique
                            heapq.heappush(open_list, (
                                self.heuristic(new_robots, target),
                                new_state_tuple,
                                path + [(robot["color"], direction, new_position)]
                            ))

        print("Aucune solution trouvée.")
        yield "NO_SOLUTION"  # Si aucune solution n'est trouvée

    def heuristic(self, robots, target):
        """
        Calcule l'heuristique basée sur la distance de Manhattan entre le robot cible et la cible.
        """
        for robot in robots:
            if robot["color"] == target["color"]:
                ry, rx = robot["position"]
                ty, tx = target["position"]
                return abs(ry - ty) + abs(rx - tx)
        return float("inf")

    def _state_to_tuple(self, state):
        """
        Convertir un état en une représentation tuple pour Open et Visited.
        """
        robots, target = state
        robots_tuple = tuple((r["position"], r["color"]) for r in robots)
        target_tuple = (target["position"], target["color"])
        return robots_tuple + target_tuple

    def _tuple_to_state(self, state_tuple):
        """
        Convertir un tuple en un état structuré.
        """
        robots_tuple = state_tuple[:-2]
        target_tuple = state_tuple[-2:]
        robots = [{"position": pos, "color": color} for pos, color in robots_tuple]
        target = {"position": target_tuple[0], "color": target_tuple[1]}
        return robots, target


class DijkstraPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def _state_to_tuple(self, state):
        """
        Converts the state into a hashable tuple for visited state tracking.
        A state includes the positions of all robots and the current target.

        Args:
            state (tuple): The state as (robots, target).

        Returns:
            tuple: A unique representation of the state.
        """
        robots, target = state
        # Convert robot positions and colors to a tuple
        robots_tuple = tuple(sorted((robot["position"], robot["color"]) for robot in robots))
        target_tuple = (target["position"], target["color"])
        return robots_tuple + target_tuple

    def _tuple_to_state(self, state_tuple):
        """
        Converts a tuple representation back into a state with robots and target.

        Args:
            state_tuple (tuple): The tuple representation of the state.

        Returns:
            tuple: A state as (robots, target).
        """
        robots_tuple = state_tuple[:-2]
        target_tuple = state_tuple[-2:]

        robots = [{"position": pos, "color": color} for pos, color in robots_tuple]
        target = {"position": target_tuple[0], "color": target_tuple[1]}

        return robots, target

    def play(self):
        start_state = (self.board.robots, self.board.get_current_target())
        start_tuple = self._state_to_tuple(start_state)

        open_list = []  # Min-heap for states
        heapq.heappush(open_list, (0, start_tuple, []))  # (cost, state_tuple, path)
        visited = set()

        while open_list:
            cost, current_tuple, path = heapq.heappop(open_list)

            # Check if the current state has already been visited
            if current_tuple in visited:
                continue
            visited.add(current_tuple)

            # Convert the tuple back to a state
            current_state = self._tuple_to_state(current_tuple)
            robots, target = current_state

            # Check if the target is reached
            for robot in robots:
                if robot["color"] == target["color"] and robot["position"] == target["position"]:
                    self.moves = path
                    yield "SOLVED"
                    return

            # Generate possible moves for each robot
            for i, robot in enumerate(robots):
                possible_moves = self.board.getPossibleMovesOfRobot(robot["position"], robots)
                for direction, new_position in possible_moves.items():
                    if new_position:
                        # Create a new state
                        new_robots = copy.deepcopy(robots)
                        new_robots[i]["position"] = new_position
                        new_state = (new_robots, target)
                        new_tuple = self._state_to_tuple(new_state)

                        # Add the new state to the priority queue
                        heapq.heappush(open_list, (cost + 1, new_tuple, path + [(robot["color"], direction, new_position)]))

            yield "CALCULATING"

        yield "NO_SOLUTION"
