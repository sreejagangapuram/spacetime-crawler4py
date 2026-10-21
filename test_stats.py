from types import SimpleNamespace
import scraper as crawler_scraper

def make_response(html):
    return SimpleNamespace(
        status=200,
        url="https://www.ics.uci.edu/about",
        raw_response=SimpleNamespace(content=html.encode())
    )

crawler_scraper.scraper(
    "https://www.ics.uci.edu/about",
    make_response("<h1>The hello world and the university</h1>")
)

crawler_scraper.scraper(
    "https://www.ics.uci.edu/about#section",
    make_response("<h1>Hello world</h1>")
)

print("Unique pages:", len(crawler_scraper.visited_pages))
print("Longest page:", crawler_scraper.longest_page_url)
print("Word count:", crawler_scraper.longest_page_words)
print("Word frequencies:", crawler_scraper.word_frequencies.most_common(5))

# checking if common stop words were removed
print("Stop words removed:", "the" not in crawler_scraper.word_frequencies)

# showing the 50 most common words
print("Top 50 words:", crawler_scraper.word_frequencies.most_common(50))