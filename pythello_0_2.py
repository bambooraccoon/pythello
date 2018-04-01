import copy
import random

class Board(object):
    dirs = [(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
    
    # weight format (piece_diff, stables, wedges, mobility)
    weights = [
            (3, 10, 5, 5),
            (2, 8, 3, 8)]

    def __init__(self, board = None, size = 8):
        if size % 2 == 1 or size < 4 or size > 26:
            self.size = 8
        else:
            self.size = size

        if board is None:
            self.value = [None, None]
            self.squares = []
            for i in range(self.size):
                self.squares.append([])
                for j in range(self.size):
                    self.squares[i].append(0) 
                     
            middle_x = int(self.size / 2)
            middle_y = int(self.size / 2)
            self.squares[middle_x][middle_y] = 2
            self.squares[middle_x-1][middle_y-1] = 2
            self.squares[middle_x-1][middle_y] = 1
            self.squares[middle_x][middle_y-1] = 1

            self.piece_count = [self.size * self.size - 4, 2, 2]
            self.turn = 1
            self.history = ""
            self.stables = {1: set(), 2: set()}
            self.wedges = {1: set(), 2: set()}
            self.legal_moves = self.get_legal_moves()

        else:
            self.size = board.size
            self.squares = copy.deepcopy(board.squares)
            self.piece_count = copy.deepcopy(board.piece_count)
            self.history = copy.deepcopy(board.history)
            self.value = copy.deepcopy(board.value)
            self.stables = copy.deepcopy(board.stables)
            self.wedges = copy.deepcopy(board.wedges)
            self.turn = board.turn
            self.legal_moves = copy.deepcopy(board.legal_moves)

    def is_legal_move(self, move):
        x = Board.get_x(move)
        y = Board.get_y(move)
        if self.squares[x][y] > 0:
            return False
        
        for d in Board.dirs:
            cursor_x = x + d[0]
            cursor_y = y + d[1]
            
            if self.get_square(cursor_x, cursor_y) == self.turn ^ 3:
                while self.get_square(cursor_x, cursor_y) == self.turn ^ 3:
                    cursor_x += d[0]
                    cursor_y += d[1]
                if self.get_square(cursor_x, cursor_y) == self.turn:
                    return True
        return False

    def get_square(self, x, y):
        if x < 0 or x > 7 or y < 0 or y > 7:
            return -1
        else:
            return self.squares[x][y]

    def get_legal_moves(self):
        legal_moves = []
        for i in range(self.size):
            for j in range(self.size):
                if self.is_legal_move(Board.get_move(i, j)):
                    legal_moves.append(Board.get_move(i, j))
        if len(legal_moves) == 0:
            legal_moves = ["__"]
        return legal_moves

    def do_move(self, move):
        if move != "__":
            x = Board.get_x(move)
            y = Board.get_y(move)
            will_flip = []

            for i in range(8):
                d = self.dirs[i]
                cursor_x = x + d[0]
                cursor_y = y + d[1]
                
                if self.get_square(cursor_x, cursor_y) == self.turn ^ 3:
                    while self.get_square(cursor_x, cursor_y) == self.turn ^ 3:
                        cursor_x += d[0]
                        cursor_y += d[1]
                    if self.get_square(cursor_x, cursor_y) == self.turn:
                        rd = self.dirs[(i + 4) % 8]
                        cursor_x += rd[0]
                        cursor_y += rd[1]
                        while self.get_square(cursor_x, cursor_y) == self.turn ^ 3:
                            will_flip.append((cursor_x, cursor_y))
                            cursor_x += rd[0]
                            cursor_y += rd[1]

            for square in will_flip:
                self.squares[square[0]][square[1]] = self.turn
                self.piece_count[self.turn ^ 3] -= 1
                self.piece_count[self.turn] += 1

            self.squares[x][y] = self.turn
            self.piece_count[self.turn] += 1

        self.history += move
        self.turn = self.turn ^ 3
        self.legal_moves = self.get_legal_moves()

    def get_piece_diff(self):
        return self.piece_count[self.turn] - self.piece_count[self.turn ^ 3]
    
    # weight format (piece_diff, stables, wedges, mobility)
    def get_instant_value(self, weights):
        return (self.get_piece_diff() * weights[0] 
                + len(self.stables[self.turn]) * weights[1]
                + len(self.wedges[self.turn]) * weights[2]
                + len(self.legal_moves) * weights[3])

    def check_stables(self):
        dirs = ((1, 0), (0, 1), (-1, 0), (0, -1)) 
        corners = ((0, 0), (self.size - 1, 0), (self.size - 1, self.size - 1),
                (0, self.size -1 ))

        # Loop through starting from each corner
        for i in range(4):
            to_check = [corners[i]]
            checked = []

            while len(to_check) > 0:
                checking = to_check.pop(0)
               
                if (get_square(checking[0], checking[1]) != self.turn or
                        checking in checked):
                    useless = 0

                elif checking in self.stables[self.turn]:
                    to_check.append(Board.move_square(checking, dirs[i]))
                    to_check.append(Board.move_square(checking, dirs[(i + 1) % 4]))

                elif self.get_square(checking[0], checking[1]) == self.turn:
                    if (Board.move_square(checking, dirs[i]) in
                        self.stables[self.turn] and
                        Board.move_square(checking, dirs[(i + 1) % 4]) in
                        self.stables[self.turn]):
                        # Current square is newly stable!
                        self.stables[self.turn].append(checking)
                        to_check.append(Board.move_square(checking, dirs[i]))
                        to_check.append(Board.move_square(checking, dirs[(i + 1) % 4]))

                checked.append(checking)

    @staticmethod
    def move_square(square, direction):
        return (square[0] + direction[0], square[1] + direction[1])

    @staticmethod
    def get_x(move):
        return ord(move[0]) - 97 

    @staticmethod
    def get_y(move):
        return int(move[1]) - 1

    @staticmethod
    def get_move(x, y):
        return chr(x + 97) + str(y + 1)

class Game(object):

    def __init__(self):
        self.boards = {}
        self.max_depth = 4
        
    def new_game(self):
        self.boards[""] = Board()
        self.current_board = ""
        self.running = True
        self.skipped_turns = 0
        self.look_ahead(self.current_board, self.max_depth)

    def do_move(self, move):
        self.current_board += move
        self.look_ahead(self.current_board, self.max_depth)
        
    def look_ahead(self, board_history, depth):
        if board_history not in self.boards:
            board = Board(self.boards[board_history[:-2]])
            self.boards[board_history] = board 
            board.do_move(board_history[-2:])
        else:
            board = self.boards[board_history]

        if depth == 0:
            board.value[0] = board.get_instant_value(Board.weights[0])
            board.value[1] = board.get_instant_value(Board.weights[1])
            return board.value

        elif board.piece_count[1] + board.piece_count[2] == 64 or board_history[-4:] == "____":
            return (board.piece_count[self.turn] - board.piece_count[self.turn^3]) * 1000

        else:
            board.value = [None, None]
            board.best_move = [None, None] 
            for move in board.legal_moves:
                val = self.look_ahead(board_history + move, depth - 1)

                if board.best_move[0] is None:
                    board.value = val
                    board.best_move = [move, move]
                else:
                    if val[0] > board.value[0]:
                        board.value[0] = val[0]
                        board.best_move[0] = move
                    if val[1] > board.value[1]:
                        board.value[1] = val[1]
                        board.best_move[1] = move
            return board.value
                    

    def run_game(self):
        queue = []
        skipped = 0
        while self.running:
            cboard = self.boards[self.current_board]
            Display.show_board(cboard)

            if len(cboard.legal_moves) == 0:
                skipped += 1
                queue.pop(0)
                if skipped == 2:
                    self.running = False
            else:
                skipped = 0
            
                if len(queue) == 0:
                    command = Display.get_input()
                else:
                    command = queue.pop(0)
                    if command == "":
                        command = Display.get_input()

                command = command.split()

                if len(command) == 0:
                    Display.show_help()

                elif command[0] == "exit":
                    running = False

                elif command[0] == "ai":
                    if len(queue) > 0:
                        queue.insert(1, "ai")
                    else:
                        queue = ["", "ai"]
                    move = cboard.best_move[cboard.turn - 1]
                    Display.show_ai_move(move)
                    self.do_move(move)
                
                elif command[0][0] in "abcdefgh" and command[0][1] in "12345678":
                    self.do_move(command[0][0:2])

                elif command[0] == "help":
                    Display.show_help()

                else:
                    print("Bad command. Enter 'help' for help or 'exit' to exit.")
            

class Display(object):
    graphics = {0: "*", 1: "B", 2: "W"}

    @staticmethod
    def show_board(board):
        line = " "
        for i in range(board.size):
            line += "  " + chr(i + 97)
        print(line + "\n")

        for j in range(board.size):
            line = str(j + 1) 
            while len(line) < 3:
                line += " "
            for i in range(board.size): 
                line += Display.graphics[board.get_square(i, j)] + "  "
            print(line + "\n")

        line = "B:" + str(board.piece_count[1]) + ", W:" + str(board.piece_count[2])
        if len(board.get_legal_moves()) == 0:
            line += ", Game over"
        else:
            line += ", " + Display.graphics[board.turn] + " to play...\n"
            line += "Legal moves: " + str(board.get_legal_moves())
        print(line)

    @staticmethod
    def show_ai_move(move):
        print("AI played " + move)

    @staticmethod
    def get_input():
        user_input = input(">> ")
        return user_input

    @staticmethod
    def show_help():
        print("Help is not yet implemented! Ask Simon or look at the code.")

# Deprecated
class GameX(object):
    def __init__(self, size, p1, p2):
        self.board = Board()
        self.players = {1: p1, 2: p2}

    def play(self):
        while len(self.board.get_legal_moves()) > 0:
            Display.show_board(self.board)
            if self.players[self.board.turn] == "human":
                command = Display.get_input()
                next_move = command 
            else:
                next_move = AI.get_move(self.board, self.players[self.board.turn])
            self.board.do_move(next_move)
        Display.show_board(self.board)

class AI(object):
    @staticmethod
    def get_move(board, ai):
        if ai == "greedy":
            best_diff = -64
            for m in board.legal_moves:
                next_board = Board(board)
                next_board.do_move(m)
                
                if next_board.get_piece_diff() > best_diff:
                    move = m
                    best_diff = next_board.get_piece_diff()
        else:
            move = random.choice(board.legal_moves)
        return (move)

# game = GameX(8, "random", "greedy")
# game.play()

game = Game()
game.new_game()
game.run_game()
