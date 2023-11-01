from rest_framework.test import APITestCase
from blog_app.models import Post
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status


class BlogAppAPITestCase(APITestCase):
    def setUp(self):
        author = User.objects.create(username='admin')

        self.test_post_publish_old = Post.objects.create(
            title='test_published_post_old', slug='test-published-post-old', author=author,
            body='test_1', publish='2023-10-20 20:08:21+10', status='PB'
        )
        self.test_post_publish_new = Post.objects.create(
            title='test_published_post_new_long', slug='test-published-post-new', author=author,
            body='test_2 long long long long long long long long long long long long long long long '
                 'long long long long long long long long long long long long long long long',
            publish='2023-10-26 20:08:21+10', status='PB'
        )
        self.test_draft_post = Post.objects.create(
            title='test_draft_post', slug='test-draft-post', author=author,
            body='test_3', publish='2023-10-25 20:08:21+10', status='DF'
        )

        self.url = reverse('blog_app:post_list')
        self.url_detail_existing_post = reverse(
            'blog_app:post_detail', args=[1, 'test-published-post-old']
        )
        self.url_detail_non_existent_post = reverse(
            'blog_app:post_detail', args=[60065, 'test-non-existent-post']
        )

        # TODO: Continue testing data when response is through django rest framework. Compare data
        # TODO: Add share on email tests

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_more_pages_than_there_are(self):
        response = self.client.get(self.url + '?page=-1')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_page_num_not_int(self):
        response = self.client.get(self.url + '?page=Hi!')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_detail_existing_post(self):
        response = self.client.get(self.url_detail_existing_post)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_detail_non_existent_post(self):
        response = self.client.get(self.url_detail_non_existent_post)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
