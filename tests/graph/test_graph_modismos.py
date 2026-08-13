# test_graph_modismos.py
import pytest
from graph_retriever import GraphRetriever

CASES_MODISMOS = [
    {
        "input": "A megghiu parola è chidda ca 'un si dici", 
        "esperados": {"A megghiu parola è chidda ca 'un si dici"}
    },
    {
        "input": "Cu mancia fa muddichi", 
        "esperados": {"Cu mancia fa muddichi"}
    },
    {
        "input": "Chiù scuru 'i menzannotti a bit fari", 
        "esperados": {"Chiù scuru 'i menzannotti a bit fari"}
    },
]

@pytest.mark.parametrize("termino, esperados", [
    (c["input"], c["esperados"]) for c in CASES_MODISMOS
])
def test_busqueda_modismos(termino, esperados):
    retriever = GraphRetriever()
    try:
        resultados = retriever.ejecutar_busqueda("buscar_modismo", termino)
        recuperados = {item["Termino"] for item in resultados}
        assert esperados.intersection(recuperados), (
            f"Query: {termino} | esperados={esperados} | recuperados={recuperados}"
        )
    finally:
        retriever.close()