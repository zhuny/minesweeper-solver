from solver.game import MinesweeperWindowInterface


def main():
    game = MinesweeperWindowInterface()
    info = game.get_info()
    print(info)
    print('\n'.join(info.mine_info))


if __name__ == '__main__':
    main()
