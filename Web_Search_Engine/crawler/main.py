import threading
from queue import Queue
from spider import Spider
from domain import *
from utils import *
import time
from graph import *

PROJECT_NAME = 'wikipedia'
HOMEPAGE = 'https://en.wikipedia.org/wiki/Computer_science'
DOMAIN_NAME = get_domain_name(HOMEPAGE)
QUEUE_FILE = PROJECT_NAME + '/queue.txt'
CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
GRAPH_FILE = PROJECT_NAME + '/graph.pkl'
NUMBER_OF_THREADS = 2
queue = Queue()
Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME)
total_crawled = 0
total_in_queue_file = 0
total_retrieved_pages = 0
max_retrieved_pages = 1
max_jobs = 1

# Create worker threads (will die when main exits)
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()
    return

# Do the next job in the queue
def work():
    global total_retrieved_pages
    while True:
        print("retrieved pages: " + str(total_retrieved_pages))
        url = queue.get()
        if(total_retrieved_pages < max_retrieved_pages):
            Spider.crawl_page(threading.current_thread().name, url)
        else:
             Spider.crawl_page_graph(threading.current_thread().name, url)
        print("Crawling task by thread is done")
        queue.task_done()

    '''
    while(queue.qsize() > 1):
        if(queue.qsize() == 1):
            print("Queue was emptied, no more jobs")
        queue.task_done()
    '''

# Each queued link is a new job
def create_jobs():
    global total_crawled
    print("Create jobs...")
    i = 0
    for link in file_to_set(QUEUE_FILE):
        queue.put(link)
        i += 1
        if(i > max_jobs):
            break
    queue.join()
    total_crawled += max_jobs
    crawl()

# Check if there are items in the queue, if so crawl them
def crawl():
    global total_in_queue_file, total_crawled, total_retrieved_pages
    print("Crawl...")
    queued_links = file_to_set(QUEUE_FILE)
    total_in_queue_file = len(queued_links)
    total_retrieved_pages = total_in_queue_file + total_crawled
    if total_in_queue_file > 0:
        print(str(len(queued_links)) + ' links in the queue')
        create_jobs()
    
create_workers()
crawl()
