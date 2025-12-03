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

    def _skip_whitespace_and_comments(self):
        while True:
            ch = self._peek()
            if ch is None:
                return
            # espaço / tabs / quebra
            if ch.isspace():
                self._advance()
                continue

            # comentário de linha: //
            if ch == "/" and self._peek(1) == "/":
                self._advance()  # /
                self._advance()  # /
                while self._peek() not in (None, "\n"):
                    self._advance()
                continue

            # comentário de bloco: /* ... */
            if ch == "/" and self._peek(1) == "*":
                self._advance()  # /
                self._advance()  # *
                while True:
                    ch2 = self._advance()
                    if ch2 is None:
                        # chegou EOF sem fechar comentário; decide o que fazer
                        return
                    if ch2 == "*" and self._peek() == "/":
                        self._advance()  # fecha */
                        break
                continue

            break  # não é espaço/comentário

    def next_token(self) -> Token:
        self._skip_whitespace_and_comments()

        ch = self._peek()
        if ch is None:
            return Token(TokenType.EOF, "", self.line)

        # Identificador ou palavra reservada: começa por letra ou _
        if ch.isalpha() or ch == "_":
            start_line = self.line
            lex = []
            while True:
                ch = self._peek()
                if ch is None or not (ch.isalnum() or ch == "_"):
                    break
                lex.append(self._advance())
            full_lex = "".join(lex)
            # truncagem
            truncated = full_lex[: self.max_lexeme_len]

            # palavra reservada?
            if full_lex in RESERVED_WORDS:
                return Token(RESERVED_WORDS[full_lex], truncated, start_line)

            # identificador → tabela de símbolos
            entry = self.symbol_table.get_or_create(full_lex, start_line)
            return Token(TokenType.IDENT, entry.lexeme, start_line, symbol_index=entry.index)

        # Número (inteiro/real simplificado)
        if ch.isdigit():
            start_line = self.line
            lex = []

            # parte inteira
            while self._peek() and self._peek().isdigit():
                lex.append(self._advance())

            # parte fracionária?
            if self._peek() == "." and (self._peek(1) and self._peek(1).isdigit()):
                lex.append(self._advance())  # .
                while self._peek() and self._peek().isdigit():
                    lex.append(self._advance())
                # ignorando por enquanto parte exponencial; você completa depois
                full_lex = "".join(lex)
                truncated = full_lex[: self.max_lexeme_len]
                return Token(TokenType.REAL_CONST, truncated, start_line)

            full_lex = "".join(lex)
            truncated = full_lex[: self.max_lexeme_len]
            return Token(TokenType.INT_CONST, truncated, start_line)

        # String (aspas duplas)
        if ch == '"':
            start_line = self.line
            self._advance()  # abre "
            lex = []
            while True:
                ch = self._peek()
                if ch is None or ch == "\n":
                    # erro de string não fechada, trate como quiser
                    break
                if ch == '"':
                    self._advance()
                    break
                lex.append(self._advance())
            full_lex = "".join(lex)
            truncated = full_lex[: self.max_lexeme_len]
            return Token(TokenType.STRING_CONST, truncated, start_line)

        # Char (aspas simples) – bem simplificado
        if ch == "'":
            start_line = self.line
            self._advance()  # '
            ch_val = self._advance()
            self._advance()  # fecha '
            lex = ch_val or ""
            truncated = lex[: self.max_lexeme_len]
            return Token(TokenType.CHAR_CONST, truncated, start_line)

        # Símbolos (tenta 2 chars primeiro)
        start_line = self.line
        two = (ch or "") + (self._peek(1) or "")
        if two in SYMBOLS:
            self._advance()
            self._advance()
            return Token(SYMBOLS[two], two, start_line)

        if ch in SYMBOLS:
            self._advance()
            return Token(SYMBOLS[ch], ch, start_line)

        # Desconhecido
        self._advance()
        return Token(TokenType.UNKNOWN, ch, self.line)
