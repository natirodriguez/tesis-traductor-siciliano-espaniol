import pandas as pd

def detectar_errores_gramaticales(archivo_excel):
    df = pd.read_excel(archivo_excel, sheet_name="Verbo") # Cambia a "Adjetivo" luego
    
    # Ejemplo: En siciliano, muchos verbos terminan en -ari, -iri, -iri
    # Si una palabra NO termina en eso y está en la lista de verbos, es sospechosa.
    terminaciones_verbo = ('ari', 'iri', 'iri')
    
    # Creamos una columna nueva para marcar las sospechosas
    df['sospechoso'] = ~df['Palabra'].astype(str).str.endswith(terminaciones_verbo)
    
    # Exportamos solo las que NO cumplen la regla para que las revises rápido
    sospechosas = df[df['sospechoso'] == True]
    sospechosas.to_excel("Verbos_A_Revisar.xlsx", index=False)
    print(f"✅ Se han detectado {len(sospechosas)} palabras sospechosas. Revisa 'Verbos_A_Revisar.xlsx'")

# Corre esto para tus verbos
detectar_errores_gramaticales("Analisis_Cobertura_Final2.xlsx")

# Cargar tus sospechosas
df_sospechosas = pd.read_excel("Verbos_A_Revisar.xlsx")

# Extraer los primeros 2 caracteres de cada palabra
df_sospechosas['prefijo'] = df_sospechosas['Palabra'].str[:2]

# Contar cuáles son los prefijos que más se repiten en los errores
conteo = df_sospechosas['prefijo'].value_counts()
print(conteo)