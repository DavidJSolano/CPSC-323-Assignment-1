import re

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

# Function to tokenize a given source code
def lexer(source_code):
    tokens = []
    current_token = ''
    fsm_state = 'start'

    # Helper function to handle FSM transitions
    def transition(current_state, char):
        nonlocal fsm_state
        if char.isalpha():
            fsm_state = IDENTIFIER_FSM[current_state].get('alpha', 'end')
        elif char.isdigit():
            fsm_state = INTEGER_FSM[current_state].get('digit', 'end')
        elif char == '.':
            fsm_state = REAL_FSM[current_state].get('.', 'end')  # Directly go to end if not a digit
        else:
            fsm_state = 'end'
        return fsm_state

    # Iterate through the source code
    for char in source_code:
        if fsm_state == 'end':
            # End current token
            if current_token:
                tokens.append((identify_token(current_token), current_token))
                current_token = char  # Start new token with the next character
            fsm_state = 'start'  # Reset state to 'start'

        # Handle comments (unchanged)
        elif char == '[':
            fsm_state = TOKEN_COMMENT
            continue
        elif char == ']':
            fsm_state = 'start'
            continue
        elif fsm_state == TOKEN_COMMENT:
            continue

        # Handle transitions
        fsm_state = transition(fsm_state, char)

        # Add char to current token (unchanged)
        if fsm_state != 'end':
            current_token += char

    # Append the last token
    if current_token:
        tokens.append((identify_token(current_token), current_token))

    return tokens

def identify_token(token):
    if token in KEYWORDS:
        return TOKEN_KEYWORD
    elif token.isdigit():
        return TOKEN_INTEGER
    elif re.match(r'\d+\.\d+', token):
        return TOKEN_REAL
    elif token in OPERATORS:
        return TOKEN_OPERATOR
    elif token in SEPARATORS:
        return TOKEN_SEPARATOR
    else:
        return TOKEN_IDENTIFIER

# Test cases
test_cases = [
    "while (fahr <= upper) a = 23.00; [* this is a sample *]",
    # Add more test cases as needed
]

# Run lexer on each test case
for idx, test_case in enumerate(test_cases, start=1):
    tokens = lexer(test_case)
    print(f"Test Case {idx}:")
    print("Token\tLexeme")
    for token, lexeme in tokens:
        print(f"{token}\t{lexeme}")
    print()
