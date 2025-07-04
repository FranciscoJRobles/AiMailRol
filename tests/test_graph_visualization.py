import logging
from ia.langgraph.graphs.processing_graph import processing_graph

def test_graph_visualization():
    """Test para visualizar el grafo de procesamiento."""
    try:
        visualization = processing_graph.get_graph_visualization()
        print(visualization)
    except Exception as e:
        logging.error(f"Error al generar la visualización del grafo: {e}")

if __name__ == "__main__":
    test_graph_visualization()
