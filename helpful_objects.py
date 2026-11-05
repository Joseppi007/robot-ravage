from enum import Enum

class Grid :
    def __init__(self, length, bredth) :
        self.length = length # width
        self.bredth = bredth # height
        self.cells = []
        self.robots = []
        for b in range(bredth) :
            self.cells.append([])
            for l in range(length) :
                self.cells[-1].append(None)
    def __str__(self) :
        s = "┏"+("━"*self.length)+"┓\n"
        for b in range(self.bredth) :
            s += "┃"
            for l in range(self.length) :
                cell = self.cells[b][l]
                if cell is None :
                    s += " "
                elif issubclass(type(cell), Robot) :
                    s += cell
                else :
                    s += "?"
            s += "┃\n"
        s += "┗"+("━"*self.length)+"┛"
        return s
    def get(position) :
        """
        Gets what is at some position. The grid is enclosed in walls.
        """
        if position.x < 0 or position.y < 0 or position.x >= self.length or position.y >= self.bredth :
            return Wall()
        return self.cells[position.y][position.x]

class Wall :
    def __init__(self) :
        pass
    def __eq__(self, other) :
        return issubclass(type(other), Wall)

class Position :
    def __init__(self, x, y) :
        self.x = x
        self.y = y
    def __str__(self) :
        return "<"+self.x+","+self.y+">"
    def __eq__(self, other) :
        if issubclass(type(other), Position) :
            return self.x == other.x and self.y == other.y
        else :
            return false
    def up(self) :
        return Position(self.x, self.y-1)
    def down(self) :
        return Position(self.x, self.y+1)
    def left(self) :
        return Position(self.x-1, self.y)
    def right(self) :
        return Position(self.x+1, self.y)
    def direction(direction) :
        match direction :
            case Direction.UP :
                return self.up()
            case Direction.DOWN :
                return self.down()
            case Direction.LEFT() :
                return self.left()
            case Direction.RIGHT() :
                return self.right()
            case _ :
                return Position(self.x, self.y)

class Target :
    def __init__(self) :
        pass
    def __str__(self) :
        return "Work in Progress"

class Direction(Enum) :
    STAY = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

class Robot :
    def __init__(self) :
        self.malicious = False
        self.network = None
        self.planned_movement = Direction.STAY
    def __str__(self) :
        if self.malicious :
            return "X"
        else :
            return "O"
    def send_message(self, reciever, content) :
        self.network.send_message(Message(self, reciever, content))
    def broadcast_message(self, content) :
        for member in self.network.group :
            if member == self :
                continue
            self.send_message(member, content)

class Message :
    def __init__(self, sender, reciever, content) :
        self.sender = sender
        self.reciever = reciever
        self.content = content

class Network :
    def __init__(self) :
        self.group = [] # List of Robot clients
        self.messages = [] # List of Messages
    def add_group_member(self, client) :
        self.group.append(client)
        client.network = self
    def send_message(self, message) :
        self.messages.append(message)
