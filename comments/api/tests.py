from rest_framework import status
from rest_framework.test import APIClient
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.xiaoweige = self.create_user('xiaoweige')
        self.xiaoweige_client = APIClient()
        self.xiaoweige_client.force_authenticate(self.xiaoweige)
        self.gongzi = self.create_user('gongzi')
        self.gongzi_client = APIClient()
        self.gongzi_client.force_authenticate(self.gongzi)

        self.tweet = self.create_tweet(self.xiaoweige)

    def test_case(self):
        # anonymous can't create comment
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # should include tweet and content
        response = self.xiaoweige_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # only include tweet id is not allowed
        response = self.xiaoweige_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # only include content is not allowed
        response = self.xiaoweige_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # content exceed maximum length is not allowed
        response = self.xiaoweige_client.post(COMMENT_URL, {'content': '1' * 141})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('content' in response.data['errors'], True)

        # test legal request
        response = self.xiaoweige_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': 'gongzi',
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.xiaoweige.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], 'gongzi')


