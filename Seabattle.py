# imports random module 
import random

# Constants
W = 6
H = 6
empty_sym = 'O'
ship_sym = '■'
kill_sym = 'X'
miss_sym = 'T'


class BadShipPlacementException(Exception):
    def __init__(self, placement):
        self.placement = placement

    def __str__(self):
        return 'Bad ship placement (%d, %d)' % self.placement


class BadShipException(Exception):
    def __init__(self, points):
        self.points = points

    def __str__(self):
        return 'Bad ship: %s' % self.points


class BrokenShipException(BadShipException):
    def __str__(self):
        return 'Broken ship: %s' % self.points


class Ship:
    points = []

    def __init__(self, points):
        if len(self.points) != len(set(self.points)):  # Some elements are equal
            raise BadShipException(points)
        self.points = [(p[1] - 1, p[0] - 1) for p in points]
        min_y = min(p[0] for p in self.points)
        min_x = min(p[1] for p in self.points)
        max_y = max(p[0] for p in self.points)
        max_x = max(p[1] for p in self.points)
        w = max_x - min_x + 1  # Ship width
        h = max_y - min_y + 1  # Ship height
        if w != 1: w, h = h, w
        # Now w should be 1
        if w != 1 or h != len(points):
            raise BrokenShipException(points)

    def make_random_ship(length):
        # Assume horizontal
        points = []  # [(2, 4), (2, 5), (2, 6)]
        x = random.randint(1, 7 - length)
        y = random.randint(1, 6)
        points = [(x + i, y) for i in range(length)]
        # Maybe flip horizontal -> vertical (50% probability)
        if random.randint(0, 1) == 0:
            points = [(p[1], p[0]) for p in points]
        return Ship(points)


class Board:
    ships = []
    m = []

    def __init__(self, ships):
        self.ships = ships.copy()
        self.m = []
        for i in range(H):
            self.m.append([empty_sym] * W)
        for ship in ships:
            self.add_ship(ship)

    def add_ship(self, ship):
        # Check neighbours
        for p in ship.points:
            if self.has_neighbour(p[1], p[0]):
                raise BadShipPlacementException(p)
        # Place ship
        for p in ship.points:
            self.m[p[0]][p[1]] = ship_sym

    def make_random_board():
        b = Board([])
        needed_ships = (3, 2, 2, 1, 1, 1, 1)
        i = 1
        for length in needed_ships:
            while True:
                ship = Ship.make_random_ship(length)
                try:
                    b.add_ship(ship)
                    i += 1
                    break
                except BadShipPlacementException as e:
                    pass
        return b

    def ship_here(self, x, y):
        return x >= 0 and x < W and y >= 0 and y < H and self.m[y][x] == ship_sym

    def has_neighbour(self, x, y):
        offsets = [(0, 0), (-1, 0), (0, -1), (1, 0), (0, 1)]
        for offset in offsets:
            x1 = x + offset[0]
            y1 = y + offset[1]
            if self.ship_here(x1, y1):
                return True
        return False

    def show(self, msg, hide_ships):
        print(msg)
        print('     ', '  '.join(map(str, [i + 1 for i in range(W)])))
        print('   ', '_' * (W * 3 + 1))
        print('   |')
        for i, row in enumerate(self.m):
            print('', i + 1, '|', end='')
            for sym in row:
                print(' ', 'O' if hide_ships and sym == ship_sym else sym, end='')
            print()
            print('   |')
        print()

    def can_fire(self, x, y):
        return not self.m[y][x] in [kill_sym, miss_sym]

    def has_live_ships(self):
        for row in self.m:
            for sym in row:
                if sym == ship_sym:
                    return True
        return False

    def fire(self, x, y):
        sym = self.m[y][x]
        if sym == empty_sym:
            self.m[y][x] = miss_sym
            return "misses"
        elif sym == ship_sym:
            self.m[y][x] = kill_sym
            return "hits"
        else:
            raise Exception('Firing went wrong!')


class Game:
    # Boards
    game_over = False
    player = None
    comp = None
    winner = ''  # Who won

    def __init__(self):
        try:
            self.player = Board([  # Ship([(X, Y)]), one-based
                Ship([(4, 1), (6, 1), (5, 1)]),
                Ship([(2, 5), (2, 6)]),
                Ship([(4, 5), (4, 6)]),
                Ship([(1, 2)]),
                Ship([(3, 3)]),
                Ship([(6, 6)]),
                Ship([(6, 4)]),
            ])
            # self.player = Board.make_random_board()
            self.comp = Board.make_random_board()
            self.run()
        except Exception as e:
            print(e)

    def read_int(self, what, begin, end):
        n = -1
        while n < begin or n > end:
            s = input('Input %s: ' % what)
            if s.lower() in ['q', 'quit', 'exit', '-1']:
                raise Exception('Game halted')
            try:
                n = int(s)
            except ValueError:
                print('Not a number')
        return n

    def go_player(self):
        self.player.show('Player:', False)
        self.comp.show('Computer:', True)
        print('Your turn.')
        while True:
            x = self.read_int('X', 1, W) - 1
            y = self.read_int('Y', 1, H) - 1

            if self.comp.can_fire(x, y): break

            print('You can not fire there.')

        result = self.comp.fire(x, y)
        print('Player fires at (%d, %d) and %s.' % (x + 1, y + 1, result))

        if not self.comp.has_live_ships():
            self.game_over = True
            self.winner = 'Player'

    def go_comp(self):
        print('Computer\'s turn.')
        while True:
            x = random.randint(0, 5)
            y = random.randint(0, 5)
            if self.player.can_fire(x, y): break

        result = self.player.fire(x, y)
        print('Computer fires at (%d, %d) and %s.' % (x + 1, y + 1, result))

        if not self.player.has_live_ships():
            self.game_over = True
            self.winner = 'Computer'

    def run(self):
        self.game_over = False
        try:
            while not self.game_over:
                self.go_player()
                if not self.game_over:
                    self.go_comp()
            print(self.winner, 'won!')
        except Exception as ex:
            print(ex)


Game()
