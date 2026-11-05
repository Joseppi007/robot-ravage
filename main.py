#!/usr/bin/env python

from helpful_objects import *

class RobotCase1 (Robot) :
    def __init__(self) :
        super().__init__()
        self.target = None
        self.others_positions = []
    def on_startup(self) :
        pass
    def after_movement(self) :
        pass
    def on_messaged(self, message) :
        pass

def main() :
    length = int(input("Grid length:  (width) "))
    bredth = int(input("Grid bredth: (height) "))
    grid = Grid(length, bredth)
    print("There are four cases you can choose from:")
    print("1: Target and Robot positions known at start.")
    print("2: 1 but with an unknown target position.")
    print("3: 2 and robots only know their own location.")
    print("4: 3 with malicious robots.")
    case_selected = int(input("Case: "))
    bot_count = int(input("How many bots? "))
    match case_selected :
        case 1 :
            bots = [RobotCase1() for i in range(bot_count)]
            grid.scatter_list_of_bots(bots)
            for bot in bots :
                bot.target = grid.target
                for other_bot in bots :
                    if other_bot == bots :
                        continue
                    bot.others_positions = other_bot.position
            grid.loop_until_done(debug = True)
        case 2 :
            pass
        case 3 :
            pass
        case 4 :
            malicious_bot_count = int(input("How many of them are malicious? "))
            good_bot_count = bot_count - malicious_bot_count

if __name__ == '__main__' :
    main()
