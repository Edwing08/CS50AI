from ctypes.wintypes import WORD
from os import remove
from re import A
import sys

from crossword import *

def obtain_list_min(array, mini):
    """
    Obtain the minimum or maximum values from a list
    """
    list_len = len(array)

    if list_len > 1:

        if mini:
            min_or_max_number = min(array, key = lambda tuple: tuple[1])[1]
        else:
            min_or_max_number = max(array, key = lambda tuple: tuple[1])[1]

        result = []
        
        for number in array:
            if number[1] == min_or_max_number:
                result.append(number)

    return result


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        
        # Go throught the domain in each variable
        for variable in self.domains:
            
            # Copy the words inside the domain from the variable
            variable_domain = self.domains[variable].copy()
            
            # Check each word in the domain of the variable and delete words whose length is not suitable for the variable
            for word in variable_domain:
                word_length = len(word)
                if word_length != variable.length:
                    self.domains[variable].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        revised = False 

        # Obtain the domain content of the variables to be revised
        x_variable_domain = self.domains[x].copy()
        y_variable_domain = self.domains[y]

        # Obtain the position where the two variables overlaps
        overlap = self.crossword.overlaps[x, y]

        # Check each word in the first variable domain and compare it to each word in the second variable domain
        for word_x in x_variable_domain:
            saved = False
            for word_y in y_variable_domain:

                # Make sure the letter is the same in the position where both variables overlap
                if word_x[overlap[0]] == word_y[overlap[1]]:
                    saved = True
            
            # Remove the word from the variable domain if the overlap letter does not match any word in the over variable
            if not saved:
                self.domains[x].remove(word_x)
                revised = True

        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue_list = []

        # Get the neighbours of each variable and store them in a list of tuples
        if arcs is None:
            for variable in self.domains:
                for variable_neighbor in self.crossword.neighbors(variable):
                    queue_list.append((variable, variable_neighbor))

        # Check if each variable is arc consistent, repeat until the queue list is empty
        while (queue_list):
            
            # Revise arc consistency of one variable from the list with its neightbours
            x, y = queue_list.pop(0)
            if self.revise(x, y):

                if x.length == 0:
                    return False
                
                # Add an additional arc in case there is a change in the previously revised domain variable 
                for z in self.crossword.neighbors(x):
                    if z is not y:
                        queue_list.append((z,x))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        complete = False

        variable_count = 0

        # Check that each variable has a word assigned to it
        for variable, values in assignment.items():
            if variable is not None and values is not None:
                variable_count += 1
            
        if variable_count == len(self.domains):
            complete = True
                
        return complete


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Check that each word assigned to each variable is consistent
        for variable in assignment:

            # Check that the word's length match the variable slots available
            if len(assignment[variable]) == variable.length:

                # Check the word assigned does not generate conflict with its neighbours
                for neighbor in self.crossword.neighbors(variable):

                    # Ignore if a neighbour from the variable is not assigned yet
                    if neighbor not in assignment.keys():
                        continue
                    else:
                        # The same word must not be assigned in more than one variable  
                        if assignment[variable] == assignment[neighbor]:
                            return False

                        overlap = self.crossword.overlaps[variable, neighbor]
                        
                        # The word must have the same letter as its neighbor in the overlapping position
                        if assignment[variable][overlap[0]] != assignment[neighbor][overlap[1]]:
                            return False
        
            else:
                return False
        
        return True
            

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        words = []
        words_var = self.domains[var]
        words_var_tuple = []

        # Store each word from the variable domain with a counter in a list
        for word in words_var:
            words_var_tuple.append([word, int(0)])

        # Check how many words are ruled out among the neighbours due to the selection of an specific word from the domain of the variable
        for neighbor in self.crossword.neighbors(var):
            if neighbor not in assignment.keys():

                words_nei = self.domains[neighbor]
                overlap = self.crossword.overlaps[var, neighbor]

                for word_var_tuple in words_var_tuple:
                    for word_nei in words_nei:

                        if word_var_tuple[0] == word_nei:
                            word_var_tuple[1] = word_var_tuple[1] + 1

                        if word_var_tuple[0][overlap[0]] != word_nei[overlap[1]]:
                            word_var_tuple[1] = word_var_tuple[1] + 1

        # Sort from lowest to highest number of words ruled out by each word
        words_var_tuple_sorted = sorted(words_var_tuple, key=lambda n:n[1])
        for i in range(len(words_var_tuple_sorted)):
            words.append(words_var_tuple_sorted[i][0])

        return words

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # Store each variable, the number of words in each variable domain and the number of neighbors of each variable in a list
        unassigned_variables = [[],[],[]]
        index_position = 0

        for variable in self.domains:
            if variable not in assignment:
                unassigned_variables[0].append(variable)
                unassigned_variables[1].append((index_position, len(self.domains[variable])))
                unassigned_variables[2].append((index_position, len(self.crossword.neighbors(variable))))
                index_position += 1

        
        len_unassined = len(unassigned_variables[0])
        
        # If the number of unassined variables is higher than 1
        if len_unassined > 1:

            # Obtain the variables with the lowest number of words
            list_unassigned_var = unassigned_variables[1]
            result_list_var = obtain_list_min(list_unassigned_var, True)
            len_list_var = len(result_list_var)

            # if there are more than one variable whose number of words correspont to the lowest value
            if len_list_var > 1:
                list_unassigned_var_nei = []

                for i in range(len(result_list_var)):
                    list_unassigned_var_nei.append(unassigned_variables[2][result_list_var[i][0]])

                # Obtain the variable with highest number of neighbours
                result_list_nei = obtain_list_min(list_unassigned_var_nei, False)

                # The assigned variable should be the one that has the lowest number of words available and the highest number of neighbours among the others
                assigned_variable_index = result_list_nei[0][0]
                assigned_variable = unassigned_variables[0][assigned_variable_index]

            else:
                assigned_variable_index = result_list_var[0][0]
                assigned_variable = unassigned_variables[0][assigned_variable_index]

        else:
            assigned_variable = unassigned_variables[0][0]

        return assigned_variable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if self.assignment_complete(assignment):
            return assignment
        
        # Select an unassigned variable
        var = self.select_unassigned_variable(assignment)
        
        # Select a word from the variable domain and check if it is suitable for assignment
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value

            # Determine whether the candidate to be assigned is consistent regarding the constraints and assign it
            if self.consistent(new_assignment):
                assignment[var] = value
                result = self.backtrack(assignment)

                if result is not None:
                    return result

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
