import csv
from typing import List, Tuple, Optional
from models.ponto import Ponto


def detectar_delimitador(linha: str) -> str:
    contagens = {
        ',': linha.count(','),
        ';': linha.count(';'),
        '\t': linha.count('\t'),
    }
    return max(contagens, key=contagens.get)


def _para_float(valor: str) -> float:
    return float(valor.strip().replace(',', '.'))


def processar_csv(caminho: str) -> Tuple[List[Ponto], Optional[str]]:
    """
    Lê CSV e retorna (lista de pontos, mensagem de erro ou None).
    Formato esperado: ID, X (Este), Y (Norte), Cota, Descrição
    """
    pontos: List[Ponto] = []
    ignorados = 0

    try:
        with open(caminho, 'r', encoding='utf-8-sig') as f:
            primeira_linha = f.readline()
            delimitador = detectar_delimitador(primeira_linha)
            f.seek(0)
            reader = csv.reader(f, delimiter=delimitador)

            for i, linha in enumerate(reader):
                if i == 0:
                    continue  # cabeçalho
                if not any(c.strip() for c in linha):
                    continue  # linha vazia

                try:
                    id_ponto = linha[0].strip()
                    x = _para_float(linha[1])
                    y = _para_float(linha[2])
                    cota = _para_float(linha[3]) if len(linha) > 3 and linha[3].strip() else 0.0
                    descricao = linha[4].strip() if len(linha) > 4 else ''
                    pontos.append(Ponto(id=id_ponto, x=x, y=y, cota=cota, descricao=descricao))
                except (ValueError, IndexError):
                    ignorados += 1

    except FileNotFoundError:
        return [], f"Arquivo não encontrado: {caminho}"
    except Exception as e:
        return [], str(e)

    if not pontos:
        return [], "Nenhum ponto válido encontrado no arquivo."

    aviso = f" ({ignorados} linhas ignoradas)" if ignorados else ""
    return pontos, None if not aviso else aviso
