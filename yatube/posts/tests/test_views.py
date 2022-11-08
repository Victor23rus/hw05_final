import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post, User

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',

        )
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )
        cls.templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': cls.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': cls.user}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={
                        'post_id': cls.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': cls.post.pk}): 'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',

        }

    def setUp(self):
        self.guest_client = Client()
        self.user = PostURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        for reverse_name, template in self.templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertIn('page_obj', response.context)
        self.assertEqual(first_object.image, self.post.image)
        self.assertEqual(post_author_0, PostURLTests.user)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, PostURLTests.group)

    def test_post_group_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertIn('page_obj', response.context)
        self.assertEqual(first_object.image, self.post.image)
        self.assertEqual(post_author_0, PostURLTests.user)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, PostURLTests.group)

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertIn('page_obj', response.context)
        self.assertEqual(first_object.image, self.post.image)
        self.assertEqual(post_author_0, PostURLTests.user)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, PostURLTests.group)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}))
        first_object = response.context['post']
        post_author = first_object.author
        post_text = first_object.text
        post_group = first_object.group
        self.assertEqual(first_object.image, self.post.image)
        self.assertEqual(post_author, PostURLTests.user)
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, Group.objects.get(slug=self.group.slug))

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIn('form', response.context)
                self.assertIsInstance(form_field, expected)

    def test_post_create_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIn('form', response.context)
                self.assertIsInstance(form_field, expected)

    def test_post_in_pages(self):
        form_fields = {
            reverse('posts:index'): Post.objects.get(group=self.post.group),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): Post.objects.get(group=self.post.group),
            reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ): Post.objects.get(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertIn('page_obj', response.context)
                self.assertIn(expected, form_field)

    def test_check_group_not_in_group_list_page(self):
        form_fields = {
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): Post.objects.exclude(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertIn('page_obj', response.context)
                self.assertNotIn(expected, form_field)

    def test_cache(self):
        response_1 = self.authorized_client.get(reverse('posts:index'))
        content_1 = response_1.content
        Post.objects.all().delete
        response_2 = self.authorized_client.get(reverse('posts:index'))
        content_2 = response_2.content
        self.assertEqual(content_1, content_2)
        Post.objects.all().delete
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        content_3 = response_3.content
        self.assertNotEqual(content_1, content_3)

    def test_follow_page(self):
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
        Follow.objects.get_or_create(user=self.user, author=self.post.author)
        response_2 = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response_2.context['page_obj']), 1)
        self.assertIn(self.post, response_2.context['page_obj'])

    def test_unfollow_page(self):
        Follow.objects.all().delete()
        response_3 = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response_3.context['page_obj']), 0)


PAGINATOR_DISPLAY = 13


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        self.post: list = []
        for i in range(PAGINATOR_DISPLAY):
            self.post.append(Post(
                text=f'Тестовый текст {i}',
                group=self.group,
                author=self.user))
        Post.objects.bulk_create(self.post)

    def test_first_page_index_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_group_list_contains_ten_records(self):
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_list_contains_three_records(self):
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_profile_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_contains_three_records(self):
        response = self.client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
