from urllib.parse import urlparse


# Get domain name (example.com)
def get_domain_name(url):
    try:
        results = get_sub_domain_name(url).split('.')
        results_slashes = url.split('/')
        if(results[-3] == "en" 
        and results_slashes[3] == "wiki" 
        and "Special:" not in url
        and "Book:" not in url
        and "Category:" not in url
        and "Portal:" not in url
        and "Special:" not in url
        and "File:" not in url
        and "Template:" not in url
        and "Image:" not in url
        and "Wikipedia:" not in url
        and "Talk:" not in url
        and "Template_talk:" not in url
        and "Help:" not in url
        and "cite" not in url
        and "#" not in url):
            return results[-3] + '.' + results[-2] + '.' + results[-1]
        else:
            return ''
    except:
        return ''


# Get sub domain name (name.example.com)
def get_sub_domain_name(url):
    try:
        return urlparse(url).netloc
    except:
        return ''
