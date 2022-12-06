from igraph import *
import random

def main():
    
    # generate a random connected bipartite graph using the igraph library
    bipartiteGraph = Graph.Random_Bipartite(40, 60, p=0.3)
    while not bipartiteGraph.is_connected():
        bipartiteGraph = Graph.Random_Bipartite(40, 60, p=0.3)
    outputGraphToFile(bipartiteGraph, 'hard.in')
    
    # generate more graphs that have at least some proportion of the vertices as leaves
    # graphPercentages = [0.35, 0.5, 0.6, 0.65, 0.7]
    # graphFactors = [(7, 4), (5, 6), (5, 7), (4, 5), (3, 7)]
    generatorParams = [(30, 400), (50, 25), (40, 0), (60, 0), (70, 0)]
    MAX_VERTICES = 100
    for paramSet in generatorParams:
        graph = generateGraph(MAX_VERTICES, paramSet[0], paramSet[1])
        # graph = generateGraph(factorSet[0], factorSet[1])
        assertValidGraph(graph)
        outputGraphToFile(graph, 'hard.in')


def generateGraph(numVertices, numLeaves, numObfuscations) -> Graph:
    graph = Graph()
    graph.add_vertices(n=numVertices)

    nodes = [node for node in graph.vs]
    random.shuffle(nodes)
    leaves = []
    branches = []
    for i in range(numVertices):
        if i < numLeaves:
            leaves.append(nodes[i])
        else:
            branches.append(nodes[i])

    # for each leaf, pick a random branch to be its parent    
    leafParentDict = {}
    for leaf in leaves:
        parent = branches[random.randrange(len(branches))]
        leafParentDict[leaf] = parent
        graph.add_edge(leaf, parent)

    # now connect the branches to get a valid spanning tree
    components = [set([x.index]) for x in branches]
    while len(components) > 1:
        branch1 = branches[random.randrange(len(branches))].index
        branch2 = branches[random.randrange(len(branches))].index
        branch1Index = getSetIndex(components, branch1)
        branch2Index = getSetIndex(components, branch2) 
        if branch1Index != branch2Index:
            graph.add_edge(branch1, branch2)
            components[branch1Index] = components[branch1Index].union(components[branch2Index])
            components.pop(branch2Index)

    assert graph.is_connected()

    # now obscure the leaves by adding some additional edges between them
    leaves = [node for node in graph.vs if graph.degree(node) == 1]
    
    # construct a dictionary to limit the degree of each leaf to that of its parent
    # this helps ensure that the graph won't be so connected so as to yield more easily findable spanning trees
    degreeRemaining = {}
    for leaf in leaves:
        parent = graph.neighbors(leaf)[0]
        degreeRemaining[leaf] = len(graph.neighbors(parent)) - 1

    leafEdges = set()
    for leaf1 in leaves:
        for leaf2 in leaves:
            leafEdges.add((leaf1, leaf2))
    leafEdges = list(leafEdges)
    random.shuffle(leafEdges)  # randomize order to help protect against possible ordering bias

    # now add those leaf edges to the graphs
    while graph.ecount() < 2000 and len(leafEdges) > 0:
        edge = leafEdges.pop()
        if (edge[0] != edge[1]) and (not graph.are_connected(edge[0], edge[1])) and degreeRemaining[edge[0]] > 0 and degreeRemaining[edge[1]] > 0:
            graph.add_edge(edge[0], edge[1])
            degreeRemaining[edge[0]] -= 1
            degreeRemaining[edge[1]] -= 1

    # now add additional edges to do more obscuring, but can prefer between branches this time
    branchChange = 0.8
    for i in range(numObfuscations):
        if graph.ecount() >= 2000:
            break

        v1 = random.choice(branches) if random.uniform(0, 1) < branchChange else random.choice(leaves)
        v2 = random.choice(branches) if random.uniform(0, 1) < branchChange else random.choice(leaves)
        if v1.index != v2.index and not graph.are_connected(v1, v2):
            graph.add_edge(v1, v2)
        
    return graph


def getSetIndex(listOfSets, element):
    for i, thing in enumerate(listOfSets):
        if element in thing:
            return i
    return None


def outputGraphToFile(graph: Graph, filename: str):
    file = open(filename, 'a')
    file.write(f'{graph.vcount()} {graph.ecount()}\n')

    adjacency_list = graph.to_list_dict()
    for key in sorted(adjacency_list.keys()):
        for neighbor in sorted(adjacency_list[key]):
            file.write(f'{key} {neighbor}\n')

    file.close()


def assertValidGraph(graph: Graph):
    assert graph.is_connected()
    assert graph.vcount() <= 100
    assert graph.ecount() <= 2000


if __name__ == "__main__":
    main()