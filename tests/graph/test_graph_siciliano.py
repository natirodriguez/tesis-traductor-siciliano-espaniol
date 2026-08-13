import pytest
from graph_retriever import GraphRetriever

CASES_SICILIANO = [
    {"input": "sentiri", "esperados": {"sentiri"}},
    {"input": "çiuraru", "esperados": {"çiuraru"}},
    {"input": "amicu", "esperados": {"amicu"}},  # ejemplo
]

@pytest.mark.parametrize("termino, esperados", [
    (c["input"], c["esperados"]) for c in CASES_SICILIANO
])
def test_siciliano_a_espanol(termino, esperados):
    retriever = GraphRetriever()
    try:
        resultados = retriever.ejecutar_busqueda("siciliano_a_espanol", termino)
        recuperados = {item["Termino"] for item in resultados}
        assert esperados.issubset(recuperados), (
            f"Query: {termino} | esperados={esperados} | recuperados={recuperados}"
        )
    finally:
        retriever.close()