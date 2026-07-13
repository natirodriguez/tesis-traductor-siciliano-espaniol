import os
import pandas as pd

class ConversorCompletoNeo4j:
    def __init__(self, ruta_archivo):
        self.ruta = ruta_archivo

    def extraer_datos(self):
        if not os.path.exists(self.ruta):
            print(f"❌ Error: No se encuentra tu archivo Excel en '{self.ruta}'")
            return
            
        print(f"\n📊 Abriendo tu archivo Excel: {os.path.basename(self.ruta)}")
        
        try:
            excel_file = pd.ExcelFile(self.ruta)
            pestañas = excel_file.sheet_names
        except Exception as e:
            print(f"❌ Error al intentar abrir el archivo Excel: {e}")
            return

        categorias_validas = ["Verbo", "Sustantivo", "Adjetivo", "Adverbio", "Articulo"]

        # Creamos la carpeta 'corpus_csv' si no existe
        carpeta_salida = os.path.join(os.path.dirname(self.ruta), "corpus_csv")
        if not os.path.exists(carpeta_salida):
            os.makedirs(carpeta_salida)

        print("⏳ Iniciando la exportación a formatos CSV para Neo4j (UTF-8)...")

        for pestaña in pestañas:
            if pestaña not in categorias_validas:
                continue

            print(f" 💾 Procesando categoría: [{pestaña}]")
            
            # Leemos la pestaña actual del Excel
            df_categoria = pd.read_excel(self.ruta, sheet_name=pestaña)
            
            # Limpieza: Rellenar nulos para evitar errores en Neo4j
            df_categoria = df_categoria.fillna("")

            # Guardamos el nombre del archivo CSV
            nombre_csv = f"{pestaña}_Neo4j.csv"
            ruta_salida_csv = os.path.join(carpeta_salida, nombre_csv)

            # GUARDADO EN UTF-8 (Crítico para Neo4j y caracteres especiales)
            df_categoria.to_csv(ruta_salida_csv, index=False, encoding="utf-8")
            print(f"   ✓ Generado con éxito: '{nombre_csv}'")

        print(f"\n✨ ¡PROCESO COMPLETADO!")
        print(f"➡ Archivos listos en la carpeta: {carpeta_salida}")

if __name__ == "__main__":
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_mi_excel = os.path.join(carpeta_actual, "Analisis_Cobertura_Final2.xlsx")

    print("\n=== SISTEMA DE CONVERSIÓN PARA NEO4J ===")
    conversor = ConversorCompletoNeo4j(ruta_mi_excel)
    conversor.extraer_datos()