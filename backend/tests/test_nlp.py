import pytest
from backend.app.nlp.topic_tagger import topic_tagger

def test_delivery_delay_classification():
    text = "meu pedido esta com atraso na entrega ja passou o prazo e ainda nao recebi nada"
    res = topic_tagger.predict(text)
    assert res["topic"] == "DELIVERY_DELAY"
    assert res["confidence"] > 0.5
    assert "DELIVERY_DELAY" in res["probabilities"]

def test_damaged_defective_classification():
    text = "a mercadoria chegou quebrada produto com defeito e de pessima qualidade"
    res = topic_tagger.predict(text)
    assert res["topic"] == "DAMAGED_DEFECTIVE"
    assert res["confidence"] > 0.5

def test_catalog_mismatch_classification():
    text = "veio tamanho errado e modelo divergente do que constava na foto do anuncio"
    res = topic_tagger.predict(text)
    assert res["topic"] == "CATALOG_MISMATCH"
    assert res["confidence"] > 0.5

def test_service_refund_classification():
    text = "ninguem responde no sac quero meu dinheiro de volta e cancelamento urgente com estorno"
    res = topic_tagger.predict(text)
    assert res["topic"] == "SERVICE_REFUND"
    assert res["confidence"] > 0.5

def test_positive_satisfaction_classification():
    text = "produto excelente muito bom chegou antes do prazo recomendo a todos"
    res = topic_tagger.predict(text)
    assert res["topic"] == "POSITIVE_SATISFACTION"
    assert res["confidence"] > 0.5

def test_empty_and_noise_handling():
    assert topic_tagger.predict("")["topic"] == "NO_COMMENT"
    assert topic_tagger.predict(None)["topic"] == "NO_COMMENT"
    assert topic_tagger.predict("   ")["topic"] == "NO_COMMENT"

def test_batch_prediction():
    batch = [
        "atrasou a entrega",
        "produto quebrado",
        "tamanho errado",
        ""
    ]
    preds = topic_tagger.predict_batch(batch)
    assert len(preds) == 4
    assert preds[0]["topic"] == "DELIVERY_DELAY"
    assert preds[1]["topic"] == "DAMAGED_DEFECTIVE"
    assert preds[2]["topic"] == "CATALOG_MISMATCH"
    assert preds[3]["topic"] == "NO_COMMENT"
