# parser/parser.py

from __future__ import annotations
from typing import List, Optional

from config.reserved import TokenType, Token
from lexer.lexer import Lexer
from symbols.symbol_table import SymbolTable


class Parser:
    def __init__(self, lexer: Lexer, symbol_table: SymbolTable) -> None:
        self.lexer = lexer
        self.symbol_table = symbol_table
        self.current_token: Token = self.lexer.next_token()
        self.errors: List[str] = []
        self.current_function: Optional[str] = None

    # -----------------------------------------------------
    # utilitários básicos
    # -----------------------------------------------------

    def _advance(self) -> None:
        self.current_token = self.lexer.next_token()

    def _check(self, t: TokenType) -> bool:
        return self.current_token.type == t

    def _eat(self, expected: TokenType) -> None:
        if self.current_token.type == expected:
            self._advance()
        else:
            self._error(
                f"Esperado {expected.value}, encontrado {self.current_token.type.value}",
                self.current_token.line,
            )
            self._advance()  # recuperação simples

    def _error(self, msg: str, line: int) -> None:
        self.errors.append(f"Linha {line}: {msg}")

    # -----------------------------------------------------
    # ENTRADA PRINCIPAL – FileProgram (SIMP)
    #
    # FileProgram =
    # "program" "id"
    # "declarations"
    # { "varType" "typeSpec" ( ":" | "[" "]" ":" ) "id"
    #   [ "[" "intConst" "]" ]
    #   { "," "id" [ "[" "intConst" "]" ] }
    #   { ";" "varType" "typeSpec" ( ":" | "[" "]" ":" ) "id" ... } }
    # "endDeclararions"
    # [ "functions" { func... } "endFunctions" ]
    # "endProgram" .
    # -----------------------------------------------------

    def parse(self) -> None:
        self.parse_FileProgram()
        if self.current_token.type != TokenType.EOF:
            self._error("Tokens após o fim do programa", self.current_token.line)

    def parse_FileProgram(self) -> None:
        # "program" "id"
        self._eat(TokenType.PROGRAM)

        if self.current_token.type == TokenType.IDENT:
            prog_tok = self.current_token
            entry = self.symbol_table.get_or_create(prog_tok.lexeme, prog_tok.line)
            entry.atom_type = TokenType.PROGRAMNAME  # IDN01
            entry.symbol_type = "VD"  # programa não retorna
            self._advance()
        else:
            self._error("Esperado identificador após 'program'", self.current_token.line)
            self._advance()

        # "declarations"
        self._eat(TokenType.DECLARATIONS)

        # { bloco de varType ... }
        self.parse_VarDeclSection()

        # "endDeclarations"
        self._eat(TokenType.ENDDECLARATIONS)

        # [ "functions" { func } "endFunctions" ]
        if self._check(TokenType.FUNCTIONS):
            self._eat(TokenType.FUNCTIONS)
            self.parse_FunctionSection()
            self._eat(TokenType.ENDFUNCTIONS)

        # "endProgram"
        self._eat(TokenType.ENDPROGRAM)

    # -----------------------------------------------------
    # Bloco de declarações:
    #
    # { "varType" "typeSpec" ( ":" | "[" "]" ":" ) "id"
    #   [ "[" "intConst" "]" ]
    #   { "," "id" [ "[" "intConst" "]" ] }
    #   { ";" "varType" "typeSpec" ( ":" | "[" "]" ":" ) "id" ... } }
    # -----------------------------------------------------

    def parse_VarDeclSection(self) -> None:
        # se não começar com varType, lista de declarações é vazia
        if not self._check(TokenType.VARTYPE):
            return

        # pelo menos um bloco varType
        self.parse_VarTypeBlock()

        # { ";" varTypeBlock }
        while self._check(TokenType.SEMICOLON):
            # olha se depois do ; vem um novo varType
            # se não vier, é só ponto-e-vírgula solto (erro leve) e sai
            self._eat(TokenType.SEMICOLON)
            if self._check(TokenType.VARTYPE):
                self.parse_VarTypeBlock()
            else:
                break

    def parse_VarTypeBlock(self) -> None:
        # "varType"
        self._eat(TokenType.VARTYPE)

        # "typeSpec"
        tipo_lex = self.parse_TypeSpecification()

        # ( ":" | "[" "]" ":" )
        is_array_type = False
        if self._check(TokenType.LBRACKET):
            # "[" "]" ":"
            self._eat(TokenType.LBRACKET)
            self._eat(TokenType.RBRACKET)
            self._eat(TokenType.COLON)
            is_array_type = True
        else:
            self._eat(TokenType.COLON)

        # primeiro "id" [ "[" "intConst" "]" ]
        self._parse_VarDeclIdList(tipo_lex, is_array_type)

    def _parse_VarDeclIdList(self, tipo_lex: str, is_array_type_decl: bool) -> None:
        # "id" [ "[" "intConst" "]" ]
        self._expect_and_register_decl_id(tipo_lex, is_array_type_decl)

        # { "," "id" [ "[" "intConst" "]" ] }
        while self._check(TokenType.COMMA):
            self._eat(TokenType.COMMA)
            self._expect_and_register_decl_id(tipo_lex, is_array_type_decl)

    def _expect_and_register_decl_id(self, tipo_lex: str, is_array_type_decl: bool) -> None:
        if self.current_token.type == TokenType.IDENT:
            id_tok = self.current_token
            self._advance()

            # [ "[" "intConst" "]" ]
            is_array = is_array_type_decl
            if self._check(TokenType.LBRACKET):
                is_array = True
                self._eat(TokenType.LBRACKET)
                if self.current_token.type == TokenType.INTCONST:
                    self._advance()
                else:
                    self._error("Esperado intConst no tamanho do vetor", self.current_token.line)
                    self._advance()
                self._eat(TokenType.RBRACKET)

            entry = self.symbol_table.get_or_create(id_tok.lexeme, id_tok.line)
            if entry.symbol_type is not None and entry.atom_type != TokenType.PROGRAMNAME:
                self._error(f"Identificador '{id_tok.lexeme}' redeclarado", id_tok.line)
            entry.atom_type = TokenType.VARIABLE  # IDN02
            entry.symbol_type = self._map_tipo_lexeme_to_code(tipo_lex, is_array)
        else:
            self._error("Esperado identificador de variável", self.current_token.line)
            self._advance()

    # -----------------------------------------------------
    # Section de funções (SIMP):
    #
    # "functions"
    # { "funcType" "typeSpec" ":" "id" "(" [ "?" | ParamGroups ] ")" Command "endFunction"
    #   { ";" "funcType" ... } }
    # "endFunctions"
    # -----------------------------------------------------

    def parse_FunctionSection(self) -> None:
        # se não começar com funcType, seção de funções vazia (gramática usa {}, mas vamos checar)
        if not self._check(TokenType.FUNCTYPE):
            return

        self.parse_FunctionDecl()

        while self._check(TokenType.SEMICOLON):
            self._eat(TokenType.SEMICOLON)
            if self._check(TokenType.FUNCTYPE):
                self.parse_FunctionDecl()
            else:
                break

    def parse_FunctionDecl(self) -> None:
        # "funcType" "typeSpec" ":" "id"
        self._eat(TokenType.FUNCTYPE)
        tipo_ret = self.parse_TypeSpecification()
        self._eat(TokenType.COLON)

        if self.current_token.type == TokenType.IDENT:
            fn_tok = self.current_token
            entry = self.symbol_table.get_or_create(fn_tok.lexeme, fn_tok.line)
            if entry.symbol_type is not None and entry.atom_type != TokenType.PROGRAMNAME:
                self._error(f"Função '{fn_tok.lexeme}' redeclarada", fn_tok.line)
            entry.atom_type = TokenType.FUNCTIONNAME  # IDN03
            entry.symbol_type = self._map_tipo_lexeme_to_code(tipo_ret, False)
            self.current_function = entry.lexeme
            self._advance()
        else:
            self._error("Esperado identificador de função após ':'", self.current_token.line)
            self._advance()

        # "(" [ "?" | ParamGroups ] ")"
        self._eat(TokenType.LPAREN)
        self.parse_ParamsOptional()
        self._eat(TokenType.RPAREN)

        # Command
        self.parse_Command()

        # "endFunction"
        self._eat(TokenType.ENDFUNCTION)
        self.current_function = None

    # -----------------------------------------------------
    # Parâmetros:
    #
    # [ "?" | "paramType" "typeSpec" ":" "id" { "," "id" }
    #   { ";" "paramType" "typeSpec" ":" "id" { "," "id" } } ]
    # -----------------------------------------------------

    def parse_ParamsOptional(self) -> None:
        if self._check(TokenType.QUESTIONMARK):
            self._eat(TokenType.QUESTIONMARK)
            return

        if not self._check(TokenType.PARAMTYPE):
            # sem parâmetros
            return

        # primeiro grupo paramType ...
        self.parse_ParamGroup()

        # { ";" ParamGroup }
        while self._check(TokenType.SEMICOLON):
            self._eat(TokenType.SEMICOLON)
            if self._check(TokenType.PARAMTYPE):
                self.parse_ParamGroup()
            else:
                break

    def parse_ParamGroup(self) -> None:
        # "paramType" "typeSpec" ":" "id" { "," "id" }
        self._eat(TokenType.PARAMTYPE)
        tipo_lex = self.parse_TypeSpecification()
        self._eat(TokenType.COLON)

        if self.current_token.type == TokenType.IDENT:
            self._register_param(self.current_token, tipo_lex)
            self._advance()
        else:
            self._error("Esperado identificador de parâmetro", self.current_token.line)
            self._advance()

        while self._check(TokenType.COMMA):
            self._eat(TokenType.COMMA)
            if self.current_token.type == TokenType.IDENT:
                self._register_param(self.current_token, tipo_lex)
                self._advance()
            else:
                self._error("Esperado identificador de parâmetro após ','", self.current_token.line)
                self._advance()

    def _register_param(self, tok: Token, tipo_lex: str) -> None:
        entry = self.symbol_table.get_or_create(tok.lexeme, tok.line)
        if entry.symbol_type is not None and entry.atom_type != TokenType.PROGRAMNAME:
            self._error(f"Parâmetro '{tok.lexeme}' redeclarado", tok.line)
        entry.atom_type = TokenType.VARIABLE  # IDN02
        entry.symbol_type = self._map_tipo_lexeme_to_code(tipo_lex, False)

    # -----------------------------------------------------
    # Command (SIMP):
    #
    # Command =
    # "{" Command { ";" Command } "}"
    # | "if" "(" Expression ")" Command [ "else" Command ] "endIf"
    # | "while" "(" Expression ")" Command "endWhile"
    # | "print" Expression
    # | "return" [ Expression ]
    # | "break"
    # | "id" [ "[" "intConst" "]" ] ( ":" | ":=" ) Expression .
    # -----------------------------------------------------

    def parse_Command(self) -> None:
        t = self.current_token.type

        if t == TokenType.LBRACE:
            # "{" Command { ";" Command } "}"
            self._eat(TokenType.LBRACE)
            self.parse_Command()
            while self._check(TokenType.SEMICOLON):
                self._eat(TokenType.SEMICOLON)
                self.parse_Command()
            self._eat(TokenType.RBRACE)

        elif t == TokenType.IF:
            self._eat(TokenType.IF)
            self._eat(TokenType.LPAREN)
            self.parse_Expression()
            self._eat(TokenType.RPAREN)
            self.parse_Command()
            if self._check(TokenType.ELSE):
                self._eat(TokenType.ELSE)
                self.parse_Command()
            self._eat(TokenType.ENDIF)

        elif t == TokenType.WHILE:
            self._eat(TokenType.WHILE)
            self._eat(TokenType.LPAREN)
            self.parse_Expression()
            self._eat(TokenType.RPAREN)
            self.parse_Command()
            self._eat(TokenType.ENDWHILE)

        elif t == TokenType.PRINT:
            self._eat(TokenType.PRINT)
            self.parse_Expression()

        elif t == TokenType.RETURN:
            self._eat(TokenType.RETURN)
            if self._starts_Expression():
                self.parse_Expression()

        elif t == TokenType.BREAK:
            self._eat(TokenType.BREAK)

        elif t == TokenType.IDENT:
            # "id" [ "[" "intConst" "]" ] ( ":" | ":=" ) Expression
            self.parse_AssignLike()

        else:
            self._error("Comando inválido ou inesperado", self.current_token.line)
            self._advance()

    def parse_AssignLike(self) -> None:
        # "id"
        if self.current_token.type != TokenType.IDENT:
            self._error("Esperado identificador em comando", self.current_token.line)
            self._advance()
            return

        id_tok = self.current_token
        entry = self.symbol_table.get_or_create(id_tok.lexeme, id_tok.line)
        if entry.symbol_type is None and entry.atom_type != TokenType.PROGRAMNAME:
            self._error(f"Identificador '{id_tok.lexeme}' usado antes da declaração", id_tok.line)
        self._advance()

        # [ "[" "intConst" "]" ]
        if self._check(TokenType.LBRACKET):
            self._eat(TokenType.LBRACKET)
            if self.current_token.type == TokenType.INTCONST:
                self._advance()
            else:
                self._error("Esperado intConst no índice de vetor", self.current_token.line)
                self._advance()
            self._eat(TokenType.RBRACKET)

        # ( ":" | ":=" )
        if self._check(TokenType.COLON):
            self._eat(TokenType.COLON)
        elif self._check(TokenType.ASSIGN):
            self._eat(TokenType.ASSIGN)
        else:
            self._error("Esperado ':' ou ':=' após identificador", self.current_token.line)
            self._advance()

        # Expression
        self.parse_Expression()

    # -----------------------------------------------------
    # Expression / Term / Factor (SIMP):
    #
    # Expression =
    #   ( Term { ("+" | "-") Term } )
    #   { RelOp ( Term { ("+" | "-") Term } ) } .
    #
    # Term =
    #   ( { "-" } Factor ) { ("*" | "/" | "%") ( { "-" } Factor ) } .
    #
    # Factor =
    #   "id" [ "[" "intConst" "]" ]
    # | "intConst" | "realConst" | "stringConst" | "charConst"
    # | "true" | "false"
    # | "(" Expression ")" .
    # -----------------------------------------------------

    def parse_Expression(self) -> None:
        # primeira parte: Term { (+|-) Term }
        self.parse_Additive()

        # { RelOp Additive }
        while self._is_relop(self.current_token.type):
            self._advance()
            self.parse_Additive()

    def parse_Additive(self) -> None:
        self.parse_Term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            self._advance()
            self.parse_Term()

    def parse_Term(self) -> None:
        # ( { "-" } Factor )
        while self._check(TokenType.MINUS):
            self._advance()
        self.parse_Factor()

        # { ("*" | "/" | "%") ( { "-" } Factor ) }
        while self.current_token.type in (TokenType.MULT, TokenType.DIV, TokenType.MOD):
            self._advance()
            while self._check(TokenType.MINUS):
                self._advance()
            self.parse_Factor()

    def parse_Factor(self) -> None:
        t = self.current_token.type

        if t == TokenType.IDENT:
            # "id" [ "[" "intConst" "]" ]
            id_tok = self.current_token
            entry = self.symbol_table.get_or_create(id_tok.lexeme, id_tok.line)
            if entry.symbol_type is None and entry.atom_type != TokenType.PROGRAMNAME:
                self._error(f"Identificador '{id_tok.lexeme}' usado antes da declaração", id_tok.line)
            self._advance()

            if self._check(TokenType.LBRACKET):
                self._eat(TokenType.LBRACKET)
                if self.current_token.type == TokenType.INTCONST:
                    self._advance()
                else:
                    self._error("Esperado intConst no índice de vetor", self.current_token.line)
                    self._advance()
                self._eat(TokenType.RBRACKET)

        elif t in (TokenType.INTCONST, TokenType.REALCONST,
                   TokenType.STRINGCONST, TokenType.CHARCONST,
                   TokenType.TRUE, TokenType.FALSE):
            self._advance()

        elif t == TokenType.LPAREN:
            self._eat(TokenType.LPAREN)
            self.parse_Expression()
            self._eat(TokenType.RPAREN)

        else:
            self._error("Esperado fator (id, constante ou expressão)", self.current_token.line)
            self._advance()

    # -----------------------------------------------------
    # TypeSpecification (não está na SIMP, mas vem da definição):
    # typeSpec → integer | real | string | boolean | character | void
    # -----------------------------------------------------

    def parse_TypeSpecification(self) -> str:
        tok = self.current_token
        if tok.type in (
            TokenType.INTEGER,
            TokenType.REAL,
            TokenType.STRING,
            TokenType.BOOLEAN,
            TokenType.CHARACTER,
            TokenType.VOID,
        ):
            tipo_lex = tok.lexeme
            self._advance()
            return tipo_lex
        else:
            self._error("Esperado especificação de tipo (real, integer, ...)", tok.line)
            self._advance()
            return "void"

    # -----------------------------------------------------
    # helpers de tipo / expressão / relop
    # -----------------------------------------------------

    def _map_tipo_lexeme_to_code(self, tipo_lexeme: str, is_array: bool) -> str:
        base = (tipo_lexeme or "").lower()
        if base == "real":
            return "AF" if is_array else "FP"
        if base == "integer":
            return "AI" if is_array else "IN"
        if base == "string":
            return "AS" if is_array else "ST"
        if base == "boolean":
            return "AB" if is_array else "BL"
        if base == "character":
            return "AC" if is_array else "CH"
        if base == "void":
            return "VD"
        return "VD"

    def _is_relop(self, t: TokenType) -> bool:
        return t in (
            TokenType.LESSEQ,
            TokenType.LESSTHAN,
            TokenType.GREATERTHAN,
            TokenType.GREATEREQ,
            TokenType.EQCMP,
            TokenType.NOTEQUAL,
        )

    def _starts_Expression(self) -> bool:
        return self.current_token.type in (
            TokenType.LPAREN,
            TokenType.IDENT,
            TokenType.INTCONST,
            TokenType.REALCONST,
            TokenType.STRINGCONST,
            TokenType.CHARCONST,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.MINUS,
        )
