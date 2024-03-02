

from collections import deque
from typing import Dict


# dictionary to store tokens and lexemes
token = {'token': 'value', 'lexeme': 'lexemee'}

#  separators in RAT24S
separators: set = set(['$', '(', ')', ',', '{', '}', ';'])

# separators in RAT24S
keywords: set = set(['function', 'integer', 'bool', 'real',
                    'if', 'else', 'endif', 'return', 'scan', 'print', 'while'])

# operators in RAT24S
operators: set = set(
    ['=', '==', '!=', '>', '<', '<=', '=>', '+', '-', '*', '/', '!'])


# fsm implementation with symbol table
class FSM:
    def __init__(self, filename: str):
        # store the filename
        self.filename: str = filename
        # set of symbols our fsm can recognize
        self.symbols: set = {'whitespace', 'chr', 'int', 'dot',
                             'special', 'separator', 'operator', 'comment', 'closecomment'}
        # set of states for our fsm
        self.states: set = {'keyword', 'identifier', 'int',
                            'real', 'operator', 'valid', 'invalid', 'ignore'}
        # The fsm should always start in a valid state
        self.starting_state: str = 'valid'
        # set of acceptable states excluding 'invalid'
        self.accepting_states: set = self.states - set({'invalid'})
        # list of tokens that have been found
        self.tokens: list = []
        # symbol table for state and transitions
        self.table: dict = {x: dict() for x in self.states}
        self.create_states()
        # grab tokens from our file
        self.lexer(file_path=filename)
        # create a deque to store the tokens
        self.token_dq: deque = deque(self.tokens)
        self.tokens = []


    def create_states(self):
        #symbol table for fsm
        
        del self.table['keyword']

        # transition states for 'invalid'
        self.table['invalid']['whitespace'] = 'valid'
        self.table['invalid']['chr'] = 'invalid'
        self.table['invalid']['int'] = 'invalid'
        self.table['invalid']['dot'] = 'invalid'
        self.table['invalid']['special'] = 'invalid'
        self.table['invalid']['separator'] = 'valid'
        self.table['invalid']['operator'] = 'invalid'
        self.table['invalid']['comment'] = 'ignore'
        self.table['invalid']['closecomment'] = 'invalid'
        # transition states is 'identifier'
        self.table['identifier']['whitespace'] = 'valid'
        self.table['identifier']['chr'] = 'identifier'
        self.table['identifier']['int'] = 'identifier'
        self.table['identifier']['dot'] = 'invalid'
        self.table['identifier']['special'] = 'invalid'
        self.table['identifier']['separator'] = 'valid'
        self.table['identifier']['operator'] = 'operator'
        self.table['identifier']['comment'] = 'ignore'
        self.table['identifier']['closecomment'] = 'invalid'
        # transition states for 'int'
        self.table['int']['whitespace'] = 'valid'
        self.table['int']['chr'] = 'invalid'
        self.table['int']['int'] = 'int'
        self.table['int']['dot'] = 'real'
        self.table['int']['special'] = 'invalid'
        self.table['int']['separator'] = 'valid'
        self.table['int']['operator'] = 'operator'
        self.table['int']['comment'] = 'ignore'
        self.table['int']['closecomment'] = 'invalid'
        # transition states for  'real'
        self.table['real']['whitespace'] = 'valid'
        self.table['real']['chr'] = 'invalid'
        self.table['real']['int'] = 'real'
        self.table['real']['dot'] = 'invalid'
        self.table['real']['special'] = 'invalid'
        self.table['real']['separator'] = 'valid'
        self.table['real']['operator'] = 'operator'
        self.table['real']['comment'] = 'ignore'
        self.table['real']['closecomment'] = 'invalid'
        # transition states for 'operator'
        self.table['operator']['whitespace'] = 'ignore'
        self.table['operator']['chr'] = 'identifier'
        self.table['operator']['int'] = 'int'
        self.table['operator']['dot'] = 'invalid'
        self.table['operator']['special'] = 'invalid'
        self.table['operator']['separator'] = 'valid'
        self.table['operator']['operator'] = 'valid'
        self.table['operator']['comment'] = 'ignore'
        self.table['operator']['closecomment'] = 'invalid'
        # transition states for 'valid'
        self.table['valid']['whitespace'] = 'valid'
        self.table['valid']['chr'] = 'identifier'
        self.table['valid']['int'] = 'int'
        self.table['valid']['dot'] = 'invalid'
        self.table['valid']['special'] = 'invalid'
        self.table['valid']['separator'] = 'valid'
        
        self.table['valid']['operator'] = 'valid'
        self.table['valid']['comment'] = 'ignore'
        self.table['valid']['closecomment'] = 'invalid'
        # New states depending on if our state is 'ignore'
        # Every state besides a new comment will be ignored here, so we can do this in 1 line using dict comprehension and a ternary statement
        self.table['ignore'] = {x: 'ignore' if x !=
                                'closecomment' else 'valid' for x in self.symbols}

    def lexer(self, file_path: str):
        # open and read the file
        file_contents: str = ''
        with open(file_path, 'r') as f:
            file_contents = f.read()
        file_length = len(file_contents)

        
        #  empty set for letters
        letters = set()
        # add lowercase and uppercase letters of the alphabet to letters set
        for i in range(26):
            lower_case_letter = chr(ord('a') + i)
            upper_case_letter = lower_case_letter.upper()
            letters.update([lower_case_letter, upper_case_letter])

        #  set for whitespace characters
        whitespaces = {' ', '\n', '\t'}

        # set for numeric characters 
        nums = {str(x) for x in range(10)}

        # retrieve the symbol of the current character
        def check_symbol(ind: int) -> str:
            # checks for comment
            if file_contents[ind] == '[':
                if ind + 1 < file_length and file_contents[ind+1] == '*':
                    return 'comment'
                else:
                    return 'special'
            # checks closing comment, whitespace, chr, int, dot, separator, operator
            if file_contents[ind] == ']' and file_contents[ind-1] == '*':
                return 'closecomment'
            
            elif file_contents[ind] in whitespaces:
                return 'whitespace'
            
            elif file_contents[ind] in letters:
                return 'chr'
            
            elif file_contents[ind] in nums:
                return 'int'
            
            elif file_contents[ind] == '.':
                return 'dot'
           
            elif file_contents[ind] in separators:
                return 'separator'
            
            elif file_contents[ind] in operators:
                return 'operator'
           
            else:
                return 'special'

        #  stores current token
        curr_token = ''
        # set starting state is valid
        curr_state = self.starting_state

        for i, char in enumerate(file_contents):
            # search for current symbol
            curr_symbol = check_symbol(i)
            # If we are analyzing comments, pass until we reach end of comment
            if curr_state == 'ignore':
                if curr_symbol == 'closecomment':
                    curr_state = 'valid'
                continue
            # Add the character to our placeholder variable
            if char not in whitespaces:
                curr_token = curr_token + char
            # stash old state
            old_state = curr_state
            # change the state 
            curr_state = self.table[curr_state][curr_symbol]

            # get next symbol
            if i < file_length - 1:  
                next_symbol = check_symbol(i + 1)

            # Checks for operators that are more than 2 characters (<= or >=)
            if curr_symbol == 'operator':
                if next_symbol != 'operator' or curr_token + file_contents[i+1] not in operators:
                    if curr_token == '!': curr_state = 'invalid'
                    self.tokens.append({'token':curr_symbol,'lexeme': curr_token})
                    curr_token = ''
                    curr_state = 'valid'
                continue

            # validate token
            if (curr_state == 'valid' and curr_token != '') or (curr_state != 'valid' and (next_symbol == 'operator' or next_symbol == 'separator' or next_symbol == 'comment')):
                # initialize new state

                # checks on token
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

                self.tokens.append({'token':old_state,'lexeme': curr_token})
                curr_token = ''

        
        if curr_token != '':
            self.tokens.append({'token': curr_token, 'lexeme': curr_state})
    
    def token(self) -> Dict[str, str]:
        try:
            return self.token_dq.popleft()
        except Exception:
            raise EOFError(f"Tokens are now empty in {self.filename}")
        
"""This is for displaying output in terminal """
testcase = FSM("test3.txt")
try:
    while True:
        print(testcase.token())
except Exception as e:
    print(e)   


"""

#This is for generating output files and no display output in terminal
#test case
test = FSM("test1.txt")
with open('display1', 'w') as f:
    try:
        while True:
            print(test.token(), file=f)
    except Exception as e:
        print(e,file=f)

test1 = FSM("test2.txt")
with open('display2', 'w') as f:
    try:
        while True:
            print(test1.token(), file=f)
    except Exception as e:
        print(e,file=f)

test2 = FSM("test3.txt")
with open('display3.txt', 'w') as f:
    try:
        while True:
            print(test2.token(), file=f)
    except Exception as e:
        print(e,file=f)
 """