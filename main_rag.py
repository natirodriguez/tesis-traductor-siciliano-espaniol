from graph_retriever import GraphRetriever

def main():
    # 1. Instanciamos el retriever
    retriever = GraphRetriever()
    
    # 2. Definimos una prueba rápida
    # Usamos una palabra que existe en el corpus local
    termino_prueba = "oscuro"
    
    print(f"--- Consultando grafo por: {termino_prueba} ---")
    
    # 3. Ejecutamos la búsqueda (usando la key definida en queries.py)
    resultado = retriever.ejecutar_busqueda("buscar_por_traduccion", termino_prueba)
    
    # 4. Mostramos el resultado
    if resultado:
        for item in resultado:
            print(f"Palabra: {item['Termino']}")
            print(f"Traducción: {item['Traduccion']}")
            if 'Relacionados' in item:
                print(f"Relacionados: {item['Relacionados']}")
            else:
                print("Relacionados: []")
    else:
        print("No se encontraron resultados o hubo un error.")
    
    # 5. Cerramos la conexión correctamente
    retriever.close()

if __name__ == "__main__":
    main()