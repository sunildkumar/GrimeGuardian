from icrawler.builtin import GoogleImageCrawler

google_crawler = GoogleImageCrawler(
    storage={
        "backend": "FileSystem",
        "root_dir": "/Users/sunilkumar/Dropbox/work/GrimeGuardian/data_scraping/empty_kitchen",
    }
)
google_crawler.crawl(keyword="empty kitchens with no one in them", max_num=100)

google_crawler = GoogleImageCrawler(
    storage={
        "backend": "FileSystem",
        "root_dir": "/Users/sunilkumar/Dropbox/work/GrimeGuardian/data_scraping/nonempty_kitchen",
    }
)
google_crawler.crawl(keyword="kitchen with a person in them", max_num=100)
