# lexer/lexer.py

from typing import Optional
from config.reserved import Token, TokenType, RESERVED_WORDS, SYMBOLS
from symbols.symbol_table import SymbolTable


class Lexer:
    def __init__(self, source: str, symbol_table: SymbolTable, max_lexeme_len: int = 35):
        self.source = source
        self.symbol_table = symbol_table
        self.pos = 0
        self.line = 1
        self.max_lexeme_len = max_lexeme_len

    # utilidades básicas ----------------------------------

    def _peek(self, offset: int = 0) -> Optional[str]:
        idx = self.pos + offset
        if idx >= len(self.source):
            return None
        return self.source[idx]

    def _advance(self) -> Optional[str]:
        ch = self._peek()
        if ch is None:
            return None
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    # espaços e comentários -------------------------------

    def _skip_whitespace_and_comments(self):
        while True:
            ch = self._peek()
            if ch is None:
                return

            # espaços/brancos
            if ch.isspace():
                self._advance()
                continue

            # // comentário de linha
            if ch == "/" and self._peek(1) == "/":
                self._advance()  # /
                self._advance()  # /
                while self._peek() not in (None, "\n"):
                    self._advance()
                continue

            # /* comentário de bloco */
            if ch == "/" and self._peek(1) == "*":
                self._advance()  # /
                self._advance()  # *
                while True:
                    ch2 = self._advance()
                    if ch2 is None:
                        # EOF sem fechar comentário
                        return
                    if ch2 == "*" and self._peek() == "/":
                        self._advance()  # fecha */
                        break
                continue

            break  # não é espaço/comentário

    # token principal -------------------------------------

    def next_token(self) -> Token:
        self._skip_whitespace_and_comments()

        ch = self._peek()
        if ch is None:
            return Token(TokenType.EOF, "", self.line)

        # IDENT ou PALAVRA RESERVADA ----------------------
        if ch.isalpha() or ch == "_":
            start_line = self.line
            lex = []
            while True:
                ch2 = self._peek()
                if ch2 is None or not (ch2.isalnum() or ch2 == "_"):
                    break
                lex.append(self._advance())
            full_lex = "".join(lex)
            truncated = full_lex[: self.max_lexeme_len]

            # palavra reservada?
            if full_lex in RESERVED_WORDS:
                return Token(RESERVED_WORDS[full_lex], truncated, start_line)

            # identificador de usuário -> tabela de símbolos
            entry = self.symbol_table.get_or_create(full_lex, start_line)
            # lexeme exibido = o truncado salvo
            return Token(TokenType.IDENT, entry.lexeme, start_line, symbol_index=entry.index)

        # NÚMEROS -----------------------------------------
        if ch.isdigit():
            start_line = self.line
            lex = []

            # parte inteira
            while self._peek() and self._peek().isdigit():
                lex.append(self._advance())

            # parte fracionária opcional
            is_real = False
            if self._peek() == "." and (self._peek(1) and self._peek(1).isdigit()):
                is_real = True
                lex.append(self._advance())  # .
                while self._peek() and self._peek().isdigit():
                    lex.append(self._advance())

            # (se quiser, depois adiciona parte exponencial aqui)

            full_lex = "".join(lex)
            truncated = full_lex[: self.max_lexeme_len]
            if is_real:
                return Token(TokenType.REALCONST, truncated, start_line)
            else:
                return Token(TokenType.INTCONST, truncated, start_line)

        # STRING ------------------------------------------
        if ch == '"':
            start_line = self.line
            self._advance()  # abre "
            lex = []
            while True:
                ch2 = self._peek()
                if ch2 is None or ch2 == "\n":
                    # string não fechada; você pode tratar como erro
                    break
                if ch2 == '"':
                    self._advance()
                    break
                lex.append(self._advance())
            full_lex = "".join(lex)
            truncated = full_lex[: self.max_lexeme_len]
            return Token(TokenType.STRINGCONST, truncated, start_line)

        # CHAR (simplificado) -----------------------------
        if ch == "'":
            start_line = self.line
            self._advance()  # '
            ch_val = self._advance()
            self._advance()  # fecha '
            lex = ch_val or ""
            truncated = lex[: self.max_lexeme_len]
            return Token(TokenType.CHARCONST, truncated, start_line)

        # SÍMBOLOS (tenta 2 chars primeiro) ---------------
        start_line = self.line
        two = (ch or "") + (self._peek(1) or "")
        if two in SYMBOLS:
            self._advance()
            self._advance()
            return Token(SYMBOLS[two], two, start_line)

        if ch in SYMBOLS:
            self._advance()
            return Token(SYMBOLS[ch], ch, start_line)

        # DESCONHECIDO ------------------------------------
        self._advance()
        return Token(TokenType.UNKNOWN, ch, self.line)
