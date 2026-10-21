# urljoin: turns relative links into complete URLs
# urldefrag: removes fragments such as #section1
# BeautifulSoup: finds links inside HTML

# keeping track of unique pages 
visited_pages = set() 

# tracking longest page 
longest_page_url = ""
longest_page_words = 0

import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup

def scraper(url, resp):
    global longest_page_url, longest_page_words

    # skip pages that didnt download successfully 
    if resp.status != 200 or resp.raw_response is None: 
        return [] 

    # removing fragments from the page URL 
    clean_url = urldefrag(resp.url or url)[0]

    # record page if it hasnt been visted 
    if clean_url not in visited_pages:
        visited_pages.add(clean_url)

    # extracting text from the webpage 
    soup = BeautifulSoup(resp.raw_response.content, "html.parser") 

    # removing code and non-visable text 
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)                 

    # counting the words 
    words = text.split() 
    word_count = len(words) 

    # saving the page if its the longest so far 
    if word_count > longest_page_words: 
        longest_page_words = word_count 
        longest_page_url = clean_url
    
    # extracting links from this page 
    links = extract_next_links(url, resp)

    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # checking if the webpage downloaded sucessfully 
    if resp.status != 200 or resp.raw_response is None: 
        return []

    # getting the HTML content 
    html = resp.raw_response.content 

    if not html:
        return [] 

    # reading the HTML using BeautifulSoup 
    soup = BeautifulSoup(html, "html.parser")

    links = set() 

    # using response URL in case the page redirected
    base_url = resp.url or url 

    # finding all links in webpage 
    for tag in soup.find_all("a", href=True): 
        href = tag["href"]

        # converting relative links into full URLs
        full_url = urljoin(base_url, href) 

        #removing fragments 
        clean_url = urldefrag(full_url)[0]

        #only keep valid URLs
        if is_valid(clean_url):
            links.add(clean_url)

    return list(links)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)

        # only allow links for four required UCI domains 
        # checking website's hostname before allowing the crawler to visit it 
        allowed_domains = (
            "ics.uci.edu",
            "cs.uci.edu",
            "informatics.uci.edu", 
            "stat.uci.edu"
        )

        hostname = parsed.hostname 

        if not hostname:
            return False 

        if not any (
            hostname == domain or hostname.endswith("." + domain)
            for domain in allowed_domains
        ):

            return False 
        
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
