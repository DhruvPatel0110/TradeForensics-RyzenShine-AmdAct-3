import re
from typing import Dict, List, Tuple, Optional

# Curated Portuguese stopwords, intentionally EXCLUDING negations (nao, nunca, nem, sem)
# because negations are critical signals in complaint diagnostics.
PORTUGUESE_STOPWORDS = {
    "de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "com",
    "uma", "os", "no", "se", "na", "por", "mais", "as", "dos", "como",
    "mas", "ao", "ele", "das", "seu", "sua", "ou", "quando", "muito",
    "nos", "ja", "eu", "tambem", "so", "pelo", "pela", "ate", "isso",
    "ela", "entre", "depois", "meu", "minha", "tem", "me", "mesmo",
    "esse", "eles", "voce", "essa", "num", "pra", "suas", "meus",
    "pelas", "pelos", "qual", "te", "lhe", "deles", "essas", "esses",
    "pelas", "este", "dele", "tu", "teus", "esta", "estao", "foi",
    "era", "eram", "ser", "sao", "ter", "estava", "estavam"
}

# Extensive, domain-specific Portuguese complaint lexicon (accent-normalized)
COMPLAINT_LEXICONS: Dict[str, List[str]] = {
    "DELIVERY_DELAY": [
        "atraso", "atrasou", "atrasada", "atrasado", "demorou", "demora", "demorado",
        "prazo", "fora do prazo", "nao recebi", "nao chegou", "nao foi entregue",
        "esperando", "aguardando entrega", "extraviado", "extravio", "correios",
        "data de entrega", "previsao de entrega", "ainda nao chegou", "nao entregaram",
        "nunca chegou", "tardio", "demora muito", "prazo vencido"
    ],
    "DAMAGED_DEFECTIVE": [
        "quebrado", "quebrada", "quebrados", "quebradas", "defeito", "com defeito",
        "danificado", "danificada", "danificados", "estragado", "estragada", "avariado",
        "avariada", "pessima qualidade", "ruim", "qualidade pessima", "nao funciona",
        "parou de funcionar", "arranhado", "amassado", "amassada", "rasgado", "rasgada",
        "furado", "solto", "quebrou", "veio quebrado", "veio com defeito", "fragil",
        "material ruim", "baixa qualidade", "falha"
    ],
    "CATALOG_MISMATCH": [
        "tamanho errado", "veio errado", "produto errado", "cor diferente", "cor errada",
        "divergente", "produto divergente", "diferente do anuncio", "propaganda enganosa",
        "nao condiz", "outro modelo", "modelo diferente", "faltando", "veio faltando",
        "veio so um", "veio apenas um", "incompleto", "incompativel", "foto diferente",
        "descricao errada", "nao e o mesmo", "nao e original", "veio menor", "veio maior",
        "peca errada", "faltou", "esperava outro"
    ],
    "SERVICE_REFUND": [
        "cancelar", "cancelamento", "cancelei", "estorno", "estornar", "estornado",
        "dinheiro de volta", "devolucao", "devolver", "troca", "trocar", "reembolso",
        "reembolsar", "nao respondem", "sem resposta", "sem retorno", "sac", "suporte",
        "nota fiscal", "cobrado", "cobranca", "atendimento pessimo", "falta de respeito",
        "procon", "justica", "processo", "ninguem responde", "engana o consumidor"
    ],
    "POSITIVE_SATISFACTION": [
        "otimo", "otima", "otimos", "otimas", "muito bom", "muito boa", "excelente",
        "perfeito", "perfeita", "recomendo", "super recomendo", "chegou antes",
        "antes do prazo", "rapido", "rapida", "entrega rapida", "tudo certo",
        "parabens", "adorei", "amei", "gostei muito", "satisfeito", "satisfeita"
    ]
}

def clean_review_tokens(text: str) -> str:
    """Removes noise, non-alphabetic chars, and filtered stopwords."""
    if not isinstance(text, str):
        return ""
    words = text.split()
    filtered = [w for w in words if len(w) > 1 and w not in PORTUGUESE_STOPWORDS]
    return " ".join(filtered)

def get_lexicon_label(text: str) -> Optional[str]:
    """
    Assigns high-confidence pseudo-label based on exact phrase/keyword hits.
    Returns the category with the highest matching keyword count, or None if ambiguous/no match.
    """
    if not text:
        return None
    
    scores: Dict[str, int] = {}
    for category, keywords in COMPLAINT_LEXICONS.items():
        score = 0
        for kw in keywords:
            # Word boundary matching or phrase match
            if " " in kw:
                if kw in text:
                    score += 3 # Multi-word phrases carry higher semantic weight
            else:
                pattern = r"\b" + re.escape(kw) + r"\b"
                if re.search(pattern, text):
                    score += 1
        if score > 0:
            scores[category] = score
            
    if not scores:
        return None
    
    # Return dominant category if it has a clear lead
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_cat, best_score = sorted_scores[0]
    
    # If tie or weak, only keep if best_score >= 1
    if len(sorted_scores) > 1 and sorted_scores[1][1] == best_score:
        return best_cat # tie breaker default
    return best_cat
