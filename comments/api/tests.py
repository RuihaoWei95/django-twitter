from testing.testcases import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from comments.models import Comment


COMMENT_URL = '/api/comments/'
COMMENT_UPDATE_URL = '/api/comments/{}/'
COMMENT_DESTROY_URL = '/api/comments/{}/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.linghu = self.create_user('linghu')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)
        self.dongxie = self.create_user('dongxie')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

        self.tweet = self.create_tweet(self.linghu)

    def test_create(self):
        # 匿名不可以创建
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # 啥参数都没带不行
        response = self.linghu_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # 只带 tweet_id 不行
        response = self.linghu_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)

        # 只带 content 不行
        response = self.linghu_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # content 太长不行
        response = self.linghu_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # tweet_id 和 content 都带才行
        response = self.linghu_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.linghu.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')

    def test_update(self):
        comment = self.create_comment(self.linghu, self.tweet, 'original')
        another_tweet = self.create_tweet(self.dongxie)

        # anonymous user can't update
        response = self.anonymous_client.put(COMMENT_UPDATE_URL.format(comment.id), {'content': 'new'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # not owner can't update
        response = self.dongxie_client.put(COMMENT_UPDATE_URL.format(comment.id), {'content': 'new'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')
        # can only update content
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.linghu_client.put(COMMENT_UPDATE_URL.format(comment.id), {
            'content': 'new',
            'user_id': self.dongxie.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.linghu)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)

    def test_destroy(self):
        comment = self.create_comment(self.linghu, self.tweet)
        # anonymous can't destroy
        response = self.anonymous_client.delete(COMMENT_DESTROY_URL.format(comment.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # not owner can't delete
        response = self.dongxie_client.delete(COMMENT_DESTROY_URL.format(comment.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # delete
        count = Comment.objects.count()
        response = self.linghu_client.delete(COMMENT_DESTROY_URL.format(comment.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_list(self):
        # needs to include tweet id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # check no comments
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 0)

        # check comments in order of time
        self.create_comment(self.linghu, self.tweet, '1')
        self.create_comment(self.linghu, self.tweet, '2')
        self.create_comment(self.dongxie, self.create_tweet(self.dongxie), '3')

        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.linghu.id
        })
        self.assertEqual(len(response.data['comments']), 2)