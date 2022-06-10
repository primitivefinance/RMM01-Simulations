from getData import get_data
from buildGraph import build_graph
from visualize import visualize


def main():
    users = get_data("KKRW7D1SQKAG2KNEBZA4XNR68H9MWYNMIB")
    graph = build_graph(users.head())
    visualize(graph)


if __name__ == "__main__":
    main()
