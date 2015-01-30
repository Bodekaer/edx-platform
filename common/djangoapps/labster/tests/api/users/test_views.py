import json
from datetime import date

from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from labster.models import LabsterUser
from student.models import UserProfile


class UserCreateTest(APITestCase):

    def setUp(self):
        self.url = '/labster/api/users/'

    def test_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, 405)

    def test_post_no_data(self):
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, 400)

    def test_post_no_email(self):
        data = {'email': ""}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_post(self):
        data = {'email': "user@email.com"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)

        users = User.objects.filter(email=data['email'])
        self.assertTrue(users.exists())

        user = users[0]
        self.assertFalse(user.has_usable_password())

        content = json.loads(response.content)
        self.assertEqual(content['id'], user.id)
        self.assertEqual(content['email'], user.email)


class UserViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='username', email='user@email.com', password='password')
        self.url = '/labster/api/users/{}/'.format(self.user.id)

        labster_user = LabsterUser.objects.get(user=self.user)
        labster_user.date_of_birth = date(2000, 1, 1)
        labster_user.language = 'en'
        labster_user.nationality = 1
        labster_user.save()

    def test_not_logged_in(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, 401)

        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, 401)

        response = self.client.put(self.url, format='json')
        self.assertEqual(response.status_code, 401)

    def test_get(self):
        self.client.login(username='username', password='password')
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, 200)

        labster_user = LabsterUser.objects.get(user=self.user)
        profile = UserProfile.objects.get(user=self.user)

        content = json.loads(response.content)
        self.assertEqual(content['user_id'], self.user.id)
        self.assertEqual(
            content['date_of_birth'],
            labster_user.date_of_birth.strftime('%Y-%m-%d'))
        self.assertEqual(content['nationality'], labster_user.nationality)
        self.assertEqual(content['language'], labster_user.language)
        self.assertEqual(content['unique_id'], labster_user.unique_id)
        self.assertEqual(content['is_labster_verified'], labster_user.is_labster_verified)
        # self.assertEqual(content['name'], profile.name)

    def test_post(self):
        self.client.login(username='username', password='password')
        data = {
            'date_of_birth': "2000-01-01",
            'nationality': "MY",
            'language': "zh",
            'unique_id': "aabbcc",
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertEqual(data['date_of_birth'], content['date_of_birth'])
        self.assertEqual(data['nationality'], content['nationality'])
        self.assertEqual(data['language'], content['language'])
        self.assertEqual(data['unique_id'], content['unique_id'])

    # def test_post_update_name(self):
    #     self.client.login(username='username', password='password')
    #     data = {'name': "The Name"}
    #     response = self.client.put(self.url, data, format='json')
    #     self.assertEqual(response.status_code, 200)

    #     user = User.objects.get(id=self.user.id)
    #     self.assertEqual(user.profile.name, data['name'])
