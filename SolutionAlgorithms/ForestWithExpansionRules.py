from igraph import Graph

def solve(graph: Graph):
    graphInProcess: Graph = graph.copy()  # copy graph so that we can delete from it without altering the original input
    spanningTree = Graph()
    spanningTree.add_vertices([str(x) for x in range(graph.vcount())])
    treeSets = [] # list of sets representing each tree in the forest
    while graphInProcess.maxdegree() >= 3:
        # iterate through each node and find the one with the maximum degree
        maxDegree = -1
        maxDegreeNode = -1
        for node in graphInProcess.vs:
            degree = graphInProcess.degree(node)
            if degree > maxDegree:
                maxDegree = degree
                maxDegreeNode = node

        # build a new tree in the forest
        nodeNames = [graphInProcess.vs[node]["name"] for node in graphInProcess.neighbors(maxDegreeNode)]
        leaves = set(nodeNames)
        nodeNames.append(maxDegreeNode["name"])
        spanningTree.add_edges([(maxDegreeNode["name"], name) for name in nodeNames if name != maxDegreeNode["name"]])
        nodesInTree = set(nodeNames)  # for faster lookup time
        
        # expand the tree while it has an expandable leaf
        expandingNodeTuple = getExpandableNode(graphInProcess, nodesInTree, leaves)
        while expandingNodeTuple is not None:
            leafNode = expandingNodeTuple[0]
            leaves.remove(leafNode["name"])
            nonTreeNeighbors = [x for x in graph.neighbors(leafNode) if x not in nodesInTree]
            if len(nonTreeNeighbors == 1):
                neighbor = nonTreeNeighbors[0]
                spanningTree.add_edge(leafNode["name"], neighbor["name"])
                nodesInTree.add(neighbor["name"])
                for extendedNeighbor in graphInProcess.neighbors(neighbor["name"]):
                    if extendedNeighbor["name"] not in nodesInTree:
                        nodesInTree.add(extendedNeighbor["name"])
                        leaves.add(extendedNeighbor["name"])
                        spanningTree.add_edge(neighbor["name"], extendedNeighbor["name"])
            else:
                for neighbor in nonTreeNeighbors:
                    nodesInTree.add(neighbor["name"])
                    leaves.add(neighbor["name"])
                    spanningTree.add_edge(leafNode["name"], neighbor["name"])
            
            expandingNodeTuple = getExpandableNode(graphInProcess, nodesInTree, leaves)
        
        # now remove the constructed tree from the original graph and update the list of connected components
        graphInProcess.delete_vertices(list(nodesInTree))
        treeSets.append(nodesInTree)

    # now connect the components
    while (spanningTree.ecount() < graph.vcount() - 1) or (len(treeSets) > 1):  # maybe only first clause is necessary 
        for edge in graph.es:
            source = graph.vs[edge.source]["name"]
            target = graph.vs[edge.target]["name"]
            setIndexSource = findSetIndex(treeSets, source)
            setIndexTarget = findSetIndex(treeSets, target)

            # if endpoints are from different connected components, add the edge to the spanning tree and connect the components
            if setIndexSource is None and setIndexTarget is None:
                spanningTree.add_edge(source, target)
                treeSets.append(set([source, target]))
            elif setIndexSource != setIndexTarget:
                spanningTree.add_edge(source, target)
                if setIndexSource is None:
                    treeSets[setIndexTarget].add(source)
                elif setIndexTarget is None:
                    treeSets[setIndexSource].add(target)
                else:
                    treeSets[setIndexSource] = treeSets[setIndexSource].union(treeSets.pop(setIndexTarget))

    return spanningTree, len([degree for degree in spanningTree.indegree() if degree == 1])


def findSetIndex(setList: set, item):
    for i in range(len(setList)):
        if item in setList[i]:
            return i
    return None


def getExpandableNode(graph: Graph, nodesInTree: set, leaves: set):
    leafPriorityDegree = (None, 999, -1)  # (leaf vertex, priority of rule, degree of vertex)
    for leaf in leaves:
        nonTreeNeighbors = [graph.vs[x]["name"] for x in graph.neighbors(leaf) if graph.vs[x]["name"] not in nodesInTree]
        if len(nonTreeNeighbors) == 1:
            nonTreeNeighborsOfNeighbor = [graph.vs[x]["name"] for x in graph.neighbors(nonTreeNeighbors[0]) if graph.vs[x]["name"] not in nodesInTree]
            if len(nonTreeNeighborsOfNeighbor) >= 2 and len(nonTreeNeighborsOfNeighbor) > leafPriorityDegree[2]:
                leafPriorityDegree = (leaf, 1, len(nonTreeNeighborsOfNeighbor))
        elif len(nonTreeNeighbors) >= 2:
            # skip this expansion if we've already found an expansion of higher priority
            if leafPriorityDegree[1] < 2:
                continue
            leafPriorityDegree = (leaf, 2, len(nonTreeNeighbors))
    
    if leafPriorityDegree[0] is not None:
        return leafPriorityDegree
    else: 
        return None
