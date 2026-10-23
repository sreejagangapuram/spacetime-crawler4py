from collections import Counter, defaultdict

# urljoin: turns relative links into complete URLs
# urldefrag: removes fragments such as #section1
# BeautifulSoup: finds links inside HTML

# keeping track of unique pages 
visited_pages = set() 

# tracking longest page 
longest_page_url = ""
longest_page_words = 0

# counting how often each word appears 
word_frequencies = Counter() 

# counting unique pages in each ICS subdomain
subdomain_pages = defaultdict(set)

# common English stop words to ignore
# NLTK's list of english stopwords: https://gist.github.com/sebleier/554280 
stop_words = {
    "a", "about", "above", "after", "again", "against",
    "all", "am", "an", "and", "any", "are", "aren", "aren't",
    "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot",
    "could", "couldn", "couldn't", "d", "did", "didn",
    "didn't", "do", "does", "doesn", "doesn't", "doing",
    "don", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn", "hadn't", "has",
    "hasn", "hasn't", "have", "haven", "haven't", "having",
    "he", "her", "here", "hers", "herself", "him", "himself",
    "his", "how", "i", "if", "in", "into", "is", "isn",
    "isn't", "it", "it's", "its", "itself", "just", "ll",
    "m", "ma", "me", "mightn", "mightn't", "more", "most",
    "mustn", "mustn't", "my", "myself", "needn", "needn't",
    "no", "nor", "not", "now", "o", "of", "off", "on",
    "once", "only", "or", "other", "our", "ours",
    "ourselves", "out", "over", "own", "re", "s", "same",
    "shan", "shan't", "she", "she's", "should", "should've",
    "shouldn", "shouldn't", "so", "some", "such", "t",
    "than", "that", "that'll", "the", "their", "theirs",
    "them", "themselves", "then", "there", "these", "they",
    "this", "those", "through", "to", "too", "under",
    "until", "up", "ve", "very", "was", "wasn", "wasn't",
    "we", "were", "weren", "weren't", "what", "when",
    "where", "which", "while", "who", "whom", "why",
    "will", "with", "won", "won't", "would", "wouldn",
    "wouldn't", "y", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves"
}


import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup

import json 
import os 

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

        # getting the hostname of the webpage 
        hostname = urlparse(clean_url).hostname 

        # counting unique pages in each ICS subdomain
        if hostname and (
            hostname == "ics.uci.edu"
            or hostname.endswith(".ics.uci.edu")
        ): 
            subdomain_pages[hostname].add(clean_url)

        # extracting text from the webpage 
        soup = BeautifulSoup(resp.raw_response.content, "html.parser") 

        # removing code and non-visable text 
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)                 

        # counting the words 
        words = text.split() 
        word_count = len(words) 

        # converting text to lowercase and find words 
        clean_words = re.findall(r"[a-z0-9]+", text.lower())

        # removing common english stop words 
        filtered_words = [
            word for word in clean_words 
            if word not in stop_words
        ]

        # counting the words from this page 
        word_frequencies.update(filtered_words)

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

        # avoiding extremely long URLs
        if len(url) > 300:
            return False

        # avoiding URLs with too many path sections
        if len([part for part in parsed.path.split("/") if part]) > 10:
            return False

        # avoiding common calendar traps
        path = parsed.path.lower()

        if "calendar" in path or "/events/" in path:
            return False

        # avoiding URLs with too many query parameters
        if len(parsed.query.split("&")) > 5:
            return False

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

# function to save stats into crawler_stats.json
def save_stats(): 
    stats = {
        "visited_pages": sorted(visited_pages), 
        "longest_page_url": longest_page_url, 
        "longest_page_words": longest_page_words,
        "word_frequencies": dict(word_frequencies), 
         "subdomain_pages": {
            domain: sorted(pages)
            for domain, pages in subdomain_pages.items()
        }
    }

    # saving to a temporary file first
    with open("crawler_stats.tmp", "w") as file:
        json.dump(stats, file, indent=4)

    # replacing the old file with the completed file
    os.replace("crawler_stats.tmp", "crawler_stats.json")

# function to load saved stats 
def load_stats():
    global longest_page_url, longest_page_words

    # checking if saved statistics exist
    if not os.path.exists("crawler_stats.json"):
        return

    # read saved statistics
    with open("crawler_stats.json", "r") as file:
        stats = json.load(file)

    # restoring visited pages
    visited_pages.clear()
    visited_pages.update(stats["visited_pages"])

    # restoring longest page
    longest_page_url = stats["longest_page_url"]
    longest_page_words = stats["longest_page_words"]

    # restoring word frequencies
    word_frequencies.clear()
    word_frequencies.update(stats["word_frequencies"])

    # restoring subdomain pages
    subdomain_pages.clear()

    for domain, pages in stats["subdomain_pages"].items():
        subdomain_pages[domain] = set(pages)