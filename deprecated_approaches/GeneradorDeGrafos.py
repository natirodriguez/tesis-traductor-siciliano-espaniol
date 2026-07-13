import networkx as nx
import matplotlib.pyplot as plt

class GeneradorDeGrafos:
    def __init__(self):
        self.G = nx.DiGraph()

    def integrar_registros(self, registros):
        for reg in registros:
            nodo_id = reg['lema']
            # Raíz de Apertium
            self.G.add_node(nodo_id, tipo="raiz", fuente=reg['fuente'], cat=reg['categoria'])
            # Conexión a la categoría (desconocido/vblex)
            self.G.add_edge(nodo_id, reg['categoria'], relacion="clasificado_como")

    def exportar_grafo_por_categoria(self, categoria_objetivo, nombre_archivo):
        if not self.G.has_node(categoria_objetivo):
            print(f"❌ Nodo '{categoria_objetivo}' no encontrado.")
            return

        # 1. Palabras que apuntan a la categoría (arisi, etc.)
        palabras = list(self.G.predecessors(categoria_objetivo))
        
        # 2. CAPTURA TOTAL: Buscamos padres (raíces) e HIJOS (traducciones)
        nodos_relacionados = []
        for p in palabras:
            # Quién origina la palabra (Raíz)
            nodos_relacionados.extend(list(self.G.predecessors(p)))
            # A quién apunta la palabra (Traducción Amarilla) -> CLAVE
            nodos_relacionados.extend(list(self.G.successors(p)))

        # 3. Construir el subgrafo
        nodos_totales = set([categoria_objetivo] + palabras + nodos_relacionados)
        subgrafo = self.G.subgraph(nodos_totales).copy()
        
        # 4. Dibujo
        plt.figure(figsize=(16, 10))
        pos = nx.spring_layout(subgrafo, k=0.7)
        
        color_map = []
        for node in subgrafo.nodes():
            tipo = subgrafo.nodes[node].get('tipo', '')
            if node == categoria_objetivo: color_map.append('orange')
            elif tipo == 'significado': color_map.append('yellow')   # TRADUCCIÓN
            elif tipo == 'palabra': color_map.append('lightgreen')
            else: color_map.append('skyblue')

        nx.draw(subgrafo, pos, with_labels=True, node_color=color_map, 
                node_size=2500, font_size=9, edge_color="gray", arrowsize=20)
        
        plt.title(f"Resultado de Integración: {categoria_objetivo.upper()}")
        plt.savefig(nombre_archivo, bbox_inches='tight', dpi=300)
        plt.close()

    def reporte_zoom_palabra(self, palabra_objetivo, nombre_archivo):
        if not self.G.has_node(palabra_objetivo):
            print(f"❌ No encuentro la palabra '{palabra_objetivo}' en el grafo.")
            return

        # Capturamos raíz (predecessor) y traducción/categoría (successors)
        nodos_relacionados = list(self.G.predecessors(palabra_objetivo)) + \
                             list(self.G.successors(palabra_objetivo)) + \
                             [palabra_objetivo]
        
        # Ampliamos a un nivel más para capturar si la palabra tiene "nietos" (traducciones)
        for vecino in list(self.G.successors(palabra_objetivo)):
            nodos_relacionados.extend(list(self.G.successors(vecino)))

        subgrafo = self.G.subgraph(set(nodos_relacionados)).copy()
        
        plt.figure(figsize=(12, 9))
        pos = nx.spring_layout(subgrafo, k=1.0, seed=42)
        
        color_map = []
        for n in subgrafo.nodes():
            tipo = subgrafo.nodes[n].get('tipo', '')
            # Lógica de colores pedida
            if tipo == 'significado': 
                color_map.append('yellow')         # TRADUCCIÓN AMARILLA
            elif tipo == 'palabra': 
                color_map.append('mediumpurple')   # PALABRAS DEL WIKI VIOLETAS (màrisi, etc)
            elif n in ['verbo', 'sustantivo', 'desconocido']: 
                color_map.append('orange')         # CATEGORÍA NARANJA
            else: 
                color_map.append('skyblue')        # RAÍZ CELESTE

        nx.draw(subgrafo, pos, with_labels=True, node_color=color_map, 
                node_size=3500, font_size=9, edge_color="gray", 
                arrowsize=20, width=1.5)
        
        plt.title(f"Zoom de Integración: {palabra_objetivo.upper()}", fontsize=14)
        plt.savefig(nombre_archivo, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"✅ Zoom generado exitosamente en: {nombre_archivo}")