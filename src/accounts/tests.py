from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase


# Test accounts
class AccountModelTests(TestCase):
    """Test the account model"""

    def test_create_user(self):
        """Test account creation"""

        user = User.objects.create_user("will", "", "testpass1234")
        user.save()
        self.assertEqual(user.username, "will")
        self.assertNotEqual(user.password, "testpass1234")  # Should be hashed
        self.assertEqual(user.email, "")
        self.assertNotEqual(user.is_superuser, True)
        self.assertNotEqual(user.is_staff, True)

        User.objects.get(username="will").delete()

    def test_create_superuser(self):
        """Test superuser creation"""

        admin_user = User.objects.create_superuser("superuser", "", "testpass1234")
        admin_user.save()
        self.assertEqual(admin_user.username, "superuser")
        self.assertEqual(admin_user.is_superuser, True)
        self.assertEqual(admin_user.is_staff, True)

        User.objects.get(username="superuser").delete()

    def change_user_password(self):
        """Test changing a user's password"""

        user = User.objects.create_user(
            username="will", password="testpass1234", email=""
        )
        user.save()
        user.set_password("newpass12345")

        newuser = authenticate(username="will", password="newpass12345")
        self.assertIsNotNone(newuser)

        User.objects.get(username="will").delete()


class AccountViewsTests(TestCase):
    """Test the account views"""

    def test_account_creation(self):
        """Test user's account creation"""

        response = self.client.post(
            "/accounts/register/",
            {
                "username": "will",
                "first_name": "Will",
                "last_name": "Null",
                "email": "noreply@appu.ltd",
                "password1": "testpass1234",
                "password2": "testpass1234",
            },
        )
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username="will")
        self.assertIsNotNone(user)

        User.objects.get(username="will").delete()

    def test_account_login(self):
        """Test user's account login"""

        user = User.objects.create_user(
            username="will", password="testpass1234", email=""
        )
        user.save()

        response = self.client.post(
            "/accounts/login/", {"username": "will", "password": "testpass1234"}
        )
        self.assertEqual(response.status_code, 302)

        User.objects.get(username="will").delete()

    def test_account_logout(self):
        """Test user's account logout"""

        user = User.objects.create_user(
            username="will", password="testpass1234", email=""
        )
        user.save()

        response = self.client.post(
            "/accounts/login/", {"username": "will", "password": "testpass1234"}
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.post("/accounts/logout/")
        self.assertEqual(response.status_code, 302)

        User.objects.get(username="will").delete()

    def test_account_profile(self):
        """Test user's account profile"""

        user = User.objects.create_user(
            username="will", password="testpass1234", email=""
        )
        user.save()

        response = self.client.post(
            "/accounts/login/", {"username": "will", "password": "testpass1234"}
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/accounts/")
        self.assertContains(response, "will")
        self.assertEqual(response.status_code, 200)

        User.objects.get(username="will").delete()

    def test_invalid_registration(self):
        """Test invalid registration"""

        # Password too short
        response = self.client.post(
            "/accounts/register/",
            {
                "username": "will",
                "first_name": "Will",
                "last_name": "Null",
                "email": "noreply@appu.ltd",
                "password1": "testpass123",
                "password2": "testpass123",
            },
        )
        self.assertEqual(response.status_code, 302)

        self.assertFalse(User.objects.filter(username="will").exists())

        # Invalid email
        response = self.client.post(
            "/accounts/register/",
            {
                "username": "will",
                "first_name": "Will",
                "last_name": "Null",
                "email": "noreply",
                "password1": "testpass1234",
                "password2": "testpass1234",
            },
        )
        self.assertEqual(response.status_code, 302)

        self.assertFalse(User.objects.filter(username="will").exists())

        # Passwords don't match
        response = self.client.post(
            "/accounts/register/",
            {
                "username": "will",
                "first_name": "Will",
                "last_name": "Null",
                "email": "noreply@appu.ltd",
                "password1": "testpass1234",
                "password2": "testpass12345",
            },
        )
        self.assertEqual(response.status_code, 302)

        self.assertFalse(User.objects.filter(username="will").exists())

        # Username already exists
        user = User.objects.create_user(
            username="will", password="testpass1234", email=""
        )
        user.save()

        response = self.client.post(
            "/accounts/register/",
            {
                "username": "will",
                "first_name": "Will",
                "last_name": "Null",
                "email": "noreply@appu.ltd",
                "password1": "testpass1234",
                "password2": "testpass1234",
            },
        )
        self.assertEqual(response.status_code, 302)

        self.assertTrue(User.objects.filter(username="will").exists())

        User.objects.get(username="will").delete()

    def test_invalid_login(self):
        """Test invalid login"""

        # User doesn't exist
        response = self.client.post(
            "/accounts/login/", {"username": "will", "password": "testpass1234"}
        )
        self.assertEqual(response.status_code, 302)

        # Invalid password
        user = User.objects.create_user(
            username="will", password="testpass1234", email=""
        )
        user.save()

        response = self.client.post(
            "/accounts/login/", {"username": "will", "password": "testpass12345"}
        )
        self.assertEqual(response.status_code, 302)

        User.objects.get(username="will").delete()
