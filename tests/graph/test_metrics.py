from graph_retriever import GraphRetriever

CASES = [
    {
        "tipo": "siciliano_a_espanol",
        "input": "sentiri",
        "esperados": {"sentiri"},
    },
    {
        "tipo": "siciliano_a_espanol",
        "input": "çiuraru",
        "esperados": {"çiuraru"},
    },
    {
        "tipo": "siciliano_a_espanol",
        "input": "amicu",
        "esperados": {"amicu"},
    },
    # 2. Casos de Español -> Siciliano (Criterio contains)
    {
        "tipo": "espanol_a_siciliano",
        "input": "ultimo",  # Debería recuperar las variantes ùltimu, ùltumu, ùrtimu, ùrtumu
        "esperados": {"ùltimu", "ùltumu", "ùrtimu", "ùrtumu"},
    },
    {
        "tipo": "espanol_a_siciliano",
        "input": "ángel",   # Debería recuperar àncilu, ànciulu, àngilu, àngiulu
        "esperados": {"àncilu", "ànciulu", "àngilu", "àngiulu"},
    },
    {
        "tipo": "espanol_a_siciliano",
        "input": "amar",    # Debería recuperar amari
        "esperados": {"amari"},
    },
    {
        "tipo": "espanol_a_siciliano",
        "input": "mañana",    
        "esperados": {"dumani", "matinu"},
    },

    # 3. Casos de Modismos (¡Ya probados y funcionando!)
    {
        "tipo": "buscar_modismo",
        "input": "A megghiu parola è chidda ca 'un si dici",
        "esperados": {"'A megghiu parola è chidda ca 'un si dici", "A megghiu parola è chidda ca 'un si dici"}, # Aceptamos ambas variantes
    },
    {
        "tipo": "buscar_modismo",
        "input": "Cu mancia fa muddichi",
        "esperados": {"Cu mancia fa muddichi"},
    },
    {
        "tipo": "buscar_modismo",
        "input": "Chiù scuru 'i menzannotti un pò fari",
        "esperados": {"Chiù scuru 'i menzannotti un pò fari"}
    },
    {
        "tipo": "buscar_modismo",
        "input": "En boca cerrada no entran moscas",
        "esperados": {"A megghiu parola è chidda ca 'un si dici", "'A megghiu parola è chidda ca 'un si dici"},
    },
]

def evaluar_caso(caso, top_k=None):
    retriever = GraphRetriever()
    try:
        resultados = retriever.ejecutar_busqueda(caso["tipo"], caso["input"])
        recuperados = [item["Termino"] for item in resultados]

        if top_k is not None:
            recuperados = recuperados[:top_k]

        recuperados_set = set(recuperados)
        esperados = set(caso["esperados"])
        interseccion = recuperados_set & esperados

        hit = 1 if interseccion else 0
        precision = len(interseccion) / max(len(recuperados_set), 1)
        recall = len(interseccion) / max(len(esperados), 1)

        return {
            "input": caso["input"],
            "tipo": caso["tipo"],
            "esperados": esperados,
            "recuperados": recuperados_set,
            "hit": hit,
            "precision": precision,
            "recall": recall,
        }
    finally:
        retriever.close()

def test_metricas_agregadas():
    resultados = [evaluar_caso(c, top_k=5) for c in CASES]

    hit_rate = sum(r["hit"] for r in resultados) / len(resultados)
    precision_prom = sum(r["precision"] for r in resultados) / len(resultados)
    recall_prom = sum(r["recall"] for r in resultados) / len(resultados)

    imprimir_reporte_metricas(resultados, hit_rate, precision_prom, recall_prom)

    assert 0 <= hit_rate <= 1
    assert 0 <= precision_prom <= 1
    assert 0 <= recall_prom <= 1

    print({
        "n_casos": len(resultados),
        "hit_rate": hit_rate,
        "precision_promedio": precision_prom,
        "recall_promedio": recall_prom,
    })

def imprimir_reporte_metricas(resultados, hit_rate, precision_prom, recall_prom):
    """Método exclusivo para formatear y mostrar los resultados en la consola."""
    print("\n" + "="*50)
    print("       REPORTE DE MÉTRICAS - GRAPHRAG")
    print("="*50)
    for i, r in enumerate(resultados, 1):
        print(f"[{i}] Input: {r['input']} ({r['tipo']})")
        print(f"    -> Hit: {r['hit']} | Precision: {r['precision']:.2f} | Recall: {r['recall']:.2f}")
    
    print("="*50)
    print("             RESUMEN GLOBAL")
    print("="*50)
    print(f" * Total de casos evaluados : {len(resultados)}")
    print(f" * Hit Rate global          : {hit_rate * 100:.2f}% (Promedio: {hit_rate:.4f})")
    print(f" * Precisión promedio       : {precision_prom:.4f}")
    print(f" * Recall promedio          : {recall_prom:.4f}")
    print("="*50 + "\n")