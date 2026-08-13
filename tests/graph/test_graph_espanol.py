import pytest
from graph_retriever import GraphRetriever

CASES_ESPANOL = [
    {
        "input": "ultimo", 
        "esperados": {"ùltimu", "ùltumu", "ùrtimu", "ùrtumu"}
    },
    {
        "input": "ángel", 
        "esperados": {"àncilu", "ànciulu", "àngilu", "àngiulu"}
    },
    {
        "input": "amar", 
        "esperados": {"amari"}
    },
    {
        "input": "mañana", 
        "esperados": {"dumani", "matinu"}
    },
]

@pytest.mark.parametrize("termino, esperados", [
    (c["input"], c["esperados"]) for c in CASES_ESPANOL
])
def test_espanol_a_siciliano(termino, esperados):
    retriever = GraphRetriever()
    try:
        resultados = retriever.ejecutar_busqueda("espanol_a_siciliano", termino)
        recuperados = {item["Termino"] for item in resultados}
        assert esperados.intersection(recuperados), (
            f"Query: {termino} | esperados={esperados} | recuperados={recuperados}"
        )
    finally:
        retriever.close()