from src.forum_scraper import ForumScraper
from src.secret import URL, COOKIE

if __name__ == "__main__":
    fs = ForumScraper(URL, COOKIE, False)
    r = fs.get_alerts()
    # r = fs.get_post(538315953)
    # r = fs.get_post(2)

    print(r)
