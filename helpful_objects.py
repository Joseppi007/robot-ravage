from enum import Enum
import random

class Grid :
    def __init__(self, length, bredth) :
        self.length = length # width
        self.bredth = bredth # height
        self.cells = []
        self.robots = []
        target_position = Position.random(self.length, self.bredth)
        self.target = Target(target_position)
        self.network = Network()
        for b in range(bredth) :
            self.cells.append([])
            for l in range(length) :
                self.cells[-1].append(None)
        self.set(target_position, self.target)
    def __str__(self) :
        s = "┏"+("━"*self.length)+"┓\n"
        for b in range(self.bredth) :
            s += "┃"
            for l in range(self.length) :
                cell = self.cells[b][l]
                if cell is None :
                    s += " "
                elif issubclass(type(cell), Robot) :
                    s += str(cell)
                elif issubclass(type(cell), Target) :
                    s += "*"
                else :
                    s += "?"
            s += "┃\n"
        s += "┗"+("━"*self.length)+"┛"
        return s
    def get(self, position) :
        """
        Gets what is at some position. The grid is enclosed in walls.
        """
        if position.x < 0 or position.y < 0 or position.x >= self.length or position.y >= self.bredth :
            return Wall()
        return self.cells[position.y][position.x]
    def set(self, position, value) :
        """
        Attempts to place something at some position. Fails if occupied, even
        by a wall.
        """
        if self.get(position) is not None :
            e = Exception("Tried to place something at an occupied location of a grid.")
            e.add_note(f"There was a(n) {type(self.get(position))} in the way.")
            raise e
        self.force_set(position, value)
    def force_set(self, position, value) :
        self.cells[position.y][position.x] = value
    def move_bots(self) :
        """
        After all of the bots decide what they want to do, this function will
        move the bots all at once.
        """
        for robot in self.shuffled_bots() :
            if robot.planned_movement == Direction.STAY :
                continue
            old_position = robot.position
            new_position = old_position.direction(robot.planned_movement)
            robot.planned_movement = Direction.STAY
            self.force_set(old_position, None)
            self.set(new_position, robot)
            robot.position = new_position
        for robot in self.shuffled_bots() :
            robot.after_movement()
    def scatter_bots(self, number) :
        """
        Scatters some number of bots about the grid.
        """
        bots = []
        for i in range(number) :
            bots.append(Robot())
        self.scatter_list_of_bots(bots)
    def scatter_list_of_bots(self, bots) :
        """
        If you want to subclass the bots to give them unique behavior, this is
        the method for you. You can make one of the bots a coordinator if you'd
        like. You can do anything. Welcome to zombo.com.
        """
        b = []
        for bot in bots :
            b.append(bot)
        while True :
            if len(b) == 0 :
                return
            p = Position.random(self.length, self.bredth)
            if self.get(p) is not None :
                continue
            r = b.pop()
            r.position = p
            self.set(p, r)
            r.grid = self
            self.network.add_group_member(r)
            self.robots.append(r)
    def loop_until_done(self, debug=False) :
        """
        Goes between the messaging phase and movement phase over and over
        until the target is surrounded.
        Debugging prints out the grid after each movement phase and at the
        very beginning of the algorithm.
        """
        if debug :
            print(self)
        for bot in self.shuffled_bots() :
            bot.on_startup()
        while not self.is_target_surrounded() :
            self.move_bots()
            self.network.handle_messages()
            if debug :
                print(self)
    def is_target_surrounded(self) :
        """
        Checks if the target is surrounded. A target against a wall is
        surrounded on the walled off side.
        """
        p = self.target.position
        u = self.get(p.up()) is not None
        d = self.get(p.down()) is not None
        l = self.get(p.left()) is not None
        r = self.get(p.right()) is not None
        return u and d and l and r
    def shuffled_bots(self) :
        """
        Shuffles the bots to be more stocastic.
        Feels networkier that way.
        """
        bots = [r for r in self.robots]
        random.shuffle(bots)
        return bots

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
    def direction(self, direction) :
        match direction :
            case Direction.UP :
                return self.up()
            case Direction.DOWN :
                return self.down()
            case Direction.LEFT :
                return self.left()
            case Direction.RIGHT :
                return self.right()
            case Direction.STAY :
                return Position(self.x, self.y)
            case _ :
                raise Exception(f"Position.direction cannot handle {direction}.")
    def random(width, height) :
        return Position(random.randint(0, width-1), random.randint(0, height-1))

class Target :
    def __init__(self, position) :
        self.position = position
    def __str__(self) :
        return self.position

class Direction(Enum) :
    STAY = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
    def random() :
        return random.choice([Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT])

class Robot :
    def __init__(self) :
        self.malicious = False
        self.network = None
        self.grid = None
        self.position = None
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
    def after_movement(self) :
        """
        This method is called after movement is performed.
        """
        pass
        # if random.randint(1, 100) == 1:
        #     self.planned_movement = Direction.random()
    def on_startup(self) :
        """
        This method is called at the beginning of the algorithm, before any
        movement occurs.
        """
        pass
        # if random.randint(1, 100) == 1:
        #     self.planned_movement = Direction.random()
    def on_messaged(self, message) :
        """
        This method is called when a message is recieved.
        """
        pass

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
    def handle_messages(self) :
        """
        Goes through the messages in a random order. Does no processing, just
        shuffles and notifies.
        """
        while len(self.messages) > 0 :
            idx = random.randint(0, len(self.messages)-1)
            m = self.messages.pop(idx)
            m.reciever.on_messaged(m)
