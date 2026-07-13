import pandas as pd
import csv

ETIQUETAS = [
    "1s", "2s", "3s", "1p", "2p", "3p",  # Presente
    "1s_pass", "2s_pass", "3s_pass", "1p_pass", "2p_pass", "3p_pass" # Pretérito
]

def etiquetar_conjugaciones(ruta_input, ruta_output):
    df = pd.read_csv(ruta_input, encoding='utf-8')
    
    # 1. FILTRADO DE CALIDAD: 
    # Solo nos quedamos con filas que tengan algo en la columna 'Conjugaciones'
    # Esto elimina automáticamente los sustantivos/adjetivos mal etiquetados como verbos
    total_antes = len(df)
    df = df[df['Conjugaciones'].notna() & (df['Conjugaciones'] != "")]
    total_despues = len(df)
    
    print(f"🧹 Limpieza: Eliminadas {total_antes - total_despues} entradas sin conjugación.")
    
    def procesar_celda(celda):
        formas = [f.strip().replace('"', '') for f in str(celda).split(',')]
        etiquetado = []
        for i, forma in enumerate(formas):
            if i < len(ETIQUETAS):
                etiquetado.append(f"{ETIQUETAS[i]}:{forma}")
        return ";".join(etiquetado)

    df['Conjugaciones'] = df['Conjugaciones'].apply(procesar_celda)
    df.to_csv(ruta_output, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
    print(f"✅ Archivo etiquetado listo: {ruta_output}")

# Ejecución
etiquetar_conjugaciones("corpus_csv/Verbo_Neo4j.csv", "corpus_csv/Verbo_Etiquetado_Neo4j.csv")