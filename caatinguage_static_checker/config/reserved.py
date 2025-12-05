# config/reserved.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional


# ============================================================
# ENUM DE TIPOS DE TOKENS
# ============================================================

class TokenType(Enum):

    # -----------------------------
    # PALAVRAS RESERVADAS
    # -----------------------------
    INTEGER = "PRS01"
    REAL = "PRS02"
    CHARACTER = "PRS03"
    STRING = "PRS04"
    BOOLEAN = "PRS05"
    VOID = "PRS06"
    TRUE = "PRS07"
    FALSE = "PRS08"
    VARTYPE = "PRS09"
    FUNCTYPE = "PRS10"
    PARAMTYPE = "PRS11"
    DECLARATIONS = "PRS12"
    ENDDECLARATIONS = "PRS13"

    PROGRAM = "PRS14"
    ENDFUNCTIONS = "PRS15"
    FUNCTIONS = "PRS16"
    RETURN = "PRS17"
    IF = "PRS18"
    ELSE = "PRS19"
    ENDIF = "PRS20"
    WHILE = "PRS21"
    ENDWHILE = "PRS22"
    BREAK = "PRS23"
    ENDPROGRAM = "PRS24"
    ENDFUNCTION = "PRS25"
    PRINT = "PRS26"
    

    # -----------------------------
    # SÍMBOLOS RESERVADOS
    # -----------------------------
    SEMICOLON = "SRS01"          # ;
    COMMA = "SRS02"              # ,
    COLON = "SRS03"              # :
    ASSIGN = "SRS04"             # =
    QUESTIONMARK = "SRS05"       # ?
    LPAREN = "SRS06"             # (
    RPAREN = "SRS07"             # )
    LBRACKET = "SRS08"           # [
    RBRACKET = "SRS09"           # ]
    LBRACE = "SRS10"             # {
    RBRACE = "SRS11"             # }

    PLUS = "SRS12"
    MINUS = "SRS13"
    MULT = "SRS14"
    DIV = "SRS15"
    MOD = "SRS16"
    EQCMP = "SRS17"              # ==
    NOTEQUAL = "SRS18"           # !=
    HASHNOT = "SRS18"            # "#" também como notEqual
    LESSTHAN = "SRS19"
    LESSEQ = "SRS20"
    GREATERTHAN = "SRS21"
    GREATEREQ = "SRS22"

    # -----------------------------
    # IDENTIFICADORES (classes)
    # -----------------------------
    PROGRAMNAME = "IDN01"
    VARIABLE = "IDN02"
    FUNCTIONNAME = "IDN03"
    INTCONST = "IDN04"
    REALCONST = "IDN05"
    STRINGCONST = "IDN06"
    CHARCONST = "IDN07"

    # -----------------------------
    # SUBMÁQUINAS
    # -----------------------------
    SUBMACHINE1 = "SUB01"
    SUBMACHINE2 = "SUB02"
    SUBMACHINE3 = "SUB03"
    SUBMACHINEN = "SUBN"

    # -----------------------------
    # ESPECIAIS
    # -----------------------------
    IDENT = "IDENT"
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"


# ============================================================
# TOKEN PADRÃO
# ============================================================

# ============================================================
# MAPA DE PALAVRAS RESERVADAS
# ============================================================

RESERVED_WORDS = {
    "integer": TokenType.INTEGER,
    "real": TokenType.REAL,
    "character": TokenType.CHARACTER,
    "string": TokenType.STRING,
    "boolean": TokenType.BOOLEAN,
    "void": TokenType.VOID,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "varType": TokenType.VARTYPE,
    "funcType": TokenType.FUNCTYPE,
    "paramType": TokenType.PARAMTYPE,
    "declarations": TokenType.DECLARATIONS,
    "endDeclarations": TokenType.ENDDECLARATIONS,

    "program": TokenType.PROGRAM,
    "functions": TokenType.FUNCTIONS,
    "endFunctions": TokenType.ENDFUNCTIONS,
    "endProgram": TokenType.ENDPROGRAM,
    "endFunction": TokenType.ENDFUNCTION,  

    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "endif": TokenType.ENDIF,
    "while": TokenType.WHILE,
    "endWhile": TokenType.ENDWHILE,
    "break": TokenType.BREAK,
    "print": TokenType.PRINT,
}


# ============================================================
# MAPA DE SÍMBOLOS RESERVADOS
# ============================================================

SYMBOLS = {
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
    ":": TokenType.COLON,
    ":=": TokenType.ASSIGN,    

    "?": TokenType.QUESTIONMARK,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,

    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MULT,
    "/": TokenType.DIV,
    "%": TokenType.MOD,

    "==": TokenType.EQCMP,
    "!=": TokenType.NOTEQUAL,
    "#": TokenType.NOTEQUAL,  

    "<": TokenType.LESSTHAN,
    "<=": TokenType.LESSEQ,
    ">": TokenType.GREATERTHAN,
    ">=": TokenType.GREATEREQ,
}



@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    symbol_index: Optional[int] = None  # índice da tabela de símbolos
