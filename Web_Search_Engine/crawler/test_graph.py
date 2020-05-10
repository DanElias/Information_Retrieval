
import pickle
from graph import *
from utils import *
import numpy as np

grafo = file_to_graph("wikipedia/graph.pkl")
print("vertices in graph: " + str(len(grafo.vertices)))
#grafo.print_graph()

mat=np.matrix(grafo.edges)
np.savetxt('edges.txt',mat,fmt='%.2f')