# main.py

from pathlib import Path
from lexer.lexer import Lexer
from symbols.symbol_table import SymbolTable
from config.reserved import TokenType


def gerar_arquivo_LEX(base_name: str, tokens):
    lex_path = Path(f"{base_name}.LEX")
    with lex_path.open("w", encoding="utf-8") as f:
        # aqui você formata o cabeçalho conforme especificação do professor
        f.write(f"RELATÓRIO LÉXICO - {base_name}.252\n")
        f.write("Lexeme\tTipo\tLinha\tIndiceTS\n")
        for t in tokens:
            idx = t.symbol_index if t.symbol_index is not None else -1
            f.write(f"{t.lexeme}\t{t.type.name}\t{t.line}\t{idx}\n")


def gerar_arquivo_TAB(base_name: str, symbol_table: SymbolTable):
    tab_path = Path(f"{base_name}.TAB")
    with tab_path.open("w", encoding="utf-8") as f:
        f.write(f"TABELA DE SÍMBOLOS - {base_name}.252\n")
        f.write("Idx\tLexeme\tTipoAtom\tLenAntes\tLenDepois\tLinhas\n")
        for entry in symbol_table.all_entries():
            linhas = ",".join(str(l) for l in entry.lines)
            f.write(
                f"{entry.index}\t{entry.lexeme}\t{entry.atom_type.name}\t"
                f"{entry.len_before_trunc}\t{entry.len_after_trunc}\t{linhas}\n"
            )


def main():
    base_name = input("Digite o nome base do programa (sem .252): ").strip()
    source_path = Path(f"./examples/{base_name}.252")

    if not source_path.exists():
        print(f"Arquivo {source_path} não encontrado.")
        return

    source = source_path.read_text(encoding="utf-8")

    symbol_table = SymbolTable()
    lexer = Lexer(source, symbol_table)

    tokens = []
    while True:
        tok = lexer.next_token()
        tokens.append(tok)
        if tok.type == TokenType.EOF:
            break

    gerar_arquivo_LEX(base_name, tokens)
    gerar_arquivo_TAB(base_name, symbol_table)
    print("Arquivos .LEX e .TAB gerados com sucesso.")


if __name__ == "__main__":
    main()
