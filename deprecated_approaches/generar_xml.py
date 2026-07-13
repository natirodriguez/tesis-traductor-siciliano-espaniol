import os
import re
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom

def crear_xml_enriquecido():
    print("\n=== GENERANDO CORPUS EN FORMATO XML PARA LA TESIS ===")
    
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    
    # Intentamos detectar el nombre del Excel original
    ruta_excel = os.path.join(carpeta_actual, "Analisis_Cobertura_Final2.xlsx")
    ruta_apertium = os.path.join(carpeta_actual, "dataset/apertium-scn.scn.dix.txt")
    
    # --- CONTROL DE ARCHIVOS ---
    if not os.path.exists(ruta_excel):
        # Si no encuentra el .xlsx solo, probamos con el nombre del CSV exportado
        ruta_alternativa = os.path.join(carpeta_actual, "Analisis_Cobertura_Final2.xlsx - Verbo.csv")
        if os.path.exists(ruta_alternativa):
            ruta_excel = ruta_alternativa
        else:
            print(f"❌ Error: No se encuentra tu archivo de datos del Wiktionary.")
            print(f"   Asegurate de que el archivo esté en la carpeta: '{carpeta_actual}'")
            return

    if not os.path.exists(ruta_apertium):
        print(f"❌ Error: No se encuentra el archivo de Apertium.")
        print(f"   Asegurate de que 'apertium-scn.scn.dix.txt' esté en: '{carpeta_actual}'")
        return

    # 1. Cargar Apertium en memoria de forma segura
    print(f"📖 Leyendo Apertium ({os.path.basename(ruta_apertium)})...")
    mapeo_conjugaciones = {}
    with open(ruta_apertium, "r", encoding="utf-8", errors="ignore") as f:
        contenido = f.read()
    entradas = re.findall(r'<l>([^<]+)</l>.*?<r>([^<s]+)', contenido)
    
    for forma, lema_padre in entradas:
        lema = lema_padre.strip()
        if lema not in mapeo_conjugaciones:
            mapeo_conjugaciones[lema] = set()
        mapeo_conjugaciones[lema].add(forma.strip())
        
    print(f"✓ Apertium procesado con éxito.")

    # 2. Cargar los datos de los verbos
    print(f"📊 Abriendo tu archivo de verbos: {os.path.basename(ruta_excel)}")
    try:
        if ruta_excel.endswith(".csv"):
            df_verbos = pd.read_csv(ruta_excel)
        else:
            df_verbos = pd.read_excel(ruta_excel, sheet_name="Verbo")
    except Exception as e:
        print(f"❌ Error al leer los datos de verbos: {e}")
        return

    # 3. Construir la estructura del árbol XML
    raiz = ET.Element("corpus", diccionarios="Wiktionary+Apertium", idioma="siciliano")
    
    print("⏳ Organizando estructura de nodos XML...")
    
    for idx, fila in df_verbos.iterrows():
        palabra = str(fila["Palabra"]).strip()
        traduccion = str(fila["Traduccion"]).strip() if pd.notna(fila["Traduccion"]) else ""
        estado = str(fila["Estado"]).strip()
        
        # Nodo principal de cada verbo
        nodo_verbo = ET.SubElement(raiz, "verbo", lema=palabra, estado=estado)
        
        nodo_trad = ET.SubElement(nodo_verbo, "traduccion_es")
        nodo_trad.text = traduccion
        
        nodo_conjugaciones = ET.SubElement(nodo_verbo, "conjugaciones", fuente="Apertium")
        
        if palabra in mapeo_conjugaciones:
            formas_ordenadas = sorted(list(mapeo_conjugaciones[palabra]))
            for forma in formas_ordenadas:
                nodo_forma = ET.SubElement(nodo_conjugaciones, "forma")
                nodo_forma.text = forma
        else:
            nodo_conjugaciones.set("estado", "sin_registro_morfologico")

    # 4. Formatear XML con sangrías elegantes ("Pretty Print")
    xml_puro = ET.tostring(raiz, encoding="utf-8")
    reparsed = minidom.parseString(xml_puro)
    xml_formateado = reparsed.toprettyxml(indent="    ")
    
    # 5. Guardar el archivo final
    ruta_salida_xml = os.path.join(carpeta_actual, "Verbos_Enriquecidos.xml")
    with open(ruta_salida_xml, "w", encoding="utf-8") as f:
        f.write(xml_formateado)
        
    print(f"\n✨ ¡CONVERSIÓN A XML COMPLETADA!")
    print(f"➡ Archivo generado en: '{os.path.basename(ruta_salida_xml)}'")

if __name__ == "__main__":
    crear_xml_enriquecido()