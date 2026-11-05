#!/usr/bin/env python

from helpful_objects import *

if __name__ == '__main__' :
    grid = Grid(20, 8)
    grid.scatter_bots(10)
    grid.loop_until_done(debug = True)
