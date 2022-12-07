from igraph import Graph
import random

'''
This algorithm attempts to solve the maximum leaf spanning tree problem by building a forest of trees that have as many
leaves as possible, then connecting those trees together to form the full spanning tree.

When connecting these components, the algorithm can prefer to pick edges between known *branches* to maintain as many
leaves as possible on the trees being connected. 

Full code is available at https://github.com/jdurrell/Max-leaf-Spanning-Tree

Note: from the igraph library, we use graph.vs.[node_index]["name"] to get the "name" of the vertex instead of using its index
        in the graph. This is because we end up deleting vertices from the working copy of the graph in order to make the 
        computation easier, but this changes the indices of those vertices, so working with names is more consistent.

        We then get the vertex index from the name using graph.vs.find(name). Although it's supposed to be able to use the 
        name property as an index, the names are constructed in the graph parser as strings from the original numbering of
        the vertices, and I don't trust Python developers or Python's typing system to not pull a Javascript on me and just 
        treat the string version of a number as an actual integer value instead of a string.
'''

def solve(graph: Graph):
    graphInProcess: Graph = graph.copy()  # copy graph so that we can delete from it without altering the original input
    spanningTree = Graph()
    spanningTree.add_vertices([str(x) for x in range(graph.vcount())])
    treeSets = [] # list of sets representing each tree in the forest (connected components)


    # build a new tree in the forest while the graph has a node that is reasonable to expand
    # nodes of degree <= 2 are less useful for expansion roots because they often end up as leaves when upon connecting components
    while graphInProcess.maxdegree() >= 3:
        # find a random node with the maximum degree (likely a best one to use as the root for this tree)
        # randomness is used because this algorithm is repeated multiple times to find a potentially better solution
        maxDegree = -1
        maxDegreeNodes = []
        for node in graphInProcess.vs:
            degree = graphInProcess.degree(node)
            if degree == maxDegree:
                maxDegreeNodes.append(node)
            elif degree > maxDegree:
                maxDegree = degree
                maxDegreeNodes = [node]
        maxDegreeNode = random.choice(maxDegreeNodes)

        # build a new tree in the forest
        nodeNames = [graphInProcess.vs[node]["name"] for node in graphInProcess.neighbors(maxDegreeNode)]
        leaves = set(nodeNames)
        nodeNames.append(maxDegreeNode["name"])
        spanningTree.add_edges([(maxDegreeNode["name"], name) for name in nodeNames if name != maxDegreeNode["name"]])
        nodesInTree = set(nodeNames)  # for faster lookup time
        
        # expand the tree while it has an expandable leaf
        expandingNodeTuple = getExpandableNode(graphInProcess, nodesInTree, leaves)
        while expandingNodeTuple is not None:
            leafNodeName: str = expandingNodeTuple[0]
            leaves.remove(leafNodeName)
            nonTreeNeighbors: list[str] = [graphInProcess.vs[x]["name"] for x in graphInProcess.neighbors(graphInProcess.vs.find(leafNodeName)) if graphInProcess.vs[x]["name"] not in nodesInTree]
            
            # if the expansion node has just one new neighbor, then it's the higher-priority expansion type
            # expand the tree to this node, then expand it to all of that neighbor's neighbors (with the neighbor as the parent)
            if len(nonTreeNeighbors) == 1:
                neighborName: str = nonTreeNeighbors[0]
                spanningTree.add_edge(spanningTree.vs.find(leafNodeName), spanningTree.vs.find(neighborName))
                nodesInTree.add(neighborName)
                for extendedNeighbor in graphInProcess.neighbors(graphInProcess.vs.find(neighborName)):
                    extendedNeighborName = graphInProcess.vs[extendedNeighbor]["name"]
                    if extendedNeighborName not in nodesInTree:
                        nodesInTree.add(extendedNeighborName)
                        leaves.add(extendedNeighborName)
                        spanningTree.add_edge(spanningTree.vs.find(neighborName), spanningTree.vs.find(extendedNeighborName))
            
            # if the expansion node has more than two new neighbors, add all of them to the tree as children of this node
            else:
                for neighborName in nonTreeNeighbors:
                    nodesInTree.add(neighborName)
                    leaves.add(neighborName)
                    spanningTree.add_edge(spanningTree.vs.find(leafNodeName), spanningTree.vs.find(neighborName))
            
            expandingNodeTuple = getExpandableNode(graphInProcess, nodesInTree, leaves)
        
        # now remove the constructed tree from the original graph and update the list of connected components (trees)
        graphInProcess.delete_vertices(list(nodesInTree))
        treeSets.append(nodesInTree)

    # now connect the components similarly to Kruskal's Algorithm
    while (spanningTree.ecount() < graph.vcount() - 1) or (len(treeSets) > 1):  # maybe only first clause is necessary?
        # skip building connections on leaf nodes to maintain maximum leafyness unless we do an entire pass without adding an edge
        addedEdge = connectionEdgePass(graph, spanningTree, treeSets, False)
        if not addedEdge:
            # if failed to add an edge the first time, then we are forced to connect on at least one leaf node
            connectionEdgePass(graph, spanningTree, treeSets, True)

    return spanningTree, len([degree for degree in spanningTree.indegree() if degree == 1])


# iterate through all of the edges in the original graph to connect the individual trees (and floating nodes) in the building spanning tree 
def connectionEdgePass(graph: Graph, tree: Graph, treeSets, useLeaves: bool):
    addedEdge = False
    for edge in graph.es:
        source = graph.vs[edge.source]["name"]
        target = graph.vs[edge.target]["name"]
        setIndexSource = findSetIndex(treeSets, source)
        setIndexTarget = findSetIndex(treeSets, target)
        
        # skip connecting on leaves when useLeaves is True (maintain more leaves when we can connect using branches instead)
        if not useLeaves and (tree.degree(graph.vs.find(source)) == 1 or tree.degree(graph.vs.find(target)) == 1):
            continue

        # if endpoints are from different connected components, add the edge to the spanning tree and connect the components
        if setIndexSource is None and setIndexTarget is None:
            tree.add_edge(tree.vs.find(source), tree.vs.find(target))
            addedEdge = True
            treeSets.append(set([source, target]))
        elif setIndexSource != setIndexTarget:
            tree.add_edge(tree.vs.find(source), tree.vs.find(target))
            addedEdge = True
            if setIndexSource is None:
                treeSets[setIndexTarget].add(source)
            elif setIndexTarget is None:
                treeSets[setIndexSource].add(target)
            else:
                treeSets[setIndexSource] = treeSets[setIndexSource].union(treeSets[setIndexTarget])
                treeSets.pop(setIndexTarget)
    
    # return whether a connection was made during this pass
    return addedEdge

# TODO: implement these as trees like in Kruskal's Algorithm for better speed
# find the set in the list where the given item appears
def findSetIndex(setList, item):
    for i in range(len(setList)):
        if item in setList[i]:
            return i
    
    # return None if item does not appear in any set
    return None


# get the next node to expand in the tree according to the priority of the expansion rules
def getExpandableNode(graph: Graph, nodesInTree: set, leaves: set):
    leafPriorityDegree = (None, 999, -1)  # (node to expand, priority of expansion type, degree of node)
    for leaf in leaves:
        nonTreeNeighbors = [graph.vs[x]["name"] for x in graph.neighbors(graph.vs.find(leaf)) if graph.vs[x]["name"] not in nodesInTree]
        
        # in the case where the leaf node has only one new neighbor, it's possible that this neighbor has many more new neighbors
        # this is essentially a one-step lookahead to find a node that might yield more total numbers of leaves
        if len(nonTreeNeighbors) == 1:
            nonTreeNeighborsOfNeighbor = [graph.vs[x]["name"] for x in graph.neighbors(graph.vs.find(nonTreeNeighbors[0])) if graph.vs[x]["name"] not in nodesInTree]
            if len(nonTreeNeighborsOfNeighbor) >= 2 and (1 < leafPriorityDegree[1] or len(nonTreeNeighborsOfNeighbor) > leafPriorityDegree[2]):
                # this expansion type is a higher piority than the other one because it comes from the lookahead
                leafPriorityDegree = (leaf, 1, len(nonTreeNeighborsOfNeighbor))
        
        # case where the leaf node has more then two new neighbors is still useful, but lower priority.
        elif len(nonTreeNeighbors) >= 2:
            # skip this expansion if we've already found an expansion of higher priority
            if leafPriorityDegree[1] < 2:
                continue
            # this expansion type has a lower priority because these nodes would end up being leaves *anyways*,
            # even on the lookahead expansion, so this allows to possibly save some number of leaves by using
            # a node found by the lookahead if one exists
            leafPriorityDegree = (leaf, 2, len(nonTreeNeighbors))
    
    # return None if there are no more expandable leaves on the tree
    if leafPriorityDegree[0] is not None:
        return leafPriorityDegree
    else: 
        return None
