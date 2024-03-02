import re

"""
# Define token types
TOKEN_KEYWORD = 'keyword'
TOKEN_IDENTIFIER = 'identifier'
TOKEN_INTEGER = 'integer'
TOKEN_REAL = 'real'
TOKEN_OPERATOR = 'operator'
TOKEN_SEPARATOR = 'separator'
TOKEN_COMMENT = 'comment'

# Define keywords
KEYWORDS = {'while', 'if', 'else', 'for', 'return', 'endif'}  # Add more as needed

# Define FSM transitions and states
# For simplicity, we'll use dictionaries to represent FSMs
IDENTIFIER_FSM = {'start': {'alpha': 'in_id'},
                   'in_id': {'alpha': 'in_id', 'digit': 'in_id'},
                   'end': {}}

INTEGER_FSM = {'start': {'digit': 'in_int'},
                'in_int': {'digit': 'in_int'},
                'end': {}}

REAL_FSM = {'start': {'digit': 'in_real', '.': 'in_dot'},
            'in_real': {'digit': 'in_real'},
            'in_int': {'digit': 'in_real'},  # Move to 'in_real' even after a dot
            'in_dot': {'digit': 'in_real'},
            'end': {}}

# Define operators and separators
OPERATORS = {'+', '-', '*', '/', '<', '>', '=', '<=', '>='}  # Add more as needed
SEPARATORS = {'(', ')', ';', '{', '}'}  # Add more as needed
"""

class Lexer:
    def __init__(self):
        self.tokens = []
        self.current_lexeme = ''

    def is_keyword(self, lexeme):
      keywords = ['while', 'for', 'if', 'else']
      return lexeme in keywords

    def is_separator(self, char):
        return char in [',', '(', ')', ';']

    def is_operator(self, char):
        return char in ['<', '=', '>']

    def add_token(self, token_type, lexeme):
        self.tokens.append((token_type, lexeme))
        self.current_lexeme = ''

    def tokenize(self, code):
        i = 0
        while i < len(code):
            char = code[i]

            # ignore whitespace
            if char.isspace():
                if self.current_lexeme:
                    #  determine type of lexeme
                    if self.is_keyword(self.current_lexeme):
                        self.add_token('keyword', self.current_lexeme)
                    elif self.current_lexeme.replace('.', '', 1).isdigit() and '.' in self.current_lexeme:
                        self.add_token('real', self.current_lexeme)
                    else:
                        self.add_token('identifier', self.current_lexeme)
                i += 1
                continue

            # ignore comments
            if char == '[':
                i = code.find(']', i) + 1
                if i == 0:  # No closing ']', syntax error
                    raise ValueError("Unclosed comment")
                continue

            # operators/separators
            if self.is_operator(char) or self.is_separator(char):
                if self.current_lexeme:
                    # determine type of lexeme
                    if self.is_keyword(self.current_lexeme):
                        self.add_token('keyword', self.current_lexeme)
                    elif self.current_lexeme.replace('.', '', 1).isdigit() and '.' in self.current_lexeme:
                        self.add_token('real', self.current_lexeme)
                    else:
                        self.add_token('identifier', self.current_lexeme)
                if self.is_operator(char) and code[i+1] == '=':  # For <= or >= operators
                    self.add_token('operator', char + '=')
                    i += 1
                else:
                    self.add_token('operator' if self.is_operator(char) else 'separator', char)
            else:
                self.current_lexeme += char
            i += 1

        # if there is a final lexeme
        if self.current_lexeme:
            if self.is_keyword(self.current_lexeme):
                self.add_token('keyword', self.current_lexeme)
            elif self.current_lexeme.replace('.', '', 1).isdigit() and '.' in self.current_lexeme:
                self.add_token('real', self.current_lexeme)
            else:
                self.add_token('identifier', self.current_lexeme)

        return self.tokens

# example usage:
lexer = Lexer()
source_code = """
[*
This is some sample code written in Rat23F
This will generate tokens using the code in this file
When `main` is run, the tokens will be written to 
testfile1_ratout.txt if you select this file for analysis

All comments will be ignored and not stored
*]

function factorial(number integer)
{
    if (number == 1)
    {
        ret number;
    }
    else
    {
        number = number - 1;
        ret number * factorial(number);
    }
    endif
}"""

tokens = lexer.tokenize(source_code)
for token in tokens:
    print(f"{token[0]:<10} {token[1]}")
