import csv

def limpiar_y_recategorizar(ruta_archivo_entrada, ruta_archivo_salida):
    datos_procesados = []
    
    with open(ruta_archivo_entrada, mode='r', encoding='utf-8') as f:
        lector = csv.reader(f)
        for fila in lector:
            if len(fila) < 3:
                continue
                
            palabra = fila[0].strip().lower()
            categoria_actual = fila[1].strip()
            definicion = fila[2].strip().lower()
            
            # --- LÓGICA DE DETECCIÓN AUTOMÁTICA ---
            # 1. Detección de Adjetivos por patrones de definición y sufijos típicos
            es_adjetivo = (
                definicion.startswith("que ") or
                definicion.startswith("relativo a") or
                definicion.startswith("perteneciente") or
                definicion.startswith("dicho de") or
                definicion.startswith("natural de") or
                (" de la " in definicion and "ciudad" not in definicion and "provincia" not in definicion and "región" not in definicion)
            )
            
            # 2. Detección de Adverbios por sufijación (-mente) o locuciones adverbiales
            es_adverbio = (
                definicion.endswith("mente") or
                definicion.startswith("en dirección") or
                definicion.startswith("de manera") or
                definicion.startswith("de forma")
            )

            # Determinación de la nueva categoría mediante lógica pura
            nueva_categoria = categoria_actual

            if es_adjetivo:
                nueva_categoria = "Adjetivo"
            elif es_adverbio:
                nueva_categoria = "Adverbio"
                
            # Actualizamos la fila con la categoría corregida
            fila_actualizada = fila.copy()
            fila_actualizada[1] = nueva_categoria
            
            # FILTRO CLAVE: Guardamos ÚNICAMENTE los que ESTABAN MAL categorizados 
            # (es decir, aquellos cuya categoría lógica resultante NO es Sustantivo)
            if nueva_categoria != 'Sustantivo':
                datos_procesados.append(fila_actualizada)

    # Guardamos el resultado en el archivo de salida
    with open(ruta_archivo_salida, mode='w', encoding='utf-8', newline='') as f:
        escritor = csv.writer(f)
        escritor.writerows(datos_procesados)
        
    print(f"Proceso finalizado. Total de registros mal categorizados detectados lógicamente: {len(datos_procesados)}")

# Ejemplo de ejecución del script automatizado para sustantivos
limpiar_y_recategorizar('corpus_csv/Sustantivo_Neo4j.csv', 'sustantivos_depurados.csv')