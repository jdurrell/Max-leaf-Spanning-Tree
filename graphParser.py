import igraph

class GraphParser:

    def __init__(self, filename):
        self.file = open(filename, 'r')
        self.numRemainingGraphs = int(self.file.readline())
        self.graphNum = 0
        self.line = 2

    
    def readNextGraph(self) -> igraph.Graph:
        if self.numRemainingGraphs <= 0:
            raise Exception("No remaining graphs to read.")
        print(f'Graph {self.graphNum}: line {self.line}')

        self.numRemainingGraphs -= 1

        headerFields = self.file.readline().split()
        self.line += 1
        numVertices = int(headerFields[0])
        numEdges = int(headerFields[1])

        graph = igraph.Graph()
        graph.add_vertices([str(x) for x in range(numVertices)]) # need to name the vertices
        while numEdges > 0: 
            edgeFields = self.file.readline().split()
            self.line += 1
            graph.add_edge(int(edgeFields[0]), int(edgeFields[1]))
            numEdges = numEdges - 1

        self.graphNum += 1
        return graph


    def hasNext(self) -> bool:
        return self.numRemainingGraphs > 0


    def close(self):
        self.file.close()
