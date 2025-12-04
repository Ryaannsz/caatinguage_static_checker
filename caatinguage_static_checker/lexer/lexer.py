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
        # lista simples de erros léxicos (mensagens de texto)
        self.errors: list[str] = []

    # --------- utilitários básicos ---------

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

    def _add_error(self, msg: str) -> None:
        self.errors.append(f"Linha {self.line}: {msg}")

    # --------- espaços em branco e comentários ---------

    def _skip_whitespace_and_comments(self):
        while True:
            ch = self._peek()
            if ch is None:
                return

            # espaço / tabs / quebra de linha
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
                        # EOF dentro do comentário: resto do arquivo é comentário
                        self._add_error("Comentário de bloco '/*' não fechado antes do EOF.")
                        return
                    if ch2 == "*" and self._peek() == "/":
                        self._advance()  # fecha */
                        break
                continue

            # não é espaço nem comentário
            break

    # --------- token principal ---------

    def next_token(self) -> Token:
        self._skip_whitespace_and_comments()

        ch = self._peek()
        if ch is None:
            return Token(TokenType.EOF, "", self.line)

        # ---------------- Identificador ou palavra reservada ----------------
        # (case-insensitive → normaliza para lower())
        if ch.isalpha() or ch == "_":
            start_line = self.line
            lex_chars = []
            while True:
                ch = self._peek()
                if ch is None or not (ch.isalnum() or ch == "_"):
                    break
                lex_chars.append(self._advance())

            full_lex_raw = "".join(lex_chars)
            canon_lex = full_lex_raw.lower()  # normaliza em minúsculo
            truncated = canon_lex[: self.max_lexeme_len]

            if canon_lex in RESERVED_WORDS:
                return Token(RESERVED_WORDS[canon_lex], truncated, start_line)

            entry = self.symbol_table.get_or_create(canon_lex, start_line)
            return Token(TokenType.IDENT, entry.lexeme, start_line, symbol_index=entry.index)

        # ---------------- Número (inteiro / real simples) ----------------
        if ch.isdigit():
            start_line = self.line
            lex_chars = []

            # parte inteira
            while self._peek() and self._peek().isdigit():
                lex_chars.append(self._advance())

            # parte fracionária?
            if self._peek() == "." and (self._peek(1) and self._peek(1).isdigit()):
                lex_chars.append(self._advance())  # .
                while self._peek() and self._peek().isdigit():
                    lex_chars.append(self._advance())
                full_lex = "".join(lex_chars)
                truncated = full_lex[: self.max_lexeme_len]
                return Token(TokenType.REAL_CONST, truncated, start_line)

            full_lex = "".join(lex_chars)
            truncated = full_lex[: self.max_lexeme_len]
            return Token(TokenType.INT_CONST, truncated, start_line)

        # ---------------- String (aspas duplas) ----------------
        if ch == '"':
            start_line = self.line
            self._advance()  # consome a aspa de abertura
            lex_chars = []

            while True:
                ch = self._peek()
                # string não fechada (EOF ou quebra de linha)
                if ch is None or ch == "\n":
                    self._add_error("String não fechada antes de fim de linha/arquivo.")
                    full_lex = "".join(lex_chars)
                    truncated = full_lex[: self.max_lexeme_len]
                    # não consome o '\n' aqui; next_token vai tratar
                    return Token(TokenType.UNKNOWN, truncated, start_line)

                if ch == '"':
                    self._advance()  # fecha "
                    break

                lex_chars.append(self._advance())

            full_lex = "".join(lex_chars)
            truncated = full_lex[: self.max_lexeme_len]
            return Token(TokenType.STRING_CONST, truncated, start_line)

        # ---------------- Char (aspas simples) ----------------
        if ch == "'":
            start_line = self.line
            self._advance()  # consome aspa de abertura '

            ch_val = self._peek()

            # EOF, quebra de linha ou fechamento imediato → erro
            if ch_val is None or ch_val == "\n" or ch_val == "'":
                self._add_error("Constante de caractere inválida ou vazia.")
                # tenta consumir eventual fechamento
                if ch_val == "'":
                    self._advance()
                return Token(TokenType.UNKNOWN, "", start_line)

            # pega o caractere
            char_val = self._advance()

            closing = self._peek()
            if closing == "'":
                # padrão correto: 'x'
                self._advance()  # consome aspa de fechamento
                truncated = (char_val or "")[: self.max_lexeme_len]
                return Token(TokenType.CHAR_CONST, truncated, start_line)

            # mais de um caractere → erro
            extra_chars = [char_val]
            while True:
                ch2 = self._peek()
                if ch2 is None or ch2 == "\n":
                    break
                if ch2 == "'":
                    self._advance()  # consome aspa final para tentar sincronizar
                    break
                extra_chars.append(self._advance())

            self._add_error("Constante de caractere com mais de um caractere.")
            full_lex = "".join(extra_chars)
            truncated = full_lex[: self.max_lexeme_len]
            return Token(TokenType.UNKNOWN, truncated, start_line)

        # ---------------- Símbolos (dois caracteres, depois um) ----------------
        start_line = self.line
        ch = self._peek()
        two = (ch or "") + (self._peek(1) or "")

        # tenta 2 chars primeiro (ex: :=, <=, >=, ==, !=)
        if two in SYMBOLS:
            self._advance()
            self._advance()
            return Token(SYMBOLS[two], two, start_line)

        # depois 1 char (ex: +, -, *, /, %, (, ), etc.)
        if ch in SYMBOLS:
            self._advance()
            return Token(SYMBOLS[ch], ch, start_line)

        # ---------------- Desconhecido ----------------
        self._add_error(f"Símbolo desconhecido: '{ch}'.")
        self._advance()
        return Token(TokenType.UNKNOWN, ch or "", self.line)
