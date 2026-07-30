import csv

def limpiar_y_recategorizar(ruta_archivo_entrada, ruta_archivo_salida):
    datos_procesados = []
    
    terminos_excepcion_verbos = {
        # Agregá aquí palabras específicas si es necesario
    }

    with open(ruta_archivo_entrada, mode='r', encoding='utf-8') as f:
        lector = csv.reader(f)
        for fila in lector:
            if len(fila) < 3:
                continue
                
            palabra = fila[0].strip().lower()
            categoria_actual = fila[1].strip()
            definicion = fila[2].strip().lower()
            
            # Criterios de reclasificación
            es_verbo = (
                definicion.startswith("participio") or
                definicion.startswith("infinitivo") or
                definicion.startswith("gerundio") or
                definicion.startswith("tercera persona") or
                definicion.startswith("primera persona") or
                " del verbo " in definicion or
                palabra in terminos_excepcion_verbos
            )
            
            es_adjetivo = (
                definicion.startswith("que ") or
                definicion.startswith("relativo a") or
                definicion.startswith("perteneciente") or
                (" de la " in definicion and not "ciudad" in definicion)
            )
            
            es_adverbio = (
                definicion.endswith("mente") or
                " en dirección " in definicion or
                " de manera " in definicion
            )

            nueva_categoria = categoria_actual
            
            if es_verbo:
                nueva_categoria = "Verbo"
            elif es_adjetivo:
                nueva_categoria = "Adjetivo"
            elif es_adverbio:
                nueva_categoria = "Adverbio"
                
            # Actualizo la fila con la categoría corregida
            fila_actualizada = fila.copy()
            fila_actualizada[1] = nueva_categoria
            
            # FILTRO INVERTIDO: Solo guardamos los que NO quedaron como Sustantivo
            if nueva_categoria != 'Sustantivo':
                datos_procesados.append(fila_actualizada)

    with open(ruta_archivo_salida, mode='w', encoding='utf-8', newline='') as f:
        escritor = csv.writer(f)
        escritor.writerows(datos_procesados)
        
    print(f"Proceso finalizado. Total de registros re-categorizados guardados: {len(datos_procesados)}")

# Ejemplo de ejecución del script automatizado
limpiar_y_recategorizar('corpus_csv/Adjetivo_Neo4j.csv', 'adjetivos_depurados.csv')