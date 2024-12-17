class Board:
    BOARD_SIZE = 16
    WALL_TOP = "T"
    WALL_BOTTOM = "B"
    WALL_LEFT = "L"
    WALL_RIGHT = "R"

    # We can't start with an random configuration because random doesn't garantee a solution so we need a starting
    # configuration
    def __init__(self, configuration):
        # We initialize an empty table with the given size
        self.board = [
            [
                {"type": "-", "walls": []} for _ in range(Board.BOARD_SIZE)
            ] for _ in range(Board.BOARD_SIZE)
        ]

        self.board[7][7]["type"] = "M"
        self.board[7][8]["type"] = "M"
        self.board[8][7]["type"] = "M"
        self.board[8][8]["type"] = "M"


        # We add the wall that was in configuration because wall is unmovable
        for wall in configuration["walls"]:
            self.board[wall[0]][wall[1]]["walls"].append(wall[2])

        self.robots = configuration["robots"]
        self.target = None

    def addTarget(self, target):
        self.target = target
        self.board[target["position"][0]][target["position"][1]]["type"] = "T" + target["color"]

    def getRobotPosition(self):
        return self.robots

    def getRobotPositionWithColor(self, color):
        for c in self.robots:
            if color in c["color"]:
                return c

    def printBoard(self):
        for y in range(Board.BOARD_SIZE):
            row = ""
            for x in range(Board.BOARD_SIZE):
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

    def getPossibleMovesOfRobot(self, coord):
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
                    if blocking_wall in next_cell["walls"] or "M" in next_cell["type"]:
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
        return possibleMoves
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


