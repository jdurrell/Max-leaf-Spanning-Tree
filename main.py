import os
import igraph
from graphParser import GraphParser
# from SolutionAlgorithms import DegreeOrderBFS
from SolutionAlgorithms import ForestWithExpansionRules

def main():
    inputFilename = 'hard.in'
    outputFilename = 'hardtest.out'

    # generate new output filename if it already exists
    if os.path.isfile(outputFilename):
        i = 1
        while os.path.isfile(f'{outputFilename} ({i})'):
            i = i + 1
        outputFilename = f'{outputFilename} ({i})'

    parser = GraphParser(inputFilename)
    while parser.hasNext():
        graph = parser.readNextGraph()
        assert graph.is_connected()  # ensure that the graph has a valid spanning tree
        solutionTree, numLeaves = ForestWithExpansionRules.solve(graph)
        assertValidSolution(graph, solutionTree, numLeaves)
        writeGraphToFile(solutionTree, numLeaves, outputFilename)
    parser.close()


def assertValidSolution(originalGraph: igraph.Graph, solutionTree: igraph.Graph, numLeaves):
    assert solutionTree.is_connected()
    
    # assert correct number of edges to be a tree
    assert solutionTree.ecount() == solutionTree.vcount() - 1

    # assert that all vertices are included and no other ones are added
    vertexSet = set()
    for edge in solutionTree.to_tuple_list():
        vertexSet.add(edge[0])
        vertexSet.add(edge[1])
    numberSet = set(range(originalGraph.vcount()))
    verticesNotIncluded = numberSet.difference(vertexSet)
    assert len(verticesNotIncluded) == 0, f'Solution did not contain vertices {verticesNotIncluded}'
    extraVertices = vertexSet.difference(numberSet)
    assert len(extraVertices) == 0, f'Solution was not supposed to contain vertices {extraVertices}'

    # assert number of leaves is correct
    realLeaves = len([indegree for indegree in solutionTree.indegree() if indegree == 1])
    assert numLeaves == realLeaves, f'Solution was supposed to contain {numLeaves} leaves, but instead contained {realLeaves} leaves'


def writeGraphToFile(graph: igraph.Graph, numLeaves, filename: str):
    file = open(filename, 'a')
    file.write(f'{numLeaves} {graph.ecount()}\n')

    edgeList = lexigraphicalEdgeOrder(graph)
    for edge in edgeList:
        file.write(f'{edge[0]} {edge[1]}\n')
    # adjacency_list = graph.to_list_dict()
    # for key in sorted(adjacency_list.keys()):
    #     for neighbor in sorted(adjacency_list[key]):
    #         file.write(f'{key} {neighbor}\n')

    file.close()


def lexigraphicalEdgeOrder(graph: igraph.Graph):
    adjacency_list = {}
    for edge in graph.es:
        source = int(graph.vs[edge.source]["name"])
        target = int(graph.vs[edge.target]["name"])
        if source < target:
            a = source
            b = target
        else:
            b = source
            a = target
        if a not in adjacency_list.keys():
            adjacency_list[a] = []
        adjacency_list[a].append(b)
    
    edges = []
    for node in sorted(adjacency_list.keys()):
        for neighbor in sorted(adjacency_list[node]):
            edges.append((node, neighbor))
    return edges     


if __name__ == '__main__':
    main()