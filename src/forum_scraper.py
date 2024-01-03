import requests
from lxml.html import fromstring

from src.secret import USER_AGENT


class NotLoggedInError(Exception):
    """Raised when user is not logged"""
    pass


class ForumScraper:
    def __init__(self, url: str, cookie: str, prod: bool = True):
        self.prod = prod
        self.payload = {}
        self.my_name = None
        self.url = url
        self.ses = requests.Session()
        self.ses.headers.update({"user-agent": USER_AGENT})
        self.ses.cookies.update({"xf_user" if prod else "2213_user": cookie})

        self.get_authorization()

    def reply(self, thread_id: str, response: str):
        url = f"{self.url.split('/forums')[0]}/threads/{thread_id}/add-reply"
        self.payload["message"] = response
        self.ses.post(url, data=self.payload)

    def get_authorization(self):
        try:
            res = self.ses.get(self.url)
            res.raise_for_status()
            # print(res.text[30:550])
            html = fromstring(res.content)
            self.payload['_xfToken'] = html.find('.//input[@name="_xfToken"]').value
            self.my_name = html.xpath('//*[@id="top"]/div[1]/div[2]/nav/div/div[4]/div[1]/a[1]/span[2]/text()')[0] if (
                self.prod) else html.xpath('/html/body/div[1]/div[1]/nav/div/div[3]/div[1]/a[1]/@title')[0]
        except (AttributeError, IndexError, requests.RequestException) as e:
            raise NotLoggedInError(f"message: not logged in! Error: {str(e)}")

    def get_alerts(self) -> list[dict | None]:
        post_ids = []
        url = f"{self.url.split('/forums')[0]}/account/alerts-popup?_xfToken={self.payload['_xfToken']}&_xfResponseType=json"
        res = self.ses.get(url)
        res.raise_for_status()
        tree = fromstring(res.json()["html"]["content"])
        alerts = tree.xpath('ol')
        if not alerts:
            return alerts
        for alert in reversed(alerts[0]):
            alert_text = alert.xpath('div/div/div[2]/text()[2]')[0].strip()
            alert_type = alert_text.split(" ", maxsplit=1)[0] if alert_text else ""
            # print("alert type", alert_type)
            if any(wrd in alert_text for wrd in ["mentioned", "quoted"]):
                post_id = {
                    "type": alert_type,
                    "id": alert.xpath(
                        'div/div/div[2]/a[2]/@href'
                    )[0].replace("/posts/" if self.prod else "/2213/index.php?posts/", "")[:-1]
                }
                post_ids.append(post_id)
        return post_ids

    def get_post(self, post_id: str) -> tuple[str, str, str, str, str, str]:
        text_selector = 'div/div[2]/div/div/div/article/div[1]/div/node()[not(ancestor-or-self::blockquote)]'
        quote_selector = './div/div[2]/div/div/div/article/div[1]/div/blockquote/div[2]/div[1]/node()'
        url = f"{self.url.split('/forums')[0]}/posts/{post_id}/show?_xfToken={self.payload['_xfToken']}&_xfResponseType=json"
        res = self.ses.get(url)
        res.raise_for_status()
        tree = fromstring(res.json()["html"]["content"])
        article = tree.xpath('div/div/article[1]')[0]
        thread = article.xpath('div/div[2]/div/header/ul[1]/li/a/@href')[0].rsplit("/", maxsplit=2)[1]
        author_id_raw = article.xpath("div/div[1]/section/div[1]/div/a/@data-user-id")
        author_id = author_id_raw[0] if author_id_raw else "0"
        author_name_raw = article.xpath("@data-author")
        author_name = author_name_raw[0] if author_id_raw else "Deleted User"
        timestamp = article.xpath("div/div[2]/div/header/ul[1]/li/a/time/@data-time")[0]
        quote = ''.join(
            [ele if isinstance(ele, str) else ele.text_content() for ele in article.xpath(quote_selector)]
        ).strip()
        text = ''.join([ele if isinstance(ele, str) else ele.text_content() for ele in article.xpath(text_selector)])
        return author_id, author_name, timestamp, thread, quote, text
