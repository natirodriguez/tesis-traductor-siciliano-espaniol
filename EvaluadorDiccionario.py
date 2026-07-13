import xml.etree.ElementTree as ET
import re
import pandas as pd

class EvaluadorDiccionarioPro:
    def __init__(self, ruta_xml):
        self.ruta = ruta_xml
        # Filtros estrictos para evitar falsos positivos
        self.categorias_objetivo = {
            "Sustantivo": [r"{{-sust-", r"sustantivu"],
            "Verbo": [r"{{-verb-", r"verbu"],
            "Adjetivo": [r"{{-adj-", r"aggittivu"],
            "Adverbio": [r"{{-adv-", r"avverbiu"],
            "Articulo": [r"{{-art-", r"artìculu"],
            "Pronombre": [r"{{-pron-", r"prunoma"],
            "Conjuncion": [r"{{-conj-", r"cungiunzioni"]
        }
        
        # Desinencias necesarias para calcular las conjugaciones automáticas
        self.desinencias_verbos = {
            "ari": ["u", "as", "a", "amu", "ati", "anu", "ai", "asti", "au", "àmuru", "àstivu", "àranu"],
            "eri": ["u", "i", "i", "emu", "iti", "inu", "ii", "isti", "ìu", "èmuru", "ìstivu", "èranu"],
            "iri": ["u", "i", "i", "imu", "iti", "inu", "ii", "isti", "ìu", "ìmuru", "ìstivu", "ìranu"]
        }

    def limpiar_traduccion(self, texto):
        if not texto: return "Unknown"
        # Eliminar etiquetas de Wiki, corchetes y llaves
        limpio = re.sub(r'[\[\]{}#*]', '', texto).strip()
        # Si tiene varias líneas, las unimos con comas
        limpio = ", ".join([line.strip() for line in limpio.split('\n') if line.strip()])
        
        if len(limpio) < 2 or limpio.startswith(':'):
            return "Unknown"
        return limpio

    def extraer_y_evaluar_sin_filtro(self):
        namespace = {'mw': 'http://www.mediawiki.org/xml/export-0.11/'}
        try:
            tree = ET.parse(self.ruta)
            root = tree.getroot()
        except Exception as e:
            print(f"Error: {e}")
            return

        registros = []
        
        for page in root.findall('mw:page', namespace):
            titulo = page.find('mw:title', namespace).text
            # Filtro de seguridad para páginas que no son palabras
            if any(x in titulo for x in [":", "/", "MediaWiki", "Template"]): continue
            
            texto_nodo = page.find('mw:revision/mw:text', namespace)
            texto = texto_nodo.text if texto_nodo is not None else ""
            
            if texto and "{{-scn-}}" in texto:
                categoria_final = "Otros"
                for cat, patrones in self.categorias_objetivo.items():
                    if any(re.search(patron, texto, re.IGNORECASE) for patron in patrones):
                        categoria_final = cat
                        break
                
                if categoria_final == "Otros": continue

                res_tradu = "Unknown"
                idioma_final = "Unknown"
                # Buscamos TODAS las ocurrencias de español e italiano
                match_es = re.findall(r"(?:spagnolu|{{es}})\s*:\s*(.*?)(?=\n|{{|\[\[Category:|$)", texto, re.IGNORECASE)
                match_it = re.findall(r"(?:talianu|{{it}})\s*:\s*(.*?)(?=\n|{{|\[\[Category:|$)", texto, re.IGNORECASE)

                if match_es:
                    res_tradu = self.limpiar_traduccion(" / ".join(match_es))
                    idioma_final = "Español"
                elif match_it:
                    res_tradu = self.limpiar_traduccion(" / ".join(match_it))
                    idioma_final = "Italiano"

                # --- NUEVO: EXTRAER CONJUGACIONES EN UNA SOLA COLUMNA ---
                lista_conjugaciones = ""
                if categoria_final == "Verbo":
                    # Intentamos extraer la raíz del verbo buscando el formato clásico de desinencia en la wiki
                    # Si termina en -ari, -eri o -iri, calculamos su raíz base de manera segura
                    sufijo = titulo[-3:].lower()
                    if sufijo in self.desinencias_verbos:
                        raiz_calculada = titulo[:-3]
                        formas = [f"{raiz_calculada}{des}" for des in self.desinencias_verbos[sufijo]]
                        # Guardamos las formas encontradas unidas por comas
                        lista_conjugaciones = ", ".join(formas)

                registros.append({
                    "Palabra": titulo,
                    "Categoria": categoria_final,
                    "Traduccion": res_tradu,
                    "Idioma": idioma_final, 
                    "Conjugaciones": lista_conjugaciones,
                    "Estado": "OK" if res_tradu != "Unknown" else "FALTA"
                })

        if not registros:
            print("No se encontraron datos.")
            return

        df = pd.DataFrame(registros)
        with pd.ExcelWriter("Analisis_Cobertura_Final2.xlsx", engine="openpyxl") as writer:
            # Resumen estadístico
            resumen = df.groupby(['Categoria', 'Estado']).size().unstack(fill_value=0)
            for col in ['OK', 'FALTA']:
                if col not in resumen: resumen[col] = 0
            
            resumen['Total'] = resumen['OK'] + resumen['FALTA']
            resumen['% Cobertura'] = (resumen['OK'] / resumen['Total']) * 100
            resumen.to_excel(writer, sheet_name="ESTADISTICAS")

            # Hojas por categorías (Mantienen tu estructura exacta, pero con la nueva columna)
            for cat in self.categorias_objetivo.keys():
                df_cat = df[df["Categoria"] == cat].sort_values("Palabra")
                if not df_cat.empty:
                    df_cat.to_excel(writer, sheet_name=cat, index=False)

        print("✨ Archivo 'Analisis_Cobertura_Final.xlsx' generado.")
        print("\n--- RESUMEN DE COBERTURA (Prioridad ES > IT) ---")
        print(resumen[['OK', 'FALTA', '% Cobertura']])

    def extraer_y_evaluar(self):
        namespace = {'mw': 'http://www.mediawiki.org/xml/export-0.11/'}
        try:
            tree = ET.parse(self.ruta)
            root = tree.getroot()
        except Exception as e:
            print(f"Error: {e}")
            return

        registros = []
        for page in root.findall('mw:page', namespace):
            titulo = page.find('mw:title', namespace).text
            if any(x in titulo for x in [":", "/", "MediaWiki", "Template"]): continue
            
            texto_nodo = page.find('mw:revision/mw:text', namespace)
            texto = texto_nodo.text if texto_nodo is not None else ""
            
            if texto and "{{-scn-}}" in texto:
                categoria_final = "Otros"
                for cat, patrones in self.categorias_objetivo.items():
                    if any(re.search(patron, texto, re.IGNORECASE) for patron in patrones):
                        categoria_final = cat
                        break
                
                if categoria_final == "Otros": continue

                res_tradu = "Unknown"
                idioma_final = "Unknown"
                match_es = re.findall(r"(?:spagnolu|{{es}})\s*:\s*(.*?)(?=\n|{{|\[\[Category:|$)", texto, re.IGNORECASE)
                match_it = re.findall(r"(?:talianu|{{it}})\s*:\s*(.*?)(?=\n|{{|\[\[Category:|$)", texto, re.IGNORECASE)

                if match_es:
                    res_tradu = self.limpiar_traduccion(" / ".join(match_es))
                    idioma_final = "Español"
                elif match_it:
                    res_tradu = self.limpiar_traduccion(" / ".join(match_it))
                    idioma_final = "Italiano"

                lista_conjugaciones = ""
                if categoria_final == "Verbo":
                    sufijo = titulo[-3:].lower()
                    if sufijo in self.desinencias_verbos:
                        raiz_calculada = titulo[:-3]
                        formas = [f"{raiz_calculada}{des}" for des in self.desinencias_verbos[sufijo]]
                        lista_conjugaciones = ", ".join(formas)

                registros.append({
                    "Palabra": titulo,
                    "Categoria": categoria_final,
                    "Traduccion": res_tradu,
                    "Idioma": idioma_final, 
                    "Conjugaciones": lista_conjugaciones,
                    "Estado": "OK" if res_tradu != "Unknown" else "FALTA"
                })

        df = pd.DataFrame(registros)
        
        # --- LÓGICA DE FILTRADO PARA EXCEL ---
        df_limpio = df[df["Estado"] == "OK"]
        df_pendientes = df[df["Estado"] == "FALTA"]
        
        print("\n--- RESUMEN DE PROCESAMIENTO ---")
        print(f"Total registros analizados: {len(df)}")
        print(f"Registros OK (Guardados en pestañas): {len(df_limpio)}")
        print(f"Registros con FALTA (Excluidos de pestañas): {len(df_pendientes)}")
        
        if not df_pendientes.empty:
            print("\n⚠️ Los siguientes registros tienen estado 'FALTA' y han sido excluidos de los listados finales:")
            print(df_pendientes[['Palabra', 'Categoria']].head(10).to_string(index=False))
            print("... (y otros más)")

        with pd.ExcelWriter("Analisis_Cobertura_Final2.xlsx", engine="openpyxl") as writer:
            # Estadística mantiene el df completo para que veas el panorama real
            resumen = df.groupby(['Categoria', 'Estado']).size().unstack(fill_value=0)
            for col in ['OK', 'FALTA']:
                if col not in resumen: resumen[col] = 0
            resumen['Total'] = resumen['OK'] + resumen['FALTA']
            resumen['% Cobertura'] = (resumen['OK'] / resumen['Total']) * 100
            resumen.to_excel(writer, sheet_name="ESTADISTICAS")

            # Hojas por categorías: Solo los registros OK
            for cat in self.categorias_objetivo.keys():
                df_cat = df_limpio[df_limpio["Categoria"] == cat].sort_values("Palabra")
                if not df_cat.empty:
                    df_cat.to_excel(writer, sheet_name=cat, index=False)

        print("\n✨ Archivo 'Analisis_Cobertura_Final2.xlsx' generado con filtros aplicados.")
        
if __name__ == "__main__":
    evaluador = EvaluadorDiccionarioPro("dataset/scnwiktionary-latest-pages-articles.xml")
    evaluador.extraer_y_evaluar()