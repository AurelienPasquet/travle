import sys
import os
import platform
from pydot import graph_from_dot_file
import random

DATASET = 'countries.csv'

GRAPHS_PATH = "graphs/"
if not os.path.exists(GRAPHS_PATH):
    os.mkdir(GRAPHS_PATH)

def parse(file_name):
    """
    Parses a file containing values separated by commas.

    Parameters:
        file_name (str): The path to the file to be parsed.

    Returns:
        dict: A dictionary containing the parsed key-value pairs, where the keys are the first elements
              in each line and the values are the remaining elements in each line.
    """

    with open(file_name, 'r') as f:
        lines = f.readlines()
        lines = [line.strip().split(',') for line in lines]
    return {line[0]: line[1:] for line in lines}


def bfs(graph, source, target):
    """
    Perform a breadth-first search on a graph to find the shortest path from a source node to a target node.

    Parameters:
        graph (dict): The graph represented as a dictionary where the keys are nodes and the values are lists of neighboring nodes.
        source: The source node from which to start the search.
        target: The target node to find the shortest path to.

    Returns:
        tuple: A tuple containing the shortest path as a list of nodes and the length of the path as an integer. If no path is found, the path will be None and the length will be -1.
    """

    if source == target:
        return [], 0

    visited = set()
    queue = [source]
    current = source

    parent_map = {source: None}

    while current != target:

        current = queue.pop(0)

        visited.add(current)

        unvisitedNeighbors = [
            neighbor for neighbor in graph[current] if neighbor not in visited]

        for neighbor in unvisitedNeighbors:
            if neighbor not in queue:
                queue.append(neighbor)
            if neighbor in parent_map:
                parent_map[neighbor].append(current)
            else:
                parent_map[neighbor] = [current]

    path = []
    while current != source:
        path.append(current)
        current = parent_map[current][0]
    minimum = len(path)

    paths = get_paths(source, target, parent_map, minimum)
    return paths if paths else [], minimum


def get_paths(source, target, parent_map, minimum):
    """
    Retrieve all paths from the given node using the provided path dictionary.

    Parameters:
        node: The starting node.
        path_dict: A dictionary containing the paths.

    Returns:
        A list of all paths from the given node.
    """

    paths = []
    get_paths_aux(paths, [], source, target, parent_map, minimum)
    paths.sort()
    return paths


def get_paths_aux(paths, path, source, node, parent_map, minimum):
    """
    Recursively finds all paths from a given node to its parent nodes in a path dictionary.

    Parameters:
        paths (list): A list to store the found paths.
        path (list): The current path being constructed.
        node: The current node being processed.
        path_dict (dict): A dictionary that maps each node to its parent nodes.

    Returns:
        None
    """

    if len(path) > minimum:
        return

    if parent_map[node] == None:
        path.reverse()
        paths.append(path)
        return

    new_path = path.copy()
    new_path.append(node)
    for parent in parent_map[node]:
        get_paths_aux(paths, new_path, source, parent, parent_map, minimum)


def check_adjacency(graph):
    """
    Check the adjacency of nodes in a graph.

    Parameters:
        graph (dict): A dictionary representing the graph, where the keys are nodes and the values are lists of neighbors.

    Returns:
        True if an error occured, False otherwise.
    """

    for node, neighbors in graph.items():
        for neighbor in neighbors:
            if neighbor not in graph:
                print(f"{neighbor} is not a key but exists as value.")
                return True
            if node not in graph[neighbor]:
                print(f"{node} has {neighbor} as neighbor but {neighbor} does not have {node} as neighbor.")
                return True
    return False


def check_connectedness(graph):
    """
    Check if a graph is connected.

    Parameters:
        graph (dict): A dictionary representing the graph, where the keys are the nodes and the values are lists of neighbors.

    Returns:
        True if an error occured, False otherwise.
    """

    visited = []
    queue = [next(iter(graph))]

    while queue:

        current = queue.pop(0)
        visited.append(current)

        unvisitedNeighbors = [
            neighbor for neighbor in graph[current] if neighbor not in visited]

        for neighbor in unvisitedNeighbors:
            if neighbor not in queue:
                queue.append(neighbor)

    disconnected = [node for node in graph if node not in visited]

    if len(visited) < len(graph):
        print(f"Graph is not connected, isolated nodes: {disconnected}.")
        return True
    return False


def check_entries(graph, source, target):
    """
    Check if the source and target inputs are valid entries in the graph.

    Parameters:
        graph (dict): A dictionary representing the graph.
        source (str): The source input to be checked.
        target (str): The target input to be checked.

    Returns:
        True if an error occured, False otherwise.
    """

    if source not in graph:
        print(f"{source} is not a valid source input.")
        return True
    if target not in graph:
        print(f"{target} is not a valid target input.")
        return True
    return False


def check_graph(graph, source, target):
    error = check_entries(graph, source, target) or \
        check_adjacency(graph) or \
        check_connectedness(graph)
    if error:
        usage()


def print_path(source, path):
    """
    Prints the path from the source node to the destination node.

    Parameters:
        source (str): The source node.
        path (list): The list of nodes representing the path.

    Returns:
        None
    """

    print(source, end='')
    for node in path:
        print(f" -> {node}", end='')
    print()


def print_paths(source, target, paths):
    print(f"\n{source} to {target}: {len(paths)} path{'s' if len(paths) != 1 else ''} of length {len(paths[0])}")
    for path in paths:
        print_path(source, path + [target])


def to_subgraph(source, paths, num_paths=None, underscores=False):
    """
    Convert a list of paths into a subgraph representation.

    Parameters:
        source (str): The source node.
        paths (list): A list of paths, where each path is a list of nodes.
        underscores (bool, optional): Whether to replace spaces with underscores in node names. Defaults to False.

    Returns:
        dict: A dictionary representing the subgraph, where the keys are nodes and the values are lists of adjacent nodes.
    """

    subgraph = {}

    if not num_paths:
        num_paths = len(paths)

    for path in paths[:min(len(paths), num_paths)]:
        if not path:
            continue

        source = source.replace(' ', '_') if underscores else source
        path_0 = path[0].replace(' ', '_') if underscores else path[0]

        if source not in subgraph:
            subgraph[source] = [path_0]
        else:
            if path_0 not in subgraph[source]:
                subgraph[source].append(path_0)

        for i in range(len(path)-1):

            path_i = path[i].replace(' ', '_') if underscores else path[i]
            path_ii = path[i+1].replace(' ', '_') if underscores else path[i+1]

            if path_i not in subgraph:
                subgraph[path_i] = [path_ii]
            else:
                if path_ii not in subgraph[path_i]:
                    subgraph[path_i].append(path_ii)

    if not paths:
        source = source.replace(' ', '_') if underscores else source
        subgraph[source] = []
    else:
        target = paths[0][-1].replace(' ',
                                      '_') if underscores else paths[0][-1]
        subgraph[target] = []

    return subgraph


def to_dot(source, paths, num_paths=None, png=True, svg=True):
    """
    Generate a graph in DOT format based on the given source and paths.

    Parameters:
        source (str): The source country.
        paths (list): A list of paths, where each path is a list of countries.
        png (bool, optional): Whether to generate a PNG image of the graph.
        svg (bool, optional): Whether to generate an SVG image of the graph.
    """

    subgraph = to_subgraph(source, paths, num_paths, underscores=True)

    with open(GRAPHS_PATH + "graph.dot", 'w') as f:

        # Open Graph
        f.write("digraph G {\n")
        f.write("\trankdir=LR;\n")
        f.write("\n")

        # Write countries
        for country in subgraph:
            f.write(f"\t{country};\n")

        # Write edges
        if subgraph:
            f.write("\n")
            for country in subgraph:
                for neighbor in subgraph[country]:
                    f.write(f"\t{country} -> {neighbor};\n")

        # Write labels
        no_labels = True
        for country in subgraph:
            if '_' in country:
                if no_labels:
                    f.write("\n")
                    no_labels = False
                fCountry = country.replace('_', '\\n')
                f.write(f"\t{country} [label=\"{fCountry}\"];\n")
        f.write("}")

    if png:
        (graph,) = graph_from_dot_file(GRAPHS_PATH + "graph.dot")
        graph.write_png(GRAPHS_PATH + "graph.png")
    if svg:
        (graph,) = graph_from_dot_file(GRAPHS_PATH + "graph.dot")
        graph.write_svg(GRAPHS_PATH + "graph.svg")


def search():

    # check params
    if len(sys.argv) not in (4, 5):
        print("Invalid number of parameters.")
        usage()

    countries = parse(DATASET)
    source = sys.argv[2].replace('_', ' ')
    target = sys.argv[3].replace('_', ' ')

    check_graph(countries, source, target)

    paths, length = bfs(countries, source, target)

    nb_paths = len(paths)
    if len(sys.argv) == 5:
        try:
            nb_paths = min(int(sys.argv[4]), nb_paths)
        except:
            print("Paths number must be an integer.")
            usage()

    print(f"\n{source} to {target}: {len(paths)} path{'s' if len(paths) != 1 else ''} of length {length}")
    for i in range(nb_paths):
        print_path(source, paths[i])

    to_dot(source, paths, nb_paths, png=True, svg=True)
    display_command = "display" if platform.system() == "Linux" else \
                      "start" if platform.system() == "Windows" else \
                      "open"  # MacOS
    os.system(f"{display_command} {GRAPHS_PATH}graph.svg")


def get_remaining_paths(paths, guesses):
    remaining_paths = []
    for path in paths:
        path_set = set(path)
        if guesses.issubset(path_set):
            remaining_paths.append(path)
    return remaining_paths


def print_incomplete_path(path, guesses):
    gap = False

    for i in range(0, len(path)):
        if path[i] in guesses:
            if gap:
                print(" -> ", end='')
            print(f"{path[i]}", end='')
            gap = False

        else:
            if gap:
                continue
            print("...", end='')
            gap = True

        if not gap and i < len(path) - 1:
            print(" -> ", end='')
    print()


def game():
    max_mistakes = 3
    nb_mistakes = 0

    countries = parse(DATASET)

    source = random.choice(list(countries.keys()))
    target = source
    while target == source or target in countries[source]:
        target = random.choice(list(countries.keys()))

    check_graph(countries, source, target)

    paths, _ = bfs(countries, source, target)
    remaining_paths = paths.copy()

    for path in paths:
        path.pop(-1)

    guesses = set()

    print(f"Find the shortest path from {source} to {target}")

    while nb_mistakes < max_mistakes:
        guess = input("Enter country name: ")
        guesses.add(guess)

        # Target reached
        for path in paths:
            if len(path) == len(guesses):
                if set(path) == guesses:
                    print_path(source, path + [target])
                    print(f"{target} reached with {nb_mistakes} mistake{'s' if nb_mistakes != 1 else ''}")
                    return

        if guess == source:
            print(f"{guess} is the source target")

        if guess == target:
            print(f"{guess} is the target country")

        # Right guess
        subset_flag = False
        for path in paths:
            if guesses.issubset(path):
                subset_flag = True
                remaining_paths = get_remaining_paths(remaining_paths, guesses)
                print_incomplete_path(remaining_paths[0], guesses)
                break

        # Wrong guess
        if not subset_flag:
            nb_mistakes += 1
            print(f"{guess.replace('_', ' ')} is not on one of the optimal paths")
            print(f"{nb_mistakes}/{max_mistakes} mistakes")
            guesses.remove(guess)

            if nb_mistakes == max_mistakes:
                print("Game over!")
                print_paths(source, target, remaining_paths)
                to_dot(source, [path + [target] for path in paths])

                display_command = "display" if platform.system() == "Linux" else \
                                  "start" if platform.system() == "Windows" else \
                                  "open"  # MacOS
                os.system(f"{display_command} {GRAPHS_PATH}graph.svg")


def usage():
    print("Usage:")
    print(f"python {sys.argv[0]} search <source> <target> [paths number]")
    print("-------------------------- OR --------------------------")
    print(f"python {sys.argv[0]} game")
    exit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
    game_mode = sys.argv[1]
    if game_mode == "game":
        if len(sys.argv) != 2:
            usage()
        game()
    elif game_mode == "search":
        search()
    else:
        usage()
