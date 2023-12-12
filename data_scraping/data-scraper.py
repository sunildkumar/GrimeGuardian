from icrawler.builtin import GoogleImageCrawler

google_crawler = GoogleImageCrawler(
    storage={
        "backend": "FileSystem",
        "root_dir": "/Users/sunilkumar/Dropbox/work/GrimeGuardian/data_scraping/clean_sink",
    }
)
google_crawler.crawl(keyword="clean sink", max_num=100)

google_crawler = GoogleImageCrawler(
    storage={
        "backend": "FileSystem",
        "root_dir": "/Users/sunilkumar/Dropbox/work/GrimeGuardian/data_scraping/dirty_sink",
    }
)
google_crawler.crawl(keyword="sink full of dishes", max_num=100)
