from graphParser import GraphParser

def main():
    inputFilename = 'hard.in'
    parser = GraphParser(inputFilename)
    while parser.hasNext():
        graph = parser.readNextGraph()
        print(graph)

    parser.close()


if __name__ == '__main__':
    main()