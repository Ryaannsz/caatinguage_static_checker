from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class TokenType(Enum):
    # Palavras reservadas (tipos)
    INTEGER = auto()
    REAL = auto()
    STRING = auto()
    BOOLEAN = auto()
    CHARACTER = auto()
    VOID = auto()

    TRUE = auto()
    FALSE = auto()

    # Estrutura do programa
    PROGRAM = auto()
    END_PROGRAM = auto()
    DECLARATIONS = auto()
    END_DECLARATIONS = auto()
    FUNCTIONS = auto()
    END_FUNCTIONS = auto()
    END_FUNCTION = auto()   # para fechar cada função

    # “Meta” palavras da gramática
    VARTYPE = auto()
    FUNCTYPE = auto()
    PARAMTYPE = auto()

    # Controle de fluxo
    IF = auto()
    ELSE = auto()
    END_IF = auto()
    WHILE = auto()
    END_WHILE = auto()
    RETURN = auto()
    BREAK = auto()
    PRINT = auto()

    # Identificadores / constantes
    IDENT = auto()          # programName, variable, functionName...
    INT_CONST = auto()
    REAL_CONST = auto()
    STRING_CONST = auto()
    CHAR_CONST = auto()

    # Símbolos / operadores
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()            # %

    ASSIGN = auto()         # :=
    EQ = auto()             # ==
    NEQ = auto()            # !=
    NEQ_HASH = auto()       # #  (se quiser separar)
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()

    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    LBRACE = auto()         # {
    RBRACE = auto()         # }

    SEMICOLON = auto()      # ;
    COLON = auto()          # :
    COMMA = auto()          # ,
    QUESTION = auto()       # ?

    EOF = auto()
    UNKNOWN = auto()



# mapa de palavras reservadas para TokenType
RESERVED_WORDS = {
    "program": TokenType.PROGRAM,
    "endprogram": TokenType.END_PROGRAM,
    "declarations": TokenType.DECLARATIONS,
    "enddeclarations": TokenType.END_DECLARATIONS,
    "functions": TokenType.FUNCTIONS,
    "endfunctions": TokenType.END_FUNCTIONS,
    "endfunction": TokenType.END_FUNCTION,

    "integer": TokenType.INTEGER,
    "real": TokenType.REAL,
    "string": TokenType.STRING,
    "boolean": TokenType.BOOLEAN,
    "character": TokenType.CHARACTER,
    "void": TokenType.VOID,

    "true": TokenType.TRUE,
    "false": TokenType.FALSE,

    "vartype": TokenType.VARTYPE,
    "functype": TokenType.FUNCTYPE,
    "paramtype": TokenType.PARAMTYPE,

    "if": TokenType.IF,
    "endif": TokenType.END_IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "endwhile": TokenType.END_WHILE,
    "return": TokenType.RETURN,
    "break": TokenType.BREAK,
    "print": TokenType.PRINT,
}


# mapa de símbolos simples/múltiplos chars
SYMBOLS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MUL,
    "/": TokenType.DIV,
    "%": TokenType.MOD,

    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,

    ";": TokenType.SEMICOLON,
    ":": TokenType.COLON,
    ",": TokenType.COMMA,
    "?": TokenType.QUESTION,

    ":=": TokenType.ASSIGN,
    "<=": TokenType.LE,
    "<": TokenType.LT,
    ">=": TokenType.GE,
    ">": TokenType.GT,
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
    "#": TokenType.NEQ_HASH,
}


@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    symbol_index: Optional[int] = None  # índice na tabela de símbolos (se for IDENT)