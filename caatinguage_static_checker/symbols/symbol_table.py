

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from config.reserved import TokenType


MAX_LINES_PER_SYMBOL = 5


@dataclass
class SymbolEntry:
    index: int
    lexeme: str
    atom_type: TokenType
    len_before_trunc: int
    len_after_trunc: int
    symbol_type: Optional[str] = None  
    lines: List[int] = field(default_factory=list)

    def add_line(self, line: int) -> None:
        if line not in self.lines and len(self.lines) < MAX_LINES_PER_SYMBOL:
            self.lines.append(line)


class SymbolTable:
    def __init__(self, max_lexeme_len: int = 35):
        self._symbols: Dict[str, SymbolEntry] = {}
        self._max_lexeme_len = max_lexeme_len
        self._next_index = 1  # começa em 1, por exemplo

    def get_or_create(self, lexeme: str, line: int) -> SymbolEntry:
        len_before = len(lexeme)
        truncated = lexeme[: self._max_lexeme_len]
        len_after = len(truncated)

        if truncated in self._symbols:
            entry = self._symbols[truncated]
            entry.add_line(line)
            return entry

        entry = SymbolEntry(
            index=self._next_index,
            lexeme=truncated,
            atom_type=TokenType.IDENT,
            len_before_trunc=len_before,
            len_after_trunc=len_after,
        )
        entry.add_line(line)
        self._symbols[truncated] = entry
        self._next_index += 1
        return entry

    def all_entries(self) -> List[SymbolEntry]:
        # retorna ordenado por index
        return sorted(self._symbols.values(), key=lambda e: e.index)
