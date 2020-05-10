from html.parser import HTMLParser
from urllib import parse


class ContentFinder(HTMLParser):

    def __init__(self, page_url):
        super().__init__()
        self.page_url = page_url
        self.isTitle = False
        self.isContent = False
        self.content = {'title': '', 'content': ''}

    # When we call HTMLParser feed() this function is called when it encounters an opening tag <p> or <title>
    def handle_starttag(self, tag, attrs):
        if tag == 'p' or tag == 'b':
            self.isContent = True
        if tag == 'title':
            self.isTitle = True
    
    def handle_data(self, data):
        if self.isContent:
            print("The page" + self.page_url + "content: " + data)
            self.content['content'] = self.content['content'] + ' ' + data
            self.isContent = False
        elif self.isTitle:
            self.content['title'] = self.content['title'] + ' ' + data
            self.isTitle = False

    def page_content(self):
        return self.content

    def error(self, message):
        pass
