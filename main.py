import os
import igraph
from graphParser import GraphParser
# from SolutionAlgorithms import DegreeOrderBFS
from SolutionAlgorithms import ForestWithExpansionRules

def main():
    inputFilename = 'all-hard.in'
    outputFilename = 'all-hard.out'
    numAttempts = 100

    # generate new output filename if it already exists
    if os.path.isfile(outputFilename):
        i = 1
        while os.path.isfile(f'{outputFilename} ({i})'):
            i = i + 1
        outputFilename = f'{outputFilename} ({i})'

    parser = GraphParser(inputFilename)
    graphNum = 0
    while parser.hasNext():
        graph = parser.readNextGraph()
        try:
            assertValidInputGraph(graph)
        except Exception as e:
            print(f'Error with instance {i}: {str(e)}')
        
        # run algorithm multiple times on each graph and take the best solution found
        # this makes use of some randomness due to set hashing (although diminishing returns are likely heavy)
        solutions = []
        for i in range(numAttempts):
            solutionTree, numLeaves = ForestWithExpansionRules.solve(graph)
            assertValidSolution(graph, solutionTree, numLeaves)
            solutions.append((solutionTree, numLeaves))
        maxSolution = (None, -1)
        for solution in solutions:
            if solution[1] > maxSolution[1]:
                maxSolution = solution
        assert maxSolution is not None

        # write graph out to file and print to console for progress tracking
        print(f'Graph {graphNum}: |V|={graph.vcount()}, |E|={graph.ecount()}, leaves = {numLeaves}')
        writeGraphToFile(maxSolution[0], maxSolution[1], outputFilename)
        graphNum += 1
    parser.close()


def assertValidInputGraph(graph: igraph.Graph):
    assert graph.is_connected()
    assert graph.vcount() <= 100
    assert graph.ecount() <= 2000
    
    # check that the graph doesn't contain duplicate or self edges
    adjacencyList = {}
    for edge in graph.es:
        assert edge.source != edge.target
        if edge.source < edge.target:
            if edge.source not in adjacencyList.keys():
                adjacencyList[edge.source] = set()
            assert edge.target not in adjacencyList[edge.source]
            adjacencyList[edge.source].add(edge.target)
        else:
            if edge.target not in adjacencyList.keys():
                adjacencyList[edge.target] = set()
            assert edge.source not in adjacencyList[edge.target]
            adjacencyList[edge.target].add(edge.source)


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

    file.close()

    file2 = open(filename + '_summary.txt', 'a')
    file2.write(f'leaves: {numLeaves}\n')
    file2.close()


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