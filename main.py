from board import Board
from configurations import configurations
from random import randrange



def main():
    board = Board(configurations[0])
    print(configurations[0]["targets"])

    objective = configurations[0]["targets"][randrange(0, len(configurations[0]["targets"]))]
    obj = configurations[0]["targets"][0]
    board.addTarget(obj)
    # board.printBoard()

    robot = board.getRobotPosition()
    board.printBoard()
    print(robot[0])
    board.getPossibleMovesOfRobot(robot[0]["position"])


if __name__ == '__main__':
    main()