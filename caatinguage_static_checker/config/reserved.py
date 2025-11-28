from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class TokenType(Enum):

    PROGRAM = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    RETURN = auto()
    # adicionar as faltantes ainda q tá lá no brut
    #..
    #..
    #..

    
    IDENT = auto()
    INT_CONST = auto()
    REAL_CONST = auto()
    STRING_CONST = auto()
    CHAR_CONST = auto()

    # Símbolos
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    ASSIGN = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    COMMA = auto()


    EOF = auto()
    UNKNOWN = auto()


# mapa de palavras reservadas para TokenType
RESERVED_WORDS = {
    "program": TokenType.PROGRAM,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "return": TokenType.RETURN,
    # ... completar
}

# mapa de símbolos simples/múltiplos chars
SYMBOLS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MUL,
    "/": TokenType.DIV,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
    "=": TokenType.ASSIGN,
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
    "<": TokenType.LT,
    "<=": TokenType.LE,
    ">": TokenType.GT,
    ">=": TokenType.GE,
    # ...
}


@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    symbol_index: Optional[int] = None  # índice na tabela de símbolos (se for IDENT)