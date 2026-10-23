from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker

import scraper

import os 

class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")

        # load previous statistics only when resuming 
        if not restart:
            scraper.visited_pages.clear()
            scraper.word_frequencies.clear()
            scraper.subdomain_pages.clear()
            scraper.longest_page_url = ""
            scraper.longest_page_words = 0

            # Remove old statistics from previous runs
            if os.path.exists("crawler_stats.json"):
                os.remove("crawler_stats.json")
        else:
            scraper.load_stats()

        self.frontier = frontier_factory(config, restart)
        self.workers = list()
        self.worker_factory = worker_factory

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        self.join()

    def join(self):
        for worker in self.workers:
            worker.join()

        # saving statistics after all workers finish 
        scraper.save_stats()
