

from pathlib import Path
from lexer.lexer import Lexer
from symbols.symbol_table import SymbolTable
from config.reserved import TokenType


def gerar_arquivo_LEX(base_name: str, tokens):
    lex_path = Path(f"{base_name}.LEX")
    with lex_path.open("w", encoding="utf-8") as f:
        f.write(f"RELATÓRIO LÉXICO - {base_name}.252\n")
        f.write("Linha\tCodAtomo\tLexeme\tIdxTS\n")

        for t in tokens:
            # se não quiser listar EOF, pule
            if t.type == TokenType.EOF:
                continue

            idx = t.symbol_index if t.symbol_index is not None else 0

            # TODO: se o professor deu tabela de códigos, usar essa tabela aqui
            cod_atomo = t.type.name  # placeholder; depois troca por ATOM_CODES[t.type]

            f.write(f"{t.line}\t{cod_atomo}\t{t.lexeme}\t{idx}\n")

def gerar_arquivo_TAB(base_name: str, symbol_table: SymbolTable):
    tab_path = Path(f"{base_name}.TAB")
    with tab_path.open("w", encoding="utf-8") as f:
        f.write(f"TABELA DE SÍMBOLOS - {base_name}.252\n")
        f.write("Idx\tLexeme\tCodAtomo\tLenAntes\tLenDepois\tTipoSimbolo\tLinhas\n")

        for entry in symbol_table.all_entries():
            linhas = ",".join(str(l) for l in entry.lines)

            cod_atomo = entry.atom_type.name  # ou usar um map, tipo ATOM_CODES[entry.atom_type]
            tipo_simbolo = entry.symbol_type or ""  # IN, RE, ST, CH, BL, VD...

            f.write(
                f"{entry.index}\t{entry.lexeme}\t{cod_atomo}\t"
                f"{entry.len_before_trunc}\t{entry.len_after_trunc}\t"
                f"{tipo_simbolo}\t{linhas}\n"
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
