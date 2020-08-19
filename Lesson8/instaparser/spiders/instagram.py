import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = 'Buk_Pars'
    insta_password = '#PWD_INSTAGRAM_BROWSER:'
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_user = ['kotyapedotya', 'kwakpub']

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    user_followers_hash = 'c76146de99bb02f6415203be841dd25a'
    user_subscriptions_hash = 'd04b0a864b4b54837c0d870b0e77e076'

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_password},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for username in self.parse_user:
                yield response.follow(
                    f'/{username}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': username}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {
            "id": user_id,
            "include_reel": True,
            "fetch_mutual": False,
            "first": 50
        }

        user_followers_url = f'{self.graphql_url}query_hash={self.user_followers_hash}&{urlencode(variables)}'
        yield response.follow(
            user_followers_url,
            callback=self.user_posts_parse,
            cb_kwargs={
                'username': username,
                'user_id': user_id,
                'variables': deepcopy(variables),
                'followed_by': True
            }
        )

        user_subscriptions_url = f'{self.graphql_url}query_hash={self.user_subscriptions_hash}&{urlencode(variables)}'
        yield response.follow(
            user_subscriptions_url,
            callback=self.user_posts_parse,
            cb_kwargs={
                'username': username,
                'user_id': user_id,
                'variables': variables
            }
        )

    def user_posts_parse(self, response: HtmlResponse, username, user_id, variables, followed_by=False):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by' if followed_by else 'edge_follow')
        if page_info is None:
            return
        page_info = page_info.get('page_info') if page_info is not None else None
        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']
            url_posts = f'{self.graphql_url}query_hash={self.user_followers_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_posts_parse,
                cb_kwargs={
                    'username': username,
                    'user_id': user_id,
                    'variables': variables
                }
            )

        users = j_data.get('data').get('user').get('edge_followed_by' if followed_by else 'edge_follow').get(
            'edges')
        for user in users:
            item = InstaparserItem(
                user_id=user.get('node').get('id'),
                user_name=user.get('node').get('username'),
                full_name=user.get('node').get('full_name'),
                photo=user.get('node').get('profile_pic_url'),
                is_followed_by=user_id if followed_by else None,
                follows=None if followed_by else user_id
            )
            yield item

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')