import pandas as pd
import xml.etree.ElementTree as ET
import csv
import os

class XMLToCSVConverter:
    def __init__(self, xml_file):
        self.xml_file = xml_file

    def limpiar_texto(self, texto):
        if not texto: return ""
        # Limpiar restos de WikiText (corchetes, llaves) pero mantener acentos
        texto = texto.replace("[[", "").replace("]]", "").replace("{{", "").replace("}}", "")
        return texto.strip()

    def convertir(self, output_folder="csv_salida"):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # Parseo el XML
        tree = ET.parse(self.xml_file)
        root = tree.getroot()
        
        # Diccionario para agrupar por categoría (si el XML tiene esa info)
        # Si no, creamos un CSV unificado
        with open(f"{output_folder}/verbos_final.csv", mode='w', encoding='utf-8', newline='') as f_verbo:
            writer = csv.writer(f_verbo)
            writer.writerow(['Palabra', 'Conjugaciones', 'Traduccion'])
            
            for verbo in root.findall('.//verbo'):
                lema = verbo.get('lema')
                conj_node = verbo.find('conjugaciones')
                
                # Extraer formas y unirlas con un pipe para que Neo4j lo lea fácil
                formas = [f.text for f in conj_node.findall('forma')]
                lista_formas = "|".join(formas) if formas else ""
                
                writer.writerow([lema, lista_formas, ""])
        
        print(f"✅ CSV generado con éxito en UTF-8.")

# Uso
# converter = XMLToCSVConverter("Verbos_Tesis_Final.xml")
# converter.convertir()