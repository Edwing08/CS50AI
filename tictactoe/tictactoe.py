"""
Tic Tac Toe Player
"""

from copy import deepcopy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Keep a counter of how many times each player has made a move
    counter_x = 0
    counter_o = 0

    # If the board is empty then X starts
    if board is None:
        return X

    # Count how many times each player has moved
    for row in board:
        for cell in row:
            if cell == X:
                counter_x += 1
            elif cell == O:
                counter_o += 1

    # If X has more move than O then it's O's turn. Otherwise, it's X's turn.
    if counter_x > counter_o:
        return O

    return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Keep a set to store the possible actions
    num_actions = set()

    # If an empty cell is found, save that position in the possible actions set
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                num_actions.add((i,j))

    return num_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # If an action contains a move out of the board, rise and error
    for element in action:
        if not 0 <= element <= 2:
            raise ValueError

    # Determine the current player moving
    turn = player(board)

    # Copy the board and finally make the move in the board copied
    board_copied = deepcopy(board)
    board_copied[action[0]][action[1]] = turn

    return board_copied


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    size = len(board)

    # Place to store rows, columns and diagonals from the current state of the board
    rows_winner = []
    diagonals = [[],[]]

    for i in range(size):

        columns = []
        for j in range(size):
            # Column
            columns.append(board[j][i])

            # Diagonal from left to right
            if i == j:
                diagonals[0].append(board[i][j])
            # Diagonal from right to left
            if j == size - i - 1:
                diagonals[1].append(board[i][j])

        # Adds the rows in one single list
        rows_winner.append(columns)

    # Adds the rows in one single list
    for rows in board:
        rows_winner.append(rows)

    # Adds the diagonals in one single list
    for rows in diagonals:
        rows_winner.append(rows)

    # Analize all posible winning combinations
    for rows in rows_winner:
        for i in range(len(rows) - 1):
            if not rows[i] == rows[i + 1]:
                break
            if i == (len(rows) - 2):
                final_winner = rows[0]
                return final_winner

    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    possible_winner = winner(board)

    # The game is over if there is a winner
    if possible_winner:
        return True

    cell_available = False

    # The game is not over if are empty cells available
    for rows in board:
        for element in rows:
            if element == EMPTY:
                cell_available = True

    if cell_available is False:
        return True

    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    possible_winner = winner(board)

    # if X is the winner, then the utility is 1
    if possible_winner == X:
        return 1
    # if O is the winner, then the utility is -1
    if possible_winner == O:
        return -1

    # if it's a tie, then the utility is 0
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Return none is the game is over
    if terminal(board):
        return None

    current_turn = player(board)

    # Place to store the utility and the actions
    options = [[],[]]

    # maximizing player
    if current_turn == X:
        for action in actions(board):
            options[0].append(minvalue(result(board,action)))
            options[1].append(action)
        # Obtain the maximum utility from every action
        maxi = max(options[0])
        for i in range(len(options[0])):
            # Select one action that have the optimal utility
            if options[0][i] == maxi:
                return options[1][i]

    # minimizing player
    elif current_turn == O:
        for action in actions(board):
            options[0].append(maxvalue(result(board,action)))
            options[1].append(action)
        # Obtain the minimum utility from every action
        mini = min(options[0])
        for i in range(len(options[0])):
            # Select one action that have the optimal utility
            if options[0][i] == mini:
                return options[1][i]

    return None

def maxvalue(state):
    """
    choose the maximum value from the minimum value chosen by the opponent
    """
    value = -math.inf

    if terminal(state):
        return utility(state)

    # Go through every action and selects the maximum value from the minumum value selected by the oponent in the round ahead
    for action in actions(state):
        value = max(value,minvalue(result(state, action)))
    return value

def minvalue(state):
    """
    choose the minimum value from the maximum value chosen by the opponent
    """
    value = math.inf

    if terminal(state):
        return utility(state)

    # Go through every action and selects the minumum value from the maximum value selected by the oponent in the round ahead
    for action in actions(state):
        value = min(value,maxvalue(result(state, action)))
    return value
