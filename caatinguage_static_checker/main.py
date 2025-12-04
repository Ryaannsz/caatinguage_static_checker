

from pathlib import Path
from lexer.lexer import Lexer
from symbols.symbol_table import SymbolTable
from config.reserved import TokenType


def gerar_arquivo_LEX(base_name: str, tokens):
    lex_path = Path(f"{base_name}.LEX")

    # monta linhas (ignorando EOF se você quiser)
    rows = []
    for t in tokens:
        if t.type == TokenType.EOF:
            continue
        linha = str(t.line)
        cod_atomo = t.type.name  # se depois quiser, troca por tabela de códigos
        lexeme = t.lexeme
        idx = str(t.symbol_index if t.symbol_index is not None else 0)
        rows.append((linha, cod_atomo, lexeme, idx))

    # cabeçalhos
    headers = ("Linha", "CodAtomo", "Lexeme", "IdxTS")

    # calcula larguras das colunas
    col_widths = []
    for i in range(len(headers)):
        max_data = max((len(row[i]) for row in rows), default=0)
        col_widths.append(max(len(headers[i]), max_data))

    with lex_path.open("w", encoding="utf-8") as f:
        f.write(f"RELATÓRIO LÉXICO - {base_name}.252\n")

        # escreve cabeçalho alinhado
        header_line = (
            f"{headers[0]:<{col_widths[0]}}  "
            f"{headers[1]:<{col_widths[1]}}  "
            f"{headers[2]:<{col_widths[2]}}  "
            f"{headers[3]:<{col_widths[3]}}\n"
        )
        f.write(header_line)

        # linha separadora
        sep_line = (
            f"{'-' * col_widths[0]}  "
            f"{'-' * col_widths[1]}  "
            f"{'-' * col_widths[2]}  "
            f"{'-' * col_widths[3]}\n"
        )
        f.write(sep_line)

        # linhas de dados
        for linha, cod_atomo, lexeme, idx in rows:
            f.write(
                f"{linha:<{col_widths[0]}}  "
                f"{cod_atomo:<{col_widths[1]}}  "
                f"{lexeme:<{col_widths[2]}}  "
                f"{idx:<{col_widths[3]}}\n"
            )

def gerar_arquivo_TAB(base_name: str, symbol_table: SymbolTable):
    tab_path = Path(f"{base_name}.TAB")

    rows = []
    for entry in symbol_table.all_entries():
        idx = str(entry.index)
        lexeme = entry.lexeme
        cod_atomo = entry.atom_type.name  # ou map pra código curto
        len_antes = str(entry.len_before_trunc)
        len_depois = str(entry.len_after_trunc)
        tipo_simbolo = entry.symbol_type or ""  # IN, RE, ST, etc, quando tiver
        linhas = ", ".join(str(l) for l in entry.lines)

        rows.append((idx, lexeme, cod_atomo, len_antes, len_depois, tipo_simbolo, linhas))

    headers = ("Idx", "Lexeme", "CodAtomo", "LenAntes", "LenDepois", "TipoSimbolo", "Linhas")

    # calcula larguras
    col_widths = []
    for i in range(len(headers)):
        max_data = max((len(row[i]) for row in rows), default=0)
        col_widths.append(max(len(headers[i]), max_data))

    with tab_path.open("w", encoding="utf-8") as f:
        f.write(f"TABELA DE SÍMBOLOS - {base_name}.252\n")

        # cabeçalho
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

        # separador
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

        # dados
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


def main():
    examples_dir = Path("./examples")

    print("Selecione o modo de execução:")
    print("1 - Testar arquivo único")
    print("2 - Testar todos os arquivos .252 da pasta 'examples'")
    choice = input("Opção (1/2): ").strip()

    # ---------------- MODO 2: todos os arquivos ----------------
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
            base_name = source_path.stem
            print(f"\nProcessando arquivo: {source_path.name}...")

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
            print(f"Arquivos {base_name}.LEX e {base_name}.TAB gerados.")

        print("\nProcessamento de todos os testes concluído.")
        return

    # ---------------- MODO 1: arquivo único (fluxo antigo) ----------------
    base_name = input("Digite o nome base do programa (sem .252): ").strip()
    source_path = examples_dir / f"{base_name}.252"

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
