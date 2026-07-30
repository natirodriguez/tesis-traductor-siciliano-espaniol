import csv
import os
import sys

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from queries import QUERIES

# Importamos tu configuración desde el archivo config.py que mencionaste
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import config


class GraphRetriever:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD),
            max_connection_lifetime=30,
            max_connection_pool_size=50,
            connection_acquisition_timeout=60,
        )
        self.driver.verify_connectivity()
        print("--- Conectado a Neo4j correctamente ---")

    def close(self):
        self.driver.close()

    def _buscar_en_csv(self, termino):
        carpeta = os.path.join(os.path.dirname(__file__), "corpus_csv")
        archivos = [
            os.path.join(carpeta, "Adjetivo_Neo4j.csv"),
            os.path.join(carpeta, "Sustantivo_Neo4j.csv"),
            os.path.join(carpeta, "Verbo_Neo4j.csv"),
            os.path.join(carpeta, "Adverbio_Neo4j.csv"),
            os.path.join(carpeta, "Articulo_Neo4j.csv"),
            os.path.join(carpeta, "Pronombre_Neo4j.csv"),
        ]

        termino_norm = termino.strip().lower()

        for ruta in archivos:
            if not os.path.exists(ruta):
                continue
            with open(ruta, encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    if row.get("Palabra", "").strip().lower() == termino_norm:
                        return [{
                            "Termino": row.get("Palabra", ""),
                            "Traduccion": row.get("Traduccion", ""),
                            "Relacionados": []
                        }]

        return []

    def ejecutar_busqueda(self, tipo_query, termino):
        query = QUERIES.get(tipo_query)

        if not query:
            raise ValueError(f"La consulta '{tipo_query}' no existe.")

        try:
            with self.driver.session() as session:
                result = session.run(query, termino=termino)
                datos = result.data()
                if datos:
                    return datos
        except Neo4jError as exc:
            print(f"Error al ejecutar la consulta en Neo4j: {exc}")
        except Exception as exc:
            print(f"Error inesperado: {exc}")

        return self._buscar_en_csv(termino)