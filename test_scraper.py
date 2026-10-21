from types import SimpleNamespace
from scraper import scraper

html = b"""
<html>
    <body>
        <a href="/faculty">Faculty</a>
        <a href="/research#overview">Research</a>
        <a href="https://google.com">Google</a>
        <a href="/documents/file.pdf">PDF</a>
        <a href="/faculty">Faculty again</a>
    </body>
</html>
"""

response = SimpleNamespace(
    status=200,
    url="https://www.ics.uci.edu",
    raw_response=SimpleNamespace(content=html)
)

links = scraper("https://www.ics.uci.edu", response)

for link in sorted(links):
    print(link)