import copy

class Board:
    WALL_TOP = "T"
    WALL_BOTTOM = "B"
    WALL_LEFT = "L"
    WALL_RIGHT = "R"

    # We can't start with an random configuration because random doesn't garantee a solution so we need a starting
    # configuration
    def __init__(self, configuration, board_size):
        # We initialize an empty table with the given size
        self.BOARD_SIZE = board_size
        self.board = [
            [
                {"type": "-", "walls": []} for _ in range(self.BOARD_SIZE)
            ] for _ in range(self.BOARD_SIZE)
        ]

        # We add the middle cells
        self.board[7][7]["type"] = "M"
        self.board[7][8]["type"] = "M"
        self.board[8][7]["type"] = "M"
        self.board[8][8]["type"] = "M"


        # We add the wall that was in configuration because wall is unmovable
        for wall in configuration["walls"]:
            self.board[wall[0]][wall[1]]["walls"].append(wall[2])

        self.robots = configuration["robots"]
        self.initial_config_robot = copy.deepcopy(configuration["robots"])
        self.targets = configuration["targets"]
        self.current_target_index = 0

    def get_current_target(self):
        """
        Returns the current target to solve.
        """
        if self.current_target_index < len(self.targets):
            return self.targets[self.current_target_index]
        return None

    def advance_to_next_target(self):
        """
        Moves to the next target in the list.
        """
        if self.current_target_index < len(self.targets):
            self.current_target_index += 1

    def is_robot_on_current_target(self):
        """
        Checks if any robot is on the current target.
        """
        current_target = self.get_current_target()
        for robot in self.robots:
            if robot["color"] == current_target["color"] and robot["position"] == current_target["position"]:
                return True
        return False

    def getRobotPosition(self):
        return self.robots

    def getRobotPositionWithColor(self, color):
        for c in self.robots:
            if color in c["color"]:
                return c

    def printBoard(self):
        for y in range(self.BOARD_SIZE):
            row = ""
            for x in range(self.BOARD_SIZE):
                cell = self.board[y][x]

                # Check for a robot at the position
                robot_here = next((r for r in self.robots if r["position"] == (y, x)), None)

                if robot_here:
                    row += f" {robot_here['color'][0]} "  # Robot color's first letter
                elif "T" in cell["type"]:
                    row += f" {cell['type']} "  # Target
                elif cell["type"] == "M":
                    row += " M "  # Center square
                else:
                    # Add walls if present
                    walls = ""
                    if 'T' in cell["walls"]: walls += "↑"
                    if 'B' in cell["walls"]: walls += "↓"
                    if 'L' in cell["walls"]: walls += "←"
                    if 'R' in cell["walls"]: walls += "→"

                    # Display walls or empty space
                    row += f" {walls if walls else '-'} "

            print(row)

    def isCollision(self, coord, all_robots):
        y, x = coord
        for r in all_robots:
            if r["position"] == (y, x):
                return True
        return False

    def getPossibleMovesOfRobot(self, coord, robots=None):
        """
        Get possible moves for a robot at a given coordinate.
        """
        if robots:
            all_robots = robots
        else :
            all_robots = self.robots

        y, x= coord
        possibleMoves = {"up": None, "down": None, "left": None, "right": None}

        current_wall = self.board[y][x]["walls"]
        directions = {
            "up": (self.WALL_TOP, self.WALL_BOTTOM, y - 1, -1, -1, "vertical"),
            "down": (self.WALL_BOTTOM, self.WALL_TOP, y + 1, len(self.board), 1, "vertical"),
            "left": (self.WALL_LEFT, self.WALL_RIGHT, x - 1, -1, -1, "horizontal"),
            "right": (self.WALL_RIGHT, self.WALL_LEFT, x + 1, len(self.board), 1, "horizontal"),
        }

        for direction, (passing_wall, blocking_wall, start, stop, step, axis) in directions.items():
            if passing_wall not in current_wall:  # Ensure we can move initially
                last_position = (y, x)  # Reset to starting position
                for i in range(start, stop, step):
                    # Calculate the next position based on the axis
                    if axis == "vertical":
                        next_cell = self.board[i][x]
                        next_position = (i, x)
                    else:
                        next_cell = self.board[y][i]
                        next_position = (y, i)

                    # Check for collisions or obstacles
                    if (
                            blocking_wall in next_cell["walls"] or
                            "M" in next_cell["type"] or
                            self.isCollision(next_position, all_robots)
                    ):
                        break  # Stop movement in this direction

                    # If there's a wall we "pass through," this is the stopping point
                    if passing_wall in next_cell["walls"]:
                        last_position = next_position
                        break

                    # Update the last valid position
                    last_position = next_position

                # Assign the last valid position or None if no move is possible
                if last_position != (y,x):
                    possibleMoves[direction] = last_position

        return possibleMoves

    def moveARobotWithDirection(self, robot, direction):
        possible_moves = self.getPossibleMovesOfRobot(robot["position"])
        new_position = possible_moves.get(direction)

        if new_position:  # Simplifies the check for valid moves
            self.moveARobot(robot, new_position)
            return True
        return False

    def moveARobot(self, robot, coord):
        for r in self.robots:
            if r == robot:
                r["position"] = coord
                break

    def resetToInitialConfig(self):
        self.robots = copy.deepcopy(self.initial_config_robot)

    def setNewConfig(self, robots):
        self.initial_config_robot = robots
        self.resetToInitialConfig()

    """"
    def getPossibleMovesOfRobot(self, coord):
        # Maybe do multithreading
        x, y = coord
        possibleMoves = {"up": None, "down": None, "left": None, "right": None}

        current_wall = self.board[x][y]["walls"]
        last_position = (x, y)

        directions = {
            "up": (self.WALL_TOP, self.WALL_BOTTOM, x - 1, -1, -1, "vertical"),
            "down": (self.WALL_BOTTOM, self.WALL_TOP, x + 1, len(self.board), 1, "vertical"),
            "left": (self.WALL_LEFT, self.WALL_RIGHT, y - 1, -1, -1, "horizontal"),
            "right": (self.WALL_RIGHT, self.WALL_LEFT, y + 1, len(self.board), 1, "horizontal"),
        }

        for direction, (passing_wall, blocking_wall, start, stop, step, axis) in directions.items():
            if passing_wall not in current_wall:  # Ensure we can move initially
                for i in range(start, stop, step):
                    # Set the next cell's coordinates depending on direction
                    if axis == "vertical":
                        next_cell = self.board[i][y]
                        next_position = (i, y)
                    else:
                        next_cell = self.board[x][i]
                        next_position = (x, i)

                    # Wall blocking movement
                    if blocking_wall in next_cell["walls"] or "M" in next_cell["type"] or self.isCollision(next_position):
                        possibleMoves[direction] = last_position
                        break

                    # Wall allowing movement
                    if passing_wall in next_cell["walls"]:
                        possibleMoves[direction] = next_position
                        break

                    last_position = next_position
                else:
                    possibleMoves[direction] = last_position

                # Reset invalid moves to None
                if possibleMoves[direction] == (x, y):
                    possibleMoves[direction] = None

        print(possibleMoves)
        return possibleMoves"""
"""
    def getPossibleMovesOfRobot(self, coord):
        x, y = coord
        possibleMoves = {"up": None, "down": None, "left": None, "right": None}

        directions = {
            "up": (self.WALL_TOP, self.WALL_BOTTOM, x - 1, -1, -1, "vertical"),
            "down": (self.WALL_BOTTOM, self.WALL_TOP, x + 1, len(self.board), 1, "vertical"),
            "left": (self.WALL_LEFT, self.WALL_RIGHT, y - 1, -1, -1, "horizontal"),
            "right": (self.WALL_RIGHT, self.WALL_LEFT, y + 1, len(self.board), 1, "horizontal"),
        }

        for direction, (passing_wall, blocking_wall, start, stop, step, axis) in directions.items():
            if passing_wall not in self.board[y][x]["walls"]:  # Initial check: can move in this direction?
                new_position = (x, y)

                for i in range(start, stop, step):
                    # Determine the next cell to check
                    if axis == "vertical":
                        cell = self.board[i][y]
                        current_position = (i, y)
                    else:
                        cell = self.board[x][i]
                        current_position = (x, i)

                    # If there's a wall or center square blocking the move, stop
                    if blocking_wall in cell["walls"] or "M" in cell["type"]:
                        break

                    # If there's a wall we "pass through," this is the stopping point
                    if passing_wall in cell["walls"]:
                        new_position = current_position
                        break

                    new_position = current_position  # Update valid position

                # Save the move if the robot can move
                if new_position != (x, y):
                    possibleMoves[direction] = new_position

        return possibleMoves
"""


