import scraper

# Start with clean statistics
scraper.visited_pages.clear()
scraper.word_frequencies.clear()
scraper.subdomain_pages.clear()
scraper.longest_page_url = ""
scraper.longest_page_words = 0

# Add sample data
scraper.visited_pages.add("https://www.ics.uci.edu/about")
scraper.word_frequencies["computer"] = 3
scraper.subdomain_pages["www.ics.uci.edu"].add(
    "https://www.ics.uci.edu/about"
)
scraper.longest_page_url = "https://www.ics.uci.edu/about"
scraper.longest_page_words = 100

# Save sample data
scraper.save_stats()

# Clear the data to simulate a restart
scraper.visited_pages.clear()
scraper.word_frequencies.clear()
scraper.subdomain_pages.clear()
scraper.longest_page_url = ""
scraper.longest_page_words = 0

# Load saved data
scraper.load_stats()

# Check recovered values
print("Visited pages:", len(scraper.visited_pages))
print("Computer count:", scraper.word_frequencies["computer"])
print("Longest page:", scraper.longest_page_url)
print("Longest page words:", scraper.longest_page_words)
print("ICS subdomains:", len(scraper.subdomain_pages))