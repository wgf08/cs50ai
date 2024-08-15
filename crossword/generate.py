import sys
from crossword import *
import collections
import math

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
        for x in self.domains.keys():
            copyDomain = self.domains[x].copy()
            for y in copyDomain:
                if x.length == len(y):
                    continue
                else:
                    self.domains[x].remove(y)
    
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlaps = self.crossword.overlaps[x, y]
        toRemove = set()
        if overlaps:
            for val in self.domains[x]:
                if all(val[overlaps[0]] != val2[overlaps[1]] for val2 in self.domains[y]):
                    toRemove.add(val)
                    revised = True
        if toRemove:
            self.domains[x] -= toRemove
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        queue = collections.deque()
        if arcs == None:
            for a in self.domains:
                for b in self.domains:
                    if a != b:
                        queue.append((a,b))
        elif not arcs:
            return False
        else:
            for arc in arcs:
                queue.append(arc)

        while queue:
            arc = queue.popleft()
            print(arc)
            a,b = arc
            if self.revise(a,b):
                if not self.domains[a]:
                    return False
                for neighbour in self.crossword.neighbors(a) - {b}:
                    print(neighbour, '<- neighbour')
                    queue.append((neighbour, a))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if all(domain in assignment for domain in self.domains):
            return True
        return False
        
    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for val in assignment:
            if len(assignment[val]) != val.length:
                return False
            for val2 in assignment:
                if val != val2:
                    if assignment[val] == assignment[val2]:
                        return False

                    overlaps = self.crossword.overlaps[val,val2]
                    if overlaps:
                        x,y = overlaps
                        if assignment[val][x] != assignment[val2][y]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        constraints = {}
        for val in self.domains[var]:
            if val not in assignment:
                constraints[val] = 0
                neighbors = self.crossword.neighbors(var)
                for neighbor in neighbors:
                    for val2 in self.domains[neighbor]:
                        if val == val2:
                            constraints[val] += 1

        return sorted(constraints, reverse = True)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        curr_best = (math.inf,-math.inf)
        res = None

        for var in self.domains:
            if var not in assignment:
                if len(self.domains[var]) < curr_best[0]:
                    res = var
                    curr_best = (len(self.domains[var]), len(self.crossword.neighbors(var)))
                elif len(self.domains[var]) == curr_best[0]:
                    if len(self.crossword.neighbors(var)) > curr_best[1]:
                        res = var
                        curr_best = (len(self.domains[var]), len(self.crossword.neighbors(var)))
        return res

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        for val in self.domains[var]:
            temp = assignment.copy()
            temp[var] = val
            if self.consistent(assignment):
                assignment[var] = val
                res = self.backtrack(assignment)
                if res != False:
                    return assignment
                assignment[var].remove(val)
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