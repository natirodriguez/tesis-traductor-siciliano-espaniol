QUERIES = {
    "buscar_por_palabra": """
        MATCH (p:Palabra)
        WHERE toLower(p.Palabra) = toLower($termino)
        OPTIONAL MATCH (p)-[r:RELACIONADO_CON]-(relacionado)
        RETURN p.Palabra AS Termino, p.Traduccion AS Traduccion, collect(relacionado.Palabra) AS Relacionados
    """,
    "buscar_por_traduccion": """
        MATCH (p:Palabra)
        WHERE toLower(p.Traduccion) CONTAINS toLower($termino)
           OR toLower(p.Palabra) CONTAINS toLower($termino)
        RETURN p.Palabra AS Termino, p.Traduccion AS Traduccion
    """
}