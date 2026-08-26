QUERIES = {
    # Búsqueda exacta en Siciliano -> Español (Exact Match)
    "siciliano_a_espanol": """
        MATCH (p:Palabra)
        WHERE toLower(p.Palabra) = toLower($termino)
        OPTIONAL MATCH (p)-[r:RELACIONADO_CON]-(relacionado)
        RETURN p.Palabra AS Termino, p.Traduccion AS Traduccion, collect(relacionado.Palabra) AS Relacionados
    """,
    
    # Búsqueda ampliada en Español -> Siciliano (Contains)
    "espanol_a_siciliano": """
        MATCH (p:Palabra)
        WHERE toLower(p.Traduccion) CONTAINS toLower($termino)
        RETURN p.Palabra AS Termino, p.Traduccion AS Traduccion
                ORDER BY CASE
                                         WHEN toLower(p.Traduccion) = toLower($termino)
                                             OR toLower(p.Traduccion) STARTS WITH toLower($termino) + ' '
                                             OR toLower(p.Traduccion) STARTS WITH toLower($termino) + '('
                                         THEN 0 ELSE 1 END,
                                 size(p.Traduccion)
    """,

    # Búsqueda de Modismos / Expresiones basadas en la estructura real del grafo (Relaciones)
    "buscar_modismo": """
        MATCH p = (n:Palabra)-[r:RELACIONADO_CON]-(m:Palabra)
        WHERE toLower(n.Palabra) CONTAINS toLower($termino)
           OR toLower(n.Traduccion) CONTAINS toLower($termino)
           OR toLower(m.Palabra) CONTAINS toLower($termino)
           OR toLower(m.Traduccion) CONTAINS toLower($termino)
        RETURN n.Palabra AS Termino, n.Traduccion AS Traduccion, collect(m.Palabra) AS Relacionados
    """
}