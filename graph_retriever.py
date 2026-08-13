import csv
import os
import sys
import unicodedata
import re

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from queries import QUERIES

# Importamos tu configuración desde el archivo config.py que mencionaste
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import config


class GraphRetriever:
    def __init__(self):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(
                config.NEO4J_URI,
                auth=(config.NEO4J_USER, config.NEO4J_PASSWORD),
                max_connection_lifetime=30,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60,
            )
            self.driver.verify_connectivity()
            print("--- Conectado a Neo4j correctamente ---")
        except Exception as exc:
            print(f"Neo4j no disponible, se usará CSV local: {exc}")
            if self.driver is not None:
                self.driver.close()
            self.driver = None

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def normalizar_termino(self, termino):
        """
        [ETAPA DE PROCESAMIENTO INTERMEDIO]
        Normalización previa del término: limpieza de espacios, 
        estandarización a minúsculas, remoción de tildes y limpieza de apóstrofes/comillas.
        """
        if not termino:
            return ""
        
        # 1. Estandarizar a minúsculas y quitar espacios extremos
        termino_limpio = termino.strip().lower()
        
        # 2. Normalizar distintos tipos de apóstrofes o comillas simples comunes (' ’ `)
        for apotrofe in ["'", "’", "`"]:
            termino_limpio = termino_limpio.replace(apotrofe, "")
            
        # 3. Remover tildes para robustecer la búsqueda
        termino_sin_tildes = ''.join(
            c for c in unicodedata.normalize('NFD', termino_limpio)
            if unicodedata.category(c) != 'Mn'
        )
        
        return termino_sin_tildes

    def buscar_en_csv(self, termino_norm):
        """
        [ETAPA DE RECUPERACIÓN - FALLBACK LOCAL]
        Recuperación alternada desde los archivos CSV locales en caso de que Neo4j no esté disponible.
        """
        carpeta = os.path.join(os.path.dirname(__file__), "corpus_csv")
        archivos = [
            os.path.join(carpeta, "Adjetivo_Neo4j.csv"),
            os.path.join(carpeta, "Sustantivo_Neo4j.csv"),
            os.path.join(carpeta, "Verbo_Neo4j.csv"),
            os.path.join(carpeta, "Adverbio_Neo4j.csv"),
            os.path.join(carpeta, "Articulo_Neo4j.csv"),
            os.path.join(carpeta, "Pronombre_Neo4j.csv"),
        ]

        resultados = []
        for ruta in archivos:
            if not os.path.exists(ruta):
                continue
            with open(ruta, encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    palabra_csv = self.normalizar_termino(row.get("Palabra", ""))
                    traduccion_csv = self.normalizar_termino(row.get("Traduccion", ""))
                    
                    if termino_norm == palabra_csv:
                        resultados.append({
                            "Termino": row.get("Palabra", ""),
                            "Traduccion": row.get("Traduccion", ""),
                            "Relacionados": []
                        })
                    elif termino_norm in traduccion_csv:
                        resultados.append({
                            "Termino": row.get("Palabra", ""),
                            "Traduccion": row.get("Traduccion", ""),
                            "Relacionados": []
                        })
        return resultados

    def ejecutar_busqueda(self, tipo_query, termino):
        """Orquestador central del flujo RAG."""
        termino_norm = self.normalizar_termino(termino)
        query = QUERIES.get(tipo_query)
        if not query:
            raise ValueError(f"La consulta '{tipo_query}' no existe.")

        # 1. Intentar recuperación en Neo4j
        datos = self.buscar_en_neo4j(query, termino, termino_norm, tipo_query)

        # 2. Filtrar por relevancia exacta
        datos_filtrados = self.filtrar_resultados(datos, termino_norm)
        if datos_filtrados:
            return datos_filtrados

        # 3. Fallback a CSV si no hay resultados en Neo4j
        return self.buscar_en_csv(termino_norm)

    def buscar_en_neo4j(self, query, termino_raw, termino_norm, tipo_query):
        """Ejecuta la lógica específica de consulta al grafo."""
        if self.driver is None:
            return []

        # Intentar variantes de texto
        variantes = self.generar_variantes(termino_raw, termino_norm)
        with self.driver.session() as session:
            for var in variantes:
                resultado = session.run(query, termino=var).data()
                if resultado: return resultado

        # Si es modismo, intentar búsqueda por tokens como último recurso
        if tipo_query == 'buscar_modismo':
            return self.buscar_modismo_por_tokens(query, termino_norm)
        
        return []

    def filtrar_resultados(self, datos, termino_norm):
        """Separa la lógica de post-procesamiento."""
        return [
            d for d in datos 
            if termino_norm == self.normalizar_termino(d.get('Termino', '')) 
            or termino_norm == self.normalizar_termino(d.get('Traduccion', ''))
        ]

    def generar_variantes(self, raw, norm):
        """Encapsula la generación de strings para consulta."""
        return list(set([
            raw.strip(), raw.strip().lower(), norm, 
            norm.replace("'", ""), raw.strip().lstrip("'")
        ]))

    def buscar_modismo_por_tokens(self, query, termino_norm):
        """Lógica especializada para modismos."""
        tokens = sorted(set(re.findall(r"\w+", termino_norm)), key=lambda x: -len(x))
        with self.driver.session() as session:
            for tok in tokens:
                if len(tok) >= 3:
                    resultado = session.run(query, termino=tok).data()
                    if resultado: return resultado
        return []