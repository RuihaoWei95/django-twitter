from friendships.models import Friendship
from testing.testcases import TestCase
from rest_framework.test import APIClient
from rest_framework import status

FOLLOW_URL = '/api/friendships/{}/follow/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'


class FriendshipApiTest(TestCase):

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

    def test_follow(self):
        url = FOLLOW_URL.format(self.xiaoweige.id)

        # need to login to follow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # need to POST to follow
        response = self.gongzi_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # can't follow yourself
        response = self.xiaoweige_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # follow successfully
        response = self.gongzi_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # follow again
        response = self.gongzi_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['duplicate'], True)

        # follow the other way will create new friendship
        count = Friendship.objects.count()
        response = self.xiaoweige_client.post(FOLLOW_URL.format(self.gongzi.id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.xiaoweige.id)

        # need to login to unfollow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # need to POST to unfollow
        response = self.gongzi_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # can't unfollow yourself
        response = self.xiaoweige_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # unfollow successfully
        Friendship.objects.create(from_user=self.gongzi, to_user=self.xiaoweige)
        count = Friendship.objects.count()
        response = self.gongzi_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # unfollow again
        count = Friendship.objects.count()
        response = self.gongzi_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.xiaoweige.id)

        # POST is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # GET is allowed
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['followings']), 3)
        # make sure order by reversed create_at time
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'xiaoweige_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'xiaoweige_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'xiaoweige_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.xiaoweige.id)
        # POST is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # GET
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual((len(response.data['followers'])), 2)

        # check timestep
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'xiaoweige_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'xiaoweige_follower0',
        )



