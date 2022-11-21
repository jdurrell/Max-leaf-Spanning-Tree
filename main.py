import os
from graphParser import GraphParser

def main():
    inputFilename = 'hard.in'
    outputFilename = 'hard.out'

    # generate new output filename if it already exists
    if os.path.isfile(outputFilename):
        i = 1
        while os.path.isfile(f'{outputFilename} ({i})'):
            i = i + 1
        outputFilename = f'{outputFilename} ({i})'

    parser = GraphParser(inputFilename)
    while parser.hasNext():
        graph = parser.readNextGraph()
        writeGraphToFile(graph, 123, outputFilename)

    parser.close()


def writeGraphToFile(graph, numLeaves, filename):
    file = open(filename, 'a')
    file.write(f'{numLeaves} {graph.vcount() - 1}\n')  # number of edges in a spanning tree is equal to number of vertices minus 1
    for edge in graph.to_tuple_list():
        file.write(f'{edge[0]} {edge[1]}\n')
    file.close()


if __name__ == '__main__':
    main()