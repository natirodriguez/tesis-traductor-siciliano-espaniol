import csv
import os

def limpiar_archivo(input_file, output_file):
    # Verificamos si el archivo existe antes de intentar abrirlo
    if not os.path.exists(input_file):
        print(f"ERROR: No se pudo encontrar el archivo en: {os.path.abspath(input_file)}")
        return

    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        
        with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            
            for row in reader:
                if not row or len(row) < 3: continue 
                
                palabra = row[0]
                traduccion = row[2].lower()
                
                categoria = "Sustantivo"
                if any(x in traduccion for x in ["porque", "para", "cuando", "donde"]):
                    categoria = "Conjunción/Adverbio"
                elif any(x in traduccion for x in ["rojo", "bueno", "malo"]):
                    categoria = "Adjetivo"
                elif any(x in traduccion for x in ["es", "hacer", "ir"]):
                    categoria = "Verbo"
                
                writer.writerow([palabra, categoria, row[2], row[3], row[4], row[5]])

    print(f"Archivo generado con éxito: {output_file}")

# Ejemplo de ruta absoluta para que nunca falle:
input_path = r'C:\Users\natys\Desktop\Tesis\sicesp\corpus_csv\Pronombre_Neo4j.csv'
output_path = r'C:\Users\natys\Desktop\Tesis\sicesp\corpus_csv\datos_procesados_final.csv'

limpiar_archivo(input_path, output_path)