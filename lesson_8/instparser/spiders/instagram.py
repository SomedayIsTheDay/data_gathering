import re
from lesson_8.instparser.items import InstparserItem
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["instagram.com"]
    start_urls = ["https://instagram.com/"]
    follow_link = "https://i.instagram.com/api/v1/friendships/"
    get_id_link = "https://i.instagram.com/api/v1/users/web_profile_info/"
    inst_login_link = "https://www.instagram.com/accounts/login/ajax/"
    inst_login = "lipyork"
    inst_pwd = (
        "#PWD_INSTAGRAM_BROWSER:10:1659687538:Aa9QAN6jjWRfvGkApCry5IVi/2SOjJUUvA/eiiT1QVodDJ10mM2XMVJtC6pMZZToa"
        "BQUHAMHq+XNO9nq4mRG//MGocN+2PKZjAqSRQZIkFBeg+6c2ZEAw11/mOn2nEIwfrQuppsGHmWKJXHhF30BThkO8fIU"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.users_to_parse = kwargs.get("users_to_parse")

    def parse(self, response: HtmlResponse, **kwargs):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method="POST",
            callback=self.login,
            formdata={"username": self.inst_login, "enc_password": self.inst_pwd},
            headers={"X-CSRFToken": csrf},
        )

    def login(self, response: HtmlResponse):
        if response.json()["authenticated"]:
            for user in self.users_to_parse:
                yield response.follow(
                    f"{self.get_id_link}?username={user}",
                    cb_kwargs={"username": user},
                    callback=self.user_parsing,
                    headers={"User-Agent": "Instagram 155.0.0.37.107"},
                )

    def user_parsing(self, response: HtmlResponse, username):
        user_id = response.json()["data"]["user"]["id"]
        followers = f"{self.follow_link}{user_id}/followers/?count=12&search_surface=follow_list_page"
        following = f"{self.follow_link}{user_id}/following/?count=12"
        for link in [followers, following]:
            yield response.follow(
                link,
                callback=self.follow_parsing,
                cb_kwargs={
                    "username": username,
                    "link": link,
                    "status": "following" if "following" in link else "follower",
                },
                headers={"User-Agent": "Instagram 155.0.0.37.107"},
            )

    def follow_parsing(self, response: HtmlResponse, username, link, status):
        j_data = response.json()
        if j_data.get("next_max_id"):
            next_max_id = j_data["next_max_id"]
            next_link = f"{link}&max_id={next_max_id}"
            yield response.follow(
                next_link,
                callback=self.follow_parsing,
                cb_kwargs={"username": username, "link": next_link, "status": status},
                headers={"User-Agent": "Instagram 155.0.0.37.107"},
            )
        users = j_data["users"]
        for user in users:
            loader = ItemLoader(item=InstparserItem(), response=response)
            loader.add_value("username", user["username"])
            loader.add_value("pfp_url", user["profile_pic_url"])
            loader.add_value("user_id", user["pk"])
            loader.add_value("status", status)
            loader.add_value("user_being_parsed", username)
            loader.add_value("link", f"https://www.instagram.com/{user['username']}/")
            yield loader.load_item()

    @staticmethod
    def fetch_csrf_token(text):
        matched = re.search('"csrf_token":"\\w+"', text).group()
        return matched.split(":").pop().replace(r'"', "")
