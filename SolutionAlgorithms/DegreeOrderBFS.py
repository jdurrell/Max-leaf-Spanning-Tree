from igraph import Graph
from queue import PriorityQueue

# easily tricked by hard instances, so maybe don't go with this
def solve(graph: Graph):
    indegreeList = graph.indegree()
    maxIndegree = max(indegreeList)
    maxIndegreeNode = indegreeList.index(maxIndegree)  # vertices are numbered 0 to n-1, so this is valid

    spanningTree = Graph()
    spanningTree.add_vertices(range(graph.vcount()))
    searchQueue = PriorityQueue()
    searchQueue.put((-1 * maxIndegree, (-1, maxIndegreeNode))) # PriorityQueue uses min-heap, so we must flip the sign of the priority
    discoveredNodes = set([maxIndegreeNode])
    while not searchQueue.empty():
        currentEdge = searchQueue.get()[1]
        if currentEdge[0] != -1:  # don't add an edge for the first vertex because its a start vertex with no edge
            spanningTree.add_edge(currentEdge[0], currentEdge[1])
        for neighbor in graph.neighbors(currentEdge[1]):
            if neighbor not in discoveredNodes:
                searchQueue.put((-1 * indegreeList[currentEdge[1]], (currentEdge[1], neighbor)))
                discoveredNodes.add(neighbor)

    return spanningTree, len([indegree for indegree in spanningTree.indegree() if indegree == 1])
