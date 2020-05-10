import os
from graph import *
import pickle

# Each website is a separate project (folder)
def create_project_dir(directory):
    if not os.path.exists(directory):
        print('Creating directory ' + directory)
        os.makedirs(directory)

# Create queue and crawled files (if not created)
def create_data_files(project_name, base_url):
    queue = os.path.join(project_name , 'queue.txt')
    crawled = os.path.join(project_name,"crawled.txt")
    graph = os.path.join(project_name,"graph.pkl")
    if not os.path.isfile(queue):
        write_file(queue, base_url)
    if not os.path.isfile(crawled):
        write_file(crawled, '')
    if not os.path.isfile(graph):
        write_graph_file(graph, Graph())

# Create a new file
def write_file(path, data):
    with open(path, 'w') as f:
        f.write(data)

# Create a new file
def write_graph_file(path, data):
    f = open(path, "wb")
    pickle.dump(data, f)
    f.close()

# Add data onto an existing file
def append_to_file(path, data):
    with open(path, 'a') as file:
        file.write(data + '\n')

# Delete the contents of a file
def delete_file_contents(path):
    open(path, 'w').close()

# Read a file and convert each line to set items
def file_to_set(file_name):
    results = set()
    with open(file_name, 'rt') as f:
        for line in f:
            results.add(line.replace('\n', ''))
    return results

# Read binary file with Graph object
def file_to_graph(file_name):
    try:
        saved_graph = Graph()
        with open(file_name,"rb") as f:
            print("Retrieving graph...")
            saved_graph.vertices = pickle.load(f)
            print("Loaded vertices")
            saved_graph.edges = pickle.load(f)
            print("Loaded edges")
            saved_graph.edge_indices = pickle.load(f)
        print("Success in retrieving graph")
        return saved_graph
    except:
        print("Failed to retrieve saved graph")
        return Graph()

# Iterate through a set, each item will be a line in a file
def set_to_file(links, file_name):
    with open(file_name,"w", encoding="utf-8") as f:
        for l in sorted(links):
            f.write(l+"\n")

#Write Graph object to binary file
def graph_to_file(graph_object, file_name):
    with open(file_name,"wb") as f:
        pickle.dump(graph_object.vertices,  f)
        pickle.dump(graph_object.edges,  f)
        pickle.dump(graph_object.edge_indices,  f)

    #mygraph = file_to_graph(file_name)
    #mygraph.print_graph()



    