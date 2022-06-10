import networkx as nx


def build_graph(data):
    G = nx.Graph()
    G.add_node(0, UTM="0x54522da62a15225c95b01bd61ff58b866c50471f")
    idx = 1
    for user in data:
        print(user)
        G.add_node(idx, UTM=user)
        G.add_edge(0, idx)
        idx += 1
    return G
