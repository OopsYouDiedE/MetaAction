import random


class Board:
    def __init__(self, size=15):
        self.size = size
        self.board = [[' ' for _ in range(size)] for _ in range(size)]
        self.current_player = 'X'

    def copy(self):
        new_board = Board(self.size)
        new_board.board = [row.copy() for row in self.board]
        new_board.current_player = self.current_player
        return new_board

    def get_legal_moves(self):
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.board[r][c] == ' ']

    def place_stone(self, row, col, player):
        if self.board[row][col] == ' ':
            self.board[row][col] = player
            return True
        return False

    def is_win(self, row, col, player):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1
            for i in range(1, 5):
                x, y = row + dx*i, col + dy*i
                if 0 <= x < self.size and 0 <= y < self.size and self.board[x][y] == player:
                    count += 1
                else:
                    break
            for i in range(1, 5):
                x, y = row - dx*i, col - dy*i
                if 0 <= x < self.size and 0 <= y < self.size and self.board[x][y] == player:
                    count += 1
                else:
                    break
            if count >= 5:
                return True
        return False

    def print_board(self):
        print("   " + " ".join(f"{i:2}" for i in range(self.size)))
        for i, row in enumerate(self.board):
            print(f"{i:2} " + " ".join(f"{cell:2}" for cell in row))


class RandomAI:
    def __init__(self, player):
        self.player = player

    def get_move(self, board):
        return random.choice(board.get_legal_moves())


class SmartAI:
    def __init__(self, player):
        self.player = player

    def get_move(self, board):
        # 立即获胜检测
        for move in board.get_legal_moves():
            new_board = board.copy()
            new_board.place_stone(*move, self.player)
            if new_board.is_win(*move, self.player):
                return move

        # 阻止对手获胜
        opponent = 'O' if self.player == 'X' else 'X'
        for move in board.get_legal_moves():
            new_board = board.copy()
            new_board.place_stone(*move, opponent)
            if new_board.is_win(*move, opponent):
                return move

        # 启发式评估
        best_score = -1
        best_moves = []
        center = (15//2, 15//2)

        for move in board.get_legal_moves():
            r, c = move
            # 中心优先
            center_score = 14 - (abs(r-center[0]) + abs(c-center[1]))

            # 邻近棋子评估
            neighbor_score = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < 15 and 0 <= nc < 15:
                        if board.board[nr][nc] == self.player:
                            neighbor_score += 3

            total = center_score + neighbor_score
            if total > best_score:
                best_score = total
                best_moves = [move]
            elif total == best_score:
                best_moves.append(move)

        return random.choice(best_moves)


def main():
    board = Board()
    ai_black = SmartAI('X')
    ai_white = SmartAI('O')

    while True:
        current_ai = ai_black if board.current_player == 'X' else ai_white
        move = current_ai.get_move(board)

        if not board.place_stone(*move, board.current_player):
            print("Invalid move! Game over.")
            break

        print(f"{board.current_player} places at {move}")
        board.print_board()

        if board.is_win(*move, board.current_player):
            print(f"Player {board.current_player} wins!")
            break

        if not board.get_legal_moves():
            print("Game ends in draw!")
            break

        board.current_player = 'O' if board.current_player == 'X' else 'X'


if __name__ == "__main__":
    main()
