from urllib.request import urlopen
from link_finder import LinkFinder
from domain import *
from utils import *
from graph import *
import pickle

class Spider:

    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    graph_file = ''
    queue = set()
    crawled = set()
    graph = Graph()

    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        Spider.graph_file = Spider.project_name + '/graph.pkl'
        self.boot()
        self.crawl_page('First crawler', Spider.base_url)

    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)
        Spider.graph = file_to_graph(Spider.graph_file)
        Spider.graph.add_vertex(Vertex(Spider.base_url))
        print("End of Crawler Boot")

    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' now crawling ' + page_url)
            print('Queue: ' + str(len(Spider.queue)) + ' | Crawled:  ' + str(len(Spider.crawled)))
            print('Graph Vertices: ' + str(len(Spider.graph.vertices)))
            gathered_links = Spider.gather_links(page_url)
            try:
                Spider.add_links_to_queue(gathered_links)
                Spider.add_vertices_edges_to_graph(page_url, gathered_links)
                Spider.queue.remove(page_url)
                Spider.crawled.add(page_url)
                Spider.update_files()
            except:
                Spider.update_files()

    # Updates graph by getting the links which already were crawled
    #It no longer add new links to the queue
    @staticmethod
    def crawl_page_graph(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' now crawling for graph ' + page_url)
            print('Queue: ' + str(len(Spider.queue)) + ' | Crawled:  ' + str(len(Spider.crawled)))
            print('Graph Vertices: ' + str(len(Spider.graph.vertices)))
            gathered_links = Spider.gather_links(page_url)
            try:
                Spider.add_edges_to_graph(page_url, gathered_links)
                Spider.queue.remove(page_url)
                Spider.crawled.add(page_url)
                Spider.update_files()
            except:
                Spider.update_files()
            
    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")
            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return set()
        return finder.page_links()

    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if Spider.domain_name != get_domain_name(url):
                continue
            Spider.queue.add(url)

    # Update the remaining links in pages to check if one of them 
    # references a page in the crawled or queued pages
    # It no longer adds unseen links to queue (boundary)
    @staticmethod
    def add_edges_to_graph(page_url, links):
        for target_url in links:
            if Spider.domain_name != get_domain_name(target_url):
                continue
            if (target_url in Spider.queue) or (target_url in Spider.crawled):
                Spider.graph.add_vertex(Vertex(page_url))
                Spider.graph.add_vertex(Vertex(target_url))
                Spider.graph.add_edge(page_url, target_url)
                print("------new edge added-------")
            else:
                continue

    # Adds to graph the new urls found and the edges
    @staticmethod
    def add_vertices_edges_to_graph(page_url, links):
        for target_url in links:
            if Spider.domain_name != get_domain_name(target_url):
                continue
            Spider.graph.add_vertex(Vertex(target_url))
            Spider.graph.add_edge(page_url, target_url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)
        graph_to_file(Spider.graph, Spider.graph_file)
        #mygraph = file_to_graph(Spider.graph_file)
        
            
       
