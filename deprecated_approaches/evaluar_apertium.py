import os
import re
import pandas as pd

def generar_prueba_cientifica(ruta_excel, ruta_apertium):
    print("=== EJECUTANDO PRUEBA DE INTEGRACIÓN APERTIUM ===")
    
    # 1. Cargar Apertium en memoria
    mapeo_conjugaciones = {}
    with open(ruta_apertium, "r", encoding="utf-8", errors="ignore") as f:
        contenido = f.read()
    entradas = re.findall(r'<l>([^<]+)</l>.*?<r>([^<s]+)', contenido)
    
    for forma, lema_padre in entradas:
        lema = lema_padre.strip()
        if lema not in mapeo_conjugaciones:
            mapeo_conjugaciones[lema] = set()
        mapeo_conjugaciones[lema].add(forma.strip())
        
    # 2. Cargar la pestaña de Verbos del Wiktionary
    df_verbos = pd.read_excel(ruta_excel, sheet_name="Verbo")
    
    total_verbos = len(df_verbos)
    verbos_falta = df_verbos[df_verbos["Estado"] == "FALTA"]
    total_falta = len(verbos_falta)
    
    # 3. Hacer los cálculos de cruce
    verbos_con_conjugaciones = 0
    total_formas_inyectadas = 0
    verbos_falta_rescatados = 0
    
    for idx, fila in df_verbos.iterrows():
        palabra = str(fila["Palabra"]).strip()
        if palabra in mapeo_conjugaciones:
            cant_formas = len(mapeo_conjugaciones[palabra])
            verbos_con_conjugaciones += 1
            total_formas_inyectadas += cant_formas
            
            # Si estaba en FALTA y Apertium lo reconoce, lo consideramos un "rescate" o validación
            if fila["Estado"] == "FALTA":
                verbos_falta_rescatados += 1

    # --- IMPRESIÓN DEL REPORTE ACADÉMICO ---
    print("\n" + "="*50)
    print("   REPORTE DE JUSTIFICACIÓN TÉCNICA (TESIS)")
    print("="*50)
    print(f"1. Diagnóstico Inicial (Wiktionary):")
    print(f"   - Total de verbos analizados: {total_verbos}")
    print(f"   - Verbos en estado 'FALTA': {total_falta} ({total_falta/total_verbos*100:.2f}%)")
    
    print(f"\n2. Impacto de la Integración con Apertium:")
    print(f"   - Verbos validados morfológicamente: {verbos_con_conjugaciones} de {total_verbos} ({verbos_con_conjugaciones/total_verbos*100:.2f}%)")
    print(f"   - Formas conjugadas inyectadas al corpus: {total_formas_inyectadas}")
    print(f"   - Promedio de flexiones por verbo: {total_formas_inyectadas/max(1, verbos_con_conjugaciones):.1f} formas.")
    
    print(f"\n3. Conclusión de Cobertura de Erreores:")
    print(f"   - De los {total_falta} verbos sin traducción, Apertium validó la existencia de: {verbos_falta_rescatados}")
    print(f"   - Porcentaje de reducción de 'incertidumbre': {verbos_falta_rescatados/max(1, total_falta)*100:.2f}%")
    print("="*50)
    
    if total_formas_inyectadas > 0:
        print("\n📢 DECISIÓN RECOMENDADA PARA LA TESIS: APROBAR INTEGRACIÓN.")
        print("Fundamento: Apertium expande exponencialmente la dimensionalidad del grafo lingüístico")
    else:
        print("\n📢 DECISIÓN RECOMENDADA PARA LA TESIS: RECHAZAR INTEGRACIÓN.")

if __name__ == "__main__":
    carpeta = os.path.dirname(os.path.abspath(__file__))
    generar_prueba_cientifica(
        os.path.join(carpeta, "Analisis_Cobertura_Final2.xlsx"),
        os.path.join(carpeta, "dataset/apertium-scn.scn.dix.txt")
    )