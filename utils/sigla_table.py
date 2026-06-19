# Tabela de siglas portada do app Android (SiglaTable.kt)
# Espaços substituídos por underscore (AutoCAD: espaço = Enter)

SIGLAS: dict[str, str] = {
    "ARV": "Árvore",
    "VE":  "Vétice_de_Edificação",
    "RP":  "Rampa",
    "DG":  "Degrau",
    "PT":  "Porta_Portão",
    "VMI": "Vétice_Muro_Interno",
    "VME": "Vétice_Muro_Externo",
    "CAP": "Captação_Águas_Pluviais",
    "N":   "Nível",
    "NT":  "Nível_do_Terreno",
    "SJ":  "Sarjeta",
    "VC":  "Vétice_Calçada",
    "OR":  "Orelhão",
    "CA":  "Caixa_de_Água",
    "CB":  "Cobertura",
    "BL":  "Boca_de_Lobo",
    "FBL": "Fundo_Boca_de_Lobo",
    "BMI": "Base_Muro_Interno",
    "BME": "Base_Muro_Externo",
    "PD":  "Padrão",
    "PST": "Poste",
    "AM":  "Altura_do_Muro",
    "MT":  "Mureta",
    "HD":  "Hidrômetro",
    "GRD": "Grade",
    "CP":  "Caixa_de_Passagem",
    "ALG": "Algibe",
}


def resolver(sigla: str) -> str:
    """Retorna o nome do layer para a sigla, ou a própria sigla se não mapeada."""
    return SIGLAS.get(sigla.upper(), sigla.upper())
