
"""
TO DO
1. Group double operators ✅
2. Separate unnecessary double operators ✅
3. Account for capital identifiers ✅
"""

"""
Written by:
Esteban Escartin
Jericho Montecillo

This file contains the code for lexical analysis of a RAT32F source file.

This file is implemented as a module file for ease of use in future project
assignments. 
"""

# This library is just to see a pretty visual of our FSM when printing, comment out if you don't have it downloaded
# The rich library can be found here: https://github.com/Textualize/rich
from rich import print
from collections import namedtuple, deque

# A set containing every separator in RAT32F
separators: set = set(['#', '(', ')', ',', '{', '}', ';'])

# A set containing every keyword in RAT32F
keywords: set = set(['function', 'integer', 'bool', 'real',
                    'if', 'else', 'endif', 'ret', 'put', 'get', 'while'])

# A set containing every operator in RAT32F
operators: set = set(
    ['=', '==', '!=', '>', '<', '<=', '=>', '+', '-', '*', '/', '!'])

# Named Tuple to store tokens
Token = namedtuple('Token', ['state', 'token'])


# Our implementation of a Finite State Machine
# This implementation includes an analysis member function to take in a file path and
# turn it into a symbol table
class FSM:
    def __init__(self, filename: str):
        # Store the filename
        self.filename: str = filename
        # A list of all the symbols our fsm may come across
        self.symbols: set = {'whitespace', 'chr', 'int', 'dot',
                             'special', 'separator', 'operator', 'comment', 'closecomment'}
        # A list of all the possible states for our fsm
        self.states: set = {'keyword', 'identifier', 'int',
                            'real', 'operator', 'valid', 'invalid', 'ignore'}
        # The fsm should always start in a valid state
        self.starting_state: str = 'valid'
        # A list of all of the acceptable states at the end of the program, Note: All states are accepted besides "invalid" which would be a lexical analysis error. We do not care about syntax, just analyzing smybols during this phase
        self.accepting_states: set = self.states - set({'invalid'})
        # A list to store all the tokens we have analyzed
        self.tokens: list = []
        # Initialize the table of states and transitions
        self.table: dict = {x: dict() for x in self.states}
        self.create_states()
        # Finally, grab the tokens from our target file
        self.analyze(file_path=filename)
        # Push into a dq and clear our temp token list
        self.token_dq: deque = deque(self.tokens)
        self.tokens = []


    def create_states(self):
        # Note: This table does NOT include keyword states. A keyword will be identified mid syntax analysis. This will be done by
        # checking if an accepted identifier is in the keyword list
        # Note: We also do NOT include states for 'invalid'. If we recieve an invalid state during lexical analysis, the
        # compiler should terminate
        del self.table['keyword']

        # Include transitions from invalid to some valid state
        self.table['invalid']['whitespace'] = 'valid'
        self.table['invalid']['chr'] = 'invalid'
        self.table['invalid']['int'] = 'invalid'
        self.table['invalid']['dot'] = 'invalid'
        self.table['invalid']['special'] = 'invalid'
        self.table['invalid']['separator'] = 'valid'
        self.table['invalid']['operator'] = 'invalid'
        self.table['invalid']['comment'] = 'ignore'
        self.table['invalid']['closecomment'] = 'invalid'
        # New states depending on if our state is 'identifier'
        self.table['identifier']['whitespace'] = 'valid'
        self.table['identifier']['chr'] = 'identifier'
        self.table['identifier']['int'] = 'identifier'
        self.table['identifier']['dot'] = 'invalid'
        self.table['identifier']['special'] = 'invalid'
        self.table['identifier']['separator'] = 'valid'
        self.table['identifier']['operator'] = 'operator'
        self.table['identifier']['comment'] = 'ignore'
        self.table['identifier']['closecomment'] = 'invalid'
        # New states depending on if our state is 'int'
        self.table['int']['whitespace'] = 'valid'
        self.table['int']['chr'] = 'invalid'
        self.table['int']['int'] = 'int'
        self.table['int']['dot'] = 'real'
        self.table['int']['special'] = 'invalid'
        self.table['int']['separator'] = 'valid'
        self.table['int']['operator'] = 'operator'
        self.table['int']['comment'] = 'ignore'
        self.table['int']['closecomment'] = 'invalid'
        # New states depending on if our state is 'real'
        self.table['real']['whitespace'] = 'valid'
        self.table['real']['chr'] = 'invalid'
        self.table['real']['int'] = 'real'
        self.table['real']['dot'] = 'invalid'
        self.table['real']['special'] = 'invalid'
        self.table['real']['separator'] = 'valid'
        self.table['real']['operator'] = 'operator'
        self.table['real']['comment'] = 'ignore'
        self.table['real']['closecomment'] = 'invalid'
        # New states depending on if our state is 'operator'
        self.table['operator']['whitespace'] = 'ignore'
        self.table['operator']['chr'] = 'identifier'
        self.table['operator']['int'] = 'int'
        self.table['operator']['dot'] = 'invalid'
        self.table['operator']['special'] = 'invalid'
        self.table['operator']['separator'] = 'valid'
        self.table['operator']['operator'] = 'valid'
        self.table['operator']['comment'] = 'ignore'
        self.table['operator']['closecomment'] = 'invalid'
        # New states depending on if our state is 'valid'
        self.table['valid']['whitespace'] = 'valid'
        self.table['valid']['chr'] = 'identifier'
        self.table['valid']['int'] = 'int'
        self.table['valid']['dot'] = 'invalid'
        self.table['valid']['special'] = 'invalid'
        # Note: we don't care if we are given a closed seperated before an opening one. That will be handled in syntax analysis
        self.table['valid']['separator'] = 'valid'
        # CHANGED THIS FROM OPERATOR TO VALID
        self.table['valid']['operator'] = 'valid'
        self.table['valid']['comment'] = 'ignore'
        self.table['valid']['closecomment'] = 'invalid'
        # New states depending on if our state is 'ignore'
        # Every state besides a new comment will be ignored here, so we can do this in 1 line using dict comprehension and a ternary statement
        self.table['ignore'] = {x: 'ignore' if x !=
                                'closecomment' else 'valid' for x in self.symbols}

    def analyze(self, file_path: str):
        # Open the file and read/store its contents
        file_contents: str = ''
        with open(file_path, 'r') as f:
            file_contents = f.read()
        n = len(file_contents)

        # Variables to be used throughout the analysis
        letters: set = set()
        for i in range(26):
            tmp = chr(ord('a') + i)
            letters.add(tmp)
            letters.add(tmp.upper())
        whitespaces: set = {' ', '\n', '\t'}
        nums: set = set(x for x in '0123456789')

        # Define a function to get what the current symbol is
        # Note: This should stay a nested function. While this is less efficient when initializing
        # a lexical analysis process, it is faster than passing a string representing the entirety
        # of a file into a member function whenever we want to check a symbol. 
        def check_symbol(ind: int) -> str:
            # Check for a comment
            if file_contents[ind] == '[':
                if ind + 1 < n and file_contents[ind+1] == '*':
                    return 'comment'
                else:
                    return 'special'
            # Check for closing comment
            if file_contents[ind] == ']' and file_contents[ind-1] == '*':
                return 'closecomment'
            # Check for whitespace
            elif file_contents[ind] in whitespaces:
                return 'whitespace'
            # Check for chr
            elif file_contents[ind] in letters:
                return 'chr'
            # Check for int
            elif file_contents[ind] in nums:
                return 'int'
            # Check for dot
            elif file_contents[ind] == '.':
                return 'dot'
            # Check for seperator
            elif file_contents[ind] in separators:
                return 'separator'
            # Check for operator
            elif file_contents[ind] in operators:
                return 'operator'
            # If none are applicable, this is a special character
            else:
                return 'special'

        # Initialize temp variable to store current token
        curr_token = ''
        # Before iterating, starting state is valid
        curr_state = self.starting_state

        for ind, char in enumerate(file_contents):
            # Find the symbol of the current character
            curr_symbol = check_symbol(ind)
            # If we are analyzing comments, pass until we reach end of comment
            if curr_state == 'ignore':
                if curr_symbol == 'closecomment':
                    curr_state = 'valid'
                continue
            # Add the character to our placeholder variable
            if char not in whitespaces:
                curr_token = curr_token + char
            # Store the old state in case token is finished
            old_state = curr_state
            # Change the state to match current state and symbol
            curr_state = self.table[curr_state][curr_symbol]

            # Get next symbol
            if ind < n - 1:  # Temp Fix
                next_symbol = check_symbol(ind + 1)

            # Checks for operators that are more than 2 characters (<= or >=)
            if curr_symbol == 'operator':
                if next_symbol != 'operator' or curr_token + file_contents[ind+1] not in operators:
                    if curr_token == '!': curr_state = 'invalid'
                    self.tokens.append(Token(curr_symbol, curr_token))
                    curr_token = ''
                    curr_state = 'valid'
                continue

            # Checks to see if token is valid
            if (curr_state == 'valid' and curr_token != '') or (curr_state != 'valid' and (next_symbol == 'operator' or next_symbol == 'separator' or next_symbol == 'comment')):
                # If valid token, initializes a new token and clears placeholder

                # Checks on the token
                if curr_symbol == 'comment':
                    curr_token = ''
                    curr_state = 'ignore'
                    continue
                elif curr_token in operators:
                    old_state = 'operator'
                elif curr_token in separators:
                    old_state = 'separator'
                elif curr_token in keywords:
                    old_state = 'keyword'

                self.tokens.append(Token(old_state, curr_token))
                curr_token = ''

        # Handle unanalyzed text
        if curr_token != '':
            self.tokens.append(Token(curr_state, curr_token))
    
    def token(self) -> Token:
        try:
            return self.token_dq.popleft()
        except Exception:
            raise EOFError(f"There are no more tokens in {self.filename}")

a = FSM("test3.txt")
try:
    while True:
        print(a.token())
except Exception as e:
    print(e)