import networkx as nx
from pyvis.network import Network

from utility.string_utility import shorten_long_string


def create_network_from_nx(graph: nx.Graph) -> Network:
    net = Network(height="90%", width="100%", directed=graph.is_directed(), notebook=True)
    for node in graph.nodes:
        net.add_node(node, shape="circle")
    for source, target, data in graph.edges(data=True):
        converted_data = {k: shorten_long_string(str(v)) for k, v in data.items()}
        net.add_edge(source, target, **converted_data)

    # Note: Active below line if you want to check modifying physic attributes
    # net.show_buttons()
    net.set_options("""
    var options = {
      "edges": {
        "color": {
          "inherit": true
        },
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 0.5
          }
        },
        "smooth": {
          "type": "continuous",
          "forceDirection": "none"
        }
      },
      "physics": {
        "minVelocity": 0.75
      }
    }
    """)
    return net


def copy_from_nx(graph: nx.DiGraph):
    """
    Create a copy from graph without keeping attributes
    :param graph: graph
    :return: copy of given graph
    """
    new_graph = nx.DiGraph()
    new_graph.add_nodes_from(graph)
    new_graph.add_edges_from(graph.edges(data=False))
    return new_graph
