import scraper

test_urls = [
    "https://www.ics.uci.edu/about",
    "https://www.ics.uci.edu/calendar/2026",
    "https://www.ics.uci.edu/events/2026/10/21",
    "https://www.ics.uci.edu/a/b/c/d/e/f/g/h/i/j/k",
    "https://www.ics.uci.edu/search?a=1&b=2&c=3&d=4&e=5&f=6",
    "https://www.google.com"
]

for url in test_urls:
    print(scraper.is_valid(url), url)