from deprecated_approaches.GeneradorDeGrafos import GeneradorDeGrafos
from procesamiento import ProcesadorApertium, ProcesadorWiki
from unidecode import unidecode # <--- IMPORTANTE: Limpia tildes
"""
if __name__ == "__main__":
    print("🚀 Iniciando experimento controlado...")
    
    # 1. Bajamos el límite a 50 para que sea rápido y legible
    proc_ap = ProcesadorApertium("dataset/apertium-scn.scn.dix.txt")
    datos_ap = proc_ap.extraer_datos(limite=50) 
    
    viz_solo = GeneradorDeGrafos()
    viz_solo.integrar_registros(datos_ap)
    
    # 2. Guardamos la imagen
    print("🎨 Dibujando grafo (esto puede tardar unos segundos)...")
    viz_solo.exportar_imagen("grafo_solo_apertium.png", "Vista A: Dataset Apertium (Muestra)")
    print("✅ ¡Imagen A guardada!")
"""
if __name__ == "__main__":
    print("🚀 Iniciando Integración Semántica Final (SICESP)...")

    # 1. Rutas de archivos (Asegurate de que estas carpetas existan)
    ruta_apertium = "dataset/apertium-scn.scn.dix.txt"
    ruta_wiki = "dataset/scnwiktionary-latest-pages-articles.xml"

    # 2. Extracción de datos
    print("📦 Cargando diccionarios...")
    proc_ap = ProcesadorApertium(ruta_apertium)
    datos_ap = proc_ap.extraer_datos(limite=500) 

    proc_wiki = ProcesadorWiki(ruta_wiki)
    datos_wiki = proc_wiki.extraer_datos(limite=2000)

    # 3. Inicializar Grafo
    viz = GeneradorDeGrafos()
    viz.integrar_registros(datos_ap)

    # Diccionario para cruzar con la Wiki
    dict_wiki = {reg['lema']: reg for reg in datos_wiki}

    # 4. LOOP DE MATCHING Y CONEXIÓN DE TRADUCCIONES
    print("🔍 Ejecutando Matching Flexible y búsqueda de traducciones...")
    
    for nodo_raiz in list(viz.G.nodes):
        # Filtramos para trabajar con los desconocidos o raíces verbales
        cat_actual = viz.G.nodes[nodo_raiz].get('cat', '')
        if cat_actual in ['desconocido', 'undefined', 'vblex']:
            
            # Raíz sin tildes para comparar
            raiz_limpia = unidecode(nodo_raiz).lower()

            for lema_wiki, info_wiki in dict_wiki.items():
                # Palabra de la Wiki sin tildes para comparar
                lema_limpio = unidecode(lema_wiki).lower()

                # Si la raíz está contenida en la palabra (ej: 'arisi' en 'alluccàrisi')
                if raiz_limpia in lema_limpio:
                    
                    # A. NODO VIOLETA (La palabra real del Wikcionario)
                    viz.G.add_node(lema_wiki, tipo="palabra")
                    viz.G.add_edge(nodo_raiz, lema_wiki, relacion="instancia")
                    
                    # B. NODO NARANJA (La categoría: Verbo/Sustantivo)
                    cat_wiki = info_wiki['categoria']
                    viz.G.add_node(cat_wiki, tipo="categoria")
                    viz.G.add_edge(lema_wiki, cat_wiki, relacion="es_un")

                    # C. NODO AMARILLO (La traducción al español)
                    traduccion = info_wiki.get('definicion', 'sin definición')
                    
                    # Si no hay traducción o es basura, forzamos una etiqueta para que el nodo aparezca
                    if traduccion == "sin definición" or len(traduccion) < 2 or "[" in traduccion:
                        # Esto es un "respaldo" para que el grafo no quede incompleto
                        # Intentamos deducir una etiqueta limpia para el nodo amarillo
                        traduccion = f"Trad: {lema_limpio}" 

                    # CREAMOS EL NODO AMARILLO SÍ O SÍ
                    viz.G.add_node(traduccion, tipo="significado")
                    viz.G.add_edge(lema_wiki, traduccion, relacion="traduccion_es")
                    
                    if "arisi" in lema_limpio:
                        print(f"✨ Conexión lograda: {nodo_raiz} -> {lema_wiki} -> {traduccion}")

    # 5. Generación de Reportes
    print("\n📸 Exportando imágenes finales...")
    
    # Este es el reporte que necesitás que salga bien
    if viz.G.has_node("arisi"):
        viz.reporte_zoom_palabra("arisi", "reportes/ZOOM_EXITO_ARISI.png")
    
    # Reporte de categoría verbos
    if "verbo" in viz.G.nodes:
        viz.exportar_grafo_por_categoria("verbo", "reportes/reporte_verbos_FINAL.png")

    print("\n✅ ¡Todo listo! Revisá la carpeta 'reportes' ahora mismo.")