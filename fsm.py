
separators = {'#', '(', ')', ',', '{', '}', ';'}

keywords = {
    'function', 'integer', 'bool', 'real',
    'if', 'else', 'endif', 'ret', 'put', 'get', 'while'
}

operators = {
    '=', '==', '!=', '>', '<', '<=', '=>', '+', '-', '*', '/', '!'
}


class FSM:
    def __init__(self, filename):
        self.filename: str = filename
        
        self.symbols: set = {'whitespace', 'chr', 'int', 'dot',
                             'special', 'separator', 'operator', 'comment', 'closecomment'}
        
        self.states: set = {'keyword', 'identifier', 'int',
                            'real', 'operator', 'valid', 'invalid', 'ignore'}
        
        self.starting_state: str = 'valid'

        self.accepting_states:str = self.accepting_states - set({'invalid'})
