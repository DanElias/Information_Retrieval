
class Vertex:
    def __init__(self, name):
        self.name = name

#Graph using adjacency matrix
class Graph:
    #vertices dictionary is used to locate any vertex given its name
    vertices = {}
    #edges list will be the adjacency matrix
    edges = []
    #dictionary to locate the index of any edge given its name
    edge_indices = {}

    def add_vertex(self, vertex):
        #Check if its the first time we have seen this vertex in the graph
        if isinstance(vertex, Vertex) and vertex.name not in self.vertices:
            #save it in the vertices dictionary
            self.vertices[vertex.name] = vertex
            #We add another column to the adjacency matrix initialized with zeroes
            for row in self.edges:
                row.append(0)
            #We add a new row for the new vertex initialized with zeroes
            self.edges.append([0] * (len(self.edges) + 1))
            #Map the vertices dictionary to the edges matrix
            #edges_indices stores which row in the edge matrix corresponds to which vertex name
            self.edge_indices[vertex.name] = len(self.edge_indices)
            return True
        else:
            return False

    def add_edge(self, u, v, weight = 1):
        if u in self.vertices and v in self.vertices:
            # u is the start vertex, v is the target vertex
            # u -> v
            self.edges[self.edge_indices[u]][self.edge_indices[v]] = weight
            #This line would be for a undirected graph, diagonally simetrical
            #self.edges[self.edge_indices[v]][self.edge_indices[u]] = weight
            return True
        else:
            return False

    def print_graph(self):
        print("Printing graph...")
        for v, i in sorted(self.edge_indices.items()):
            print(v + ' ', end = '')
            for j in range(len(self.edges)):
                print(self.edges[i][j], end = '')
            print(' ')

'''
import pickle

#Test code

g = Graph()
for i in range(ord("A"), ord("D")):
    g.add_vertex(Vertex(chr(i)))

edges = [ ["A", "B"], ["B", "A"], ["A", "C"],  ["B", "C"] ]
for edge in edges:
    g.add_edge(edge[0], edge[1])

g.print_graph()

f = open("wikipedia/graph.txt", "wb")
pickle.dump(g, f)
f.close()

graph = Graph()
f = open("wikipedia/graph.txt", "rb")
graph = pickle.load(f)
f.close()
graph.print_graph()
'''