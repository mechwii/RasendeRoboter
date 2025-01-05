import copy

class Board:
    WALL_TOP = "T"
    WALL_BOTTOM = "B"
    WALL_LEFT = "L"
    WALL_RIGHT = "R"

    # Initialisation du plateau de jeu avec une configuration donnée
    def __init__(self, configuration, board_size):
        """
        Initialise le plateau de jeu.

        Args:
            configuration (dict): Configuration initiale avec murs, robots et cibles.
            board_size (int): Taille du plateau (ex: 16x16).
        """
        # Création d'une grille vide

        self.BOARD_SIZE = board_size
        self.board = [
            [
                {"type": "-", "walls": []} for _ in range(self.BOARD_SIZE)
            ] for _ in range(self.BOARD_SIZE)
        ]

        # Ajout des cases centrales (qui permettront de reset les moves)
        self.board[7][7]["type"] = "M"
        self.board[7][8]["type"] = "M"
        self.board[8][7]["type"] = "M"
        self.board[8][8]["type"] = "M"


        # Ajout des murs
        for wall in configuration["walls"]:
            self.board[wall[0]][wall[1]]["walls"].append(wall[2])

        # Robots et cibles
        self.robots = configuration["robots"]
        self.initial_config_robot = copy.deepcopy(configuration["robots"])
        self.targets = configuration["targets"]
        self.current_target_index = 0

    def get_current_target(self):
        """
        Renvoie la cible actuelle à atteindre.

        Returns:
            dict: Cible actuelle (position et couleur).
        """
        if self.current_target_index < len(self.targets):
            return self.targets[self.current_target_index]
        return None

    def advance_to_next_target(self):
        """
        Passe à la cible suivante dans la liste.
        """
        if self.current_target_index < len(self.targets):
            self.current_target_index += 1

    def is_robot_on_current_target(self):
        """
        Vérifie si un robot est sur la cible actuelle.

        Returns:
            bool: True si un robot est sur la cible, False sinon.
        """
        current_target = self.get_current_target()
        for robot in self.robots:
            if robot["color"] == current_target["color"] and robot["position"] == current_target["position"]:
                return True
        return False

    def getRobotPosition(self):
        """
        Récupère les positions des robots.

        Returns:
            list: Liste des robots avec leurs positions.
        """
        return self.robots

    def getRobotPositionWithColor(self, color):
        """
        Récupère les informations du robot avec une couleur donnée.

        Args:
            color (str): Couleur du robot.

        Returns:
            dict: Robot correspondant.
        """
        for c in self.robots:
            if color in c["color"]:
                return c

    def printBoard(self):
        """
        Affiche le plateau de jeu dans la console.
        """
        for y in range(self.BOARD_SIZE):
            row = ""
            for x in range(self.BOARD_SIZE):
                cell = self.board[y][x]

                # On verifie si il y'a un robot
                robot_here = next((r for r in self.robots if r["position"] == (y, x)), None)

                if robot_here:
                    row += f" {robot_here['color'][0]} "  # Premiere lettre du robo
                elif "T" in cell["type"]:
                    row += f" {cell['type']} "  # Cible
                elif cell["type"] == "M":
                    row += " M "  # Milieu
                else:
                    # Ajout des murs
                    walls = ""
                    if 'T' in cell["walls"]: walls += "↑"
                    if 'B' in cell["walls"]: walls += "↓"
                    if 'L' in cell["walls"]: walls += "←"
                    if 'R' in cell["walls"]: walls += "→"

                    row += f" {walls if walls else '-'} "

            print(row)

    def isCollision(self, coord, all_robots):
        """
          Vérifie la collision avec un autre robot.

          Args:
              coord (tuple): Coordonnées (y, x).
              all_robots (list): Liste de tous les robots.

          Returns:
              bool: True si collision, False sinon.
          """
        y, x = coord
        for r in all_robots:
            if r["position"] == (y, x):
                return True
        return False

    def getPossibleMovesOfRobot(self, coord, robots=None):
        """
        Calcule les déplacements possibles pour un robot à une position donnée.

        Args:
            coord (tuple): Coordonnées (y, x) du robot.
            robots (list, optional): Liste des robots. Si None, utilise les robots actuels. On
            utilise cette liste car pour les IA on bouge les robots fictivement, donc on a besoin
            de la nouvelle position des robots.

        Returns:
            dict: Déplacements possibles (up, down, left, right).
        """

        # Si la liste est vide on prend les robots présent sur le plateau
        if robots:
            all_robots = robots
        else :
            all_robots = self.robots

        y, x= coord

        # On initialise notre dictionnaire de retour avec toutes les directions possibles
        possibleMoves = {"up": None, "down": None, "left": None, "right": None}

        current_wall = self.board[y][x]["walls"]

        """
        Ce tableau est important puisque grâce à luion peut savoir dans chaque direction 
        si quelle type de mur est bloquant, et lequel donne accès à la case (comme dit dans 
        le rapport si je vient d'en bas vers le haut, et que je rencontre un mur qui bloque le haut
        d'une case je peux accéder à cette case, mais si il bloque le bas je m'arrête sur celle avant
        """
        directions = {
            "up": (self.WALL_TOP, self.WALL_BOTTOM, y - 1, -1, -1, "vertical"),
            "down": (self.WALL_BOTTOM, self.WALL_TOP, y + 1, len(self.board), 1, "vertical"),
            "left": (self.WALL_LEFT, self.WALL_RIGHT, x - 1, -1, -1, "horizontal"),
            "right": (self.WALL_RIGHT, self.WALL_LEFT, x + 1, len(self.board), 1, "horizontal"),
        }

        for direction, (passing_wall, blocking_wall, start, stop, step, axis) in directions.items():
            if passing_wall not in current_wall:  # On s'assure qu'on puisse bouger de base
                last_position = (y, x)  # On réinitialiser la dernière position
                for i in range(start, stop, step):
                    # On calcul la prochaine position en fonction de la direction h/v
                    if axis == "vertical":
                        next_cell = self.board[i][x]
                        next_position = (i, x)
                    else:
                        next_cell = self.board[y][i]
                        next_position = (y, i)

                    # On vérifie si dans la prochaine case un obstacle nous empêche d'y accéder
                    # et donc on doit s'arrête à la case d'avant
                    if (
                            blocking_wall in next_cell["walls"] or
                            "M" in next_cell["type"] or
                            self.isCollision(next_position, all_robots)
                    ):
                        break  # Dans ce cas la on arrête le mouvement dans cette direction

                    # Si il y'a un mur mais on peut quand même accéder à la case, on s'arrête à cette case
                    if passing_wall in next_cell["walls"]:
                        last_position = next_position
                        break

                    # On met à jour la dernière position avec la nouvelle position valide
                    last_position = next_position

                # Si notre position est différent de la position initiale on l'affecte(dernière verif)
                if last_position != (y,x):
                    possibleMoves[direction] = last_position

        return possibleMoves

    def moveARobotWithDirection(self, robot, direction):
        """
        Déplace un robot dans une direction donnée.

        Args:
            robot (dict): Robot à déplacer.
            direction (str): Direction du mouvement (up, down, left, right).

        Returns:
            bool: True si le mouvement est réussi, False sinon.
        """
        possible_moves = self.getPossibleMovesOfRobot(robot["position"])
        new_position = possible_moves.get(direction)

        # Si le move est possible on le déplace sinon non
        if new_position:
            self.moveARobot(robot, new_position)
            return True
        return False

    def moveARobot(self, robot, coord):
        """
        Met à jour la position d'un robot.

        Args:
            robot (dict): Robot à déplacer.
            coord (tuple): Nouvelle position (y, x).
        """
        for r in self.robots:
            if r == robot:
                r["position"] = coord
                break

    def resetToInitialConfig(self):
        """
        Réinitialise les robots à leur configuration initiale.
        """
        self.robots = copy.deepcopy(self.initial_config_robot)

    def setNewConfig(self, robots):
        """
        Met à jour la configuration initiale des robots. Afin que les joueurs ait la même config
        après un tour jouer (on garde la configuration de celui qui a gagné le tour).

        Args:
            robots (list): Nouvelle configuration des robots.
        """
        self.initial_config_robot = robots
        self.resetToInitialConfig()

