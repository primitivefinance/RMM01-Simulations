from getData import get_data
from buildGraph import build_graph
from visualize import visualize


def main():
    users = get_data("")
    graph = build_graph(users.head())
    visualize(graph)


if __name__ == "__main__":
    main()
