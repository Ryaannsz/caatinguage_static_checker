import sys
from pathlib import Path
from lexer.lexer import Lexer
from symbols.symbol_table import SymbolTable
from config.reserved import TokenType
from parser.parser import Parser


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        return Path(__file__).resolve().parent


def get_results_dir() -> Path:
    if getattr(sys, "frozen", False):
        # Diretório onde o executável está
        base_output = Path(sys.executable).resolve().parent
    else:
        # Diretório onde está o main.py
        base_output = Path(__file__).resolve().parent

    results_dir = base_output / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


def gerar_arquivo_LEX(base_name: str, tokens):
    results_dir = get_results_dir()
    lex_path = results_dir / f"{base_name}.LEX"

    rows = []
    for t in tokens:
        if t.type == TokenType.EOF:
            continue
        linha = str(t.line)
        cod_atomo = t.type.value
        lexeme = t.lexeme
        idx = str(t.symbol_index if t.symbol_index is not None else 0)
        rows.append((linha, cod_atomo, lexeme, idx))

    headers = ("Linha", "CodAtomo", "Lexeme", "IdxTS")

    col_widths = []
    for i in range(len(headers)):
        max_data = max((len(row[i]) for row in rows), default=0)
        col_widths.append(max(len(headers[i]), max_data))

    with lex_path.open("w", encoding="utf-8") as f:
        f.write(f"RELATÓRIO LÉXICO - {base_name}.252\n")

        header_line = (
            f"{headers[0]:<{col_widths[0]}}  "
            f"{headers[1]:<{col_widths[1]}}  "
            f"{headers[2]:<{col_widths[2]}}  "
            f"{headers[3]:<{col_widths[3]}}\n"
        )
        f.write(header_line)

        sep_line = (
            f"{'-' * col_widths[0]}  "
            f"{'-' * col_widths[1]}  "
            f"{'-' * col_widths[2]}  "
            f"{'-' * col_widths[3]}\n"
        )
        f.write(sep_line)

        for linha, cod_atomo, lexeme, idx in rows:
            f.write(
                f"{linha:<{col_widths[0]}}  "
                f"{cod_atomo:<{col_widths[1]}}  "
                f"{lexeme:<{col_widths[2]}}  "
                f"{idx:<{col_widths[3]}}\n"
            )


def gerar_arquivo_TAB(base_name: str, symbol_table: SymbolTable):
    results_dir = get_results_dir()
    tab_path = results_dir / f"{base_name}.TAB"

    rows = []
    for entry in symbol_table.all_entries():
        idx = str(entry.index)
        lexeme = entry.lexeme
        cod_atomo = entry.atom_type.value
        len_antes = str(entry.len_before_trunc)
        len_depois = str(entry.len_after_trunc)
        tipo_simbolo = entry.symbol_type or ""
        linhas = ", ".join(str(l) for l in entry.lines)
        rows.append((idx, lexeme, cod_atomo, len_antes, len_depois, tipo_simbolo, linhas))

    headers = ("Idx", "Lexeme", "CodAtomo", "LenAntes", "LenDepois", "TipoSimbolo", "Linhas")

    col_widths = []
    for i in range(len(headers)):
        max_data = max((len(row[i]) for row in rows), default=0)
        col_widths.append(max(len(headers[i]), max_data))

    with tab_path.open("w", encoding="utf-8") as f:
        f.write(f"TABELA DE SÍMBOLOS - {base_name}.252\n")

        header_line = (
            f"{headers[0]:<{col_widths[0]}}  "
            f"{headers[1]:<{col_widths[1]}}  "
            f"{headers[2]:<{col_widths[2]}}  "
            f"{headers[3]:<{col_widths[3]}}  "
            f"{headers[4]:<{col_widths[4]}}  "
            f"{headers[5]:<{col_widths[5]}}  "
            f"{headers[6]:<{col_widths[6]}}\n"
        )
        f.write(header_line)

        sep_line = (
            f"{'-' * col_widths[0]}  "
            f"{'-' * col_widths[1]}  "
            f"{'-' * col_widths[2]}  "
            f"{'-' * col_widths[3]}  "
            f"{'-' * col_widths[4]}  "
            f"{'-' * col_widths[5]}  "
            f"{'-' * col_widths[6]}\n"
        )
        f.write(sep_line)

        for row in rows:
            f.write(
                f"{row[0]:<{col_widths[0]}}  "
                f"{row[1]:<{col_widths[1]}}  "
                f"{row[2]:<{col_widths[2]}}  "
                f"{row[3]:<{col_widths[3]}}  "
                f"{row[4]:<{col_widths[4]}}  "
                f"{row[5]:<{col_widths[5]}}  "
                f"{row[6]:<{col_widths[6]}}\n"
            )


def gerar_arquivo_ERR(base_name: str, errors: list[str]):
    results_dir = get_results_dir()
    err_path = results_dir / f"{base_name}.ERR"
    print("PATHHHHH")
    print(err_path)
    with err_path.open("w", encoding="utf-8") as f:
        if not errors:
            f.write("Nenhum erro encontrado.\n")
        else:
            for e in errors:
                f.write(e + "\n")


def processar_arquivo(source_path: Path):
    base_name = source_path.stem
    print(f"\nProcessando arquivo: {source_path.name}...")

    source = source_path.read_text(encoding="utf-8")

    symbol_table = SymbolTable()
    lexer_for_parser = Lexer(source, symbol_table)
    parser = Parser(lexer_for_parser, symbol_table)

    parser.parse()

    lexer_for_lex = Lexer(source, symbol_table)
    tokens = []
    while True:
        tok = lexer_for_lex.next_token()
        tokens.append(tok)
        if tok.type == TokenType.EOF:
            break

    gerar_arquivo_LEX(base_name, tokens)
    gerar_arquivo_TAB(base_name, symbol_table)
    gerar_arquivo_ERR(base_name, parser.errors)

    print(f"Arquivos {base_name}.LEX, {base_name}.TAB e {base_name}.ERR gerados.")


def main():
    base_dir = get_base_dir()
    examples_dir = base_dir / "examples"

    print("Selecione o modo de execução:")
    print("1 - Testar arquivo único")
    print("2 - Testar todos os arquivos .252 da pasta 'examples'")
    choice = input("Opção (1/2): ").strip()

    if choice == "2":
        if not examples_dir.exists():
            print("Pasta 'examples' não encontrada.")
            return

        files = sorted(examples_dir.glob("*.252"))
        if not files:
            print("Nenhum arquivo .252 encontrado na pasta 'examples'.")
            return

        print(f"Encontrados {len(files)} arquivo(s) .252 em 'examples'.")
        for source_path in files:
            processar_arquivo(source_path)

        print("\nProcessamento de todos os testes concluído.")
        return

    base_name = input("Digite o nome base do programa (sem .252): ").strip()
    source_path = examples_dir / f"{base_name}.252"

    if not source_path.exists():
        print(f"Arquivo {source_path} não encontrado.")
        return

    processar_arquivo(source_path)
    print("\nProcessamento concluído com sucesso.")


if __name__ == "__main__":
    main()
