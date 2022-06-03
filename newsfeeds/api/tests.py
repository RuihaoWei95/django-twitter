from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from testing.testcases import TestCase
from rest_framework.test import APIClient
from rest_framework import status

NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTest(TestCase):

    def setUp(self):


        self.gongzi = self.create_user('gongzi')
        self.gongzi_client = APIClient()
        self.gongzi_client.force_authenticate(self.gongzi)

        self.xiaoweige = self.create_user('xiaoweige')
        self.xiaoweige_client = APIClient()
        self.xiaoweige_client.force_authenticate(self.xiaoweige)

        # create following and followers
        for i in range(2):
            follower = self.create_user(f'xiaoweige_follower{i}')
            Friendship.objects.create(from_user=follower, to_user=self.xiaoweige)
        for i in range(3):
            following = self.create_user(f'xiaoweige_following{i}')
            Friendship.objects.create(from_user=self.xiaoweige, to_user=following)

    def test_list(self):
        # test login account
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # test POST
        response = self.gongzi_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # initial state, has nothing
        response = self.gongzi_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 0)

        self.gongzi_client.post(POST_TWEETS_URL, {'content': 'Hello Gongzi'})
        response = self.gongzi_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 1)

        self.gongzi_client.post(FOLLOW_URL.format(self.xiaoweige.id))
        response = self.xiaoweige_client.post(POST_TWEETS_URL, {
            'content': 'Hello Gongzi',
        })
        posted_tweet_id = response.data['id']
        response = self.gongzi_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)
