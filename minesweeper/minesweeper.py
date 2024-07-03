import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        mines_discovered = set()

        # All the cells from a sentence with the same number of cells as the count number are known to be mines
        if len(self.cells) == self.count and len(self.cells) > 0:
            for mine in self.cells:
                mines_discovered.add(mine)

            return mines_discovered

        return None


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        # All the cells from a sentence with a count number equal to zero are known to be safe
        safe_discovered = set()
        if self.count == 0 and len(self.cells) > 0:
            for safe in self.cells:
                safe_discovered.add(safe)

            return safe_discovered

        return None


    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        # Update the sentence removing the mine if the mine is in the sentence, lower the count number as well
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

        # If the count number has been lower down to or equal to zero in the process, limit the count number to be as low as zero.
        self.count = max(self.count, 0)


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        # remove every cell marked as safe if it is inside the sentence
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

        # List of possible random spaces
        # self.possible_move is a matrix with every space unknown available. Everytime that a safe cell or a mine is discovered, that position is removed.
        self.possible_move = []
        for i in range(self.width):
            for j in range(self.height):
                self.possible_move.append((i,j))

        # List of possible safe spaces
        self.safe_move = []


    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # 1 mark the cell as a move that has been made
        self.moves_made.add(cell)
        self.possible_move.remove(cell)

        if cell in self.safe_move:
            self.safe_move.remove(cell)

        if cell in self.possible_move:
            self.possible_move.remove(cell)

        # 2 mark the cell as safe
        self.mark_safe(cell)

        # 3 add a new sentence to the AI's knowledge base, based on the value of `cell` and `count`

        # Set the limit for the window of neighbours
        limit_min = 0
        limit_max_x = self.width - 1
        limit_max_y = self.height - 1

        new_sentence = set()
        mines_counter = 0

        # Collect information about the cells neighboring the cell that has just been moved in, in order to make a new sentence
        for i in range(3):
            for j in range(3):
                nb_x = cell[0] - 1 + i
                nb_y = cell[1] - 1 + j
                neighbour = (nb_x, nb_y)

                # Omit the neighbour cell if that cell is out of the board or if the neighbour cell is the same as the cell
                if limit_min <= nb_x <= limit_max_x and limit_min <= nb_y <= limit_max_y and neighbour != cell:
                    if neighbour in self.mines:
                        mines_counter += 1
                    # Omit the neightbour cell if it is known to be a mine or a safe
                    if neighbour not in self.mines and neighbour not in self.safes:
                        new_sentence.add((nb_x, nb_y))

        # Omit the mines known
        new_count = count - mines_counter

        # Create the sentence and add it to the knowledge
        created_sentence = Sentence(new_sentence, new_count)
        self.knowledge.append(created_sentence)

        # 4 mark any additional cells as safe or as mines

        # Loop throught until no change in knowledge is detected
        change = True
        while change:

            change = False
            remove_sentence = []

            # Check every sentence in knowledge
            for i, sentence in enumerate(self.knowledge, start=0):

                # If a sentence in knowledge is empty, remove it
                if len(sentence.cells) == 0:
                    remove_sentence.append(i)

                else:
                    # If the cells in the sentence is known to be mines, proceed to mark them
                    if sentence.known_mines() is not None:
                        for mine_cell in sentence.known_mines():
                            self.mark_mine(mine_cell)
                            self.possible_move.remove(mine_cell)

                    # If the cells in the sentence is known to be safe, proceed to mark them
                    if sentence.known_safes() is not None:
                        remove_sentence.append(i)
                        for safe_cell in sentence.known_safes():
                            self.safe_move.append(safe_cell)
                            self.mark_safe(safe_cell)

            # If there is a sentence to be remove, the list remove_sentence track the sentences to be removed
            if len(remove_sentence) > 0:
                counter = 0
                for position in remove_sentence:
                    self.knowledge.pop(position - counter)
                    counter += 1

            # 5 add any new sentences to the AI's knowledge base
            len_knowledge = len(self.knowledge)

            # Compare every sentence in knowledge against each other in order to infer more information
            for i in range(len_knowledge):
                for j in range(len_knowledge):
                    # Omit self-comparisons of sentences
                    if i != j:
                        set1_cells = self.knowledge[i].cells
                        set2_cells = self.knowledge[j].cells
                        set1_count = self.knowledge[i].count
                        set2_count = self.knowledge[j].count

                        # If there is a sentence that is a complete subset of any other senteces, create a new sentences out of it. Omit equal sentences.
                        if set1_cells.issubset(set2_cells) and len(set1_cells) > 0 and len(set2_cells) > 0 and len(set1_cells) != len(set2_cells):
                            const_sent_cell = set2_cells.difference(set1_cells)
                            const_sent_count = set2_count - set1_count

                            # Zero is the lowest count number
                            const_sent_count = max(const_sent_count, 0)

                            # Break and avoid adding empty sentences
                            if len(const_sent_cell) == 0:
                                break

                            # Add the new infered sentence in the knowledge and keep looping
                            const_sent = Sentence(const_sent_cell, const_sent_count)
                            self.knowledge.append(const_sent)
                            change = True


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        num_safe_move = len(self.safe_move)

        # If a safe cell is available choose one. Otherwise, return None
        if num_safe_move > 0:
            for i in range(num_safe_move):
                move = self.safe_move[i]
                if move not in self.mines and move not in self.moves_made:
                    return move

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # If a random cell is available choose one. Otherwise, return None.
        # self.possible_move is a matrix with every space unknown available. Everytime that a safe cell or a mine is discovered, that position is removed.
        if len(self.possible_move) > 0:
            random_move = random.choice(self.possible_move)

            if random_move not in self.mines and random_move not in self.moves_made:
                return random_move

        return None
