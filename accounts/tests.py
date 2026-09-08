from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()

CHANGE_URL = '/password-change/'
TEMP_PASSWORD = 'Temp12345!'
NEW_PASSWORD = 'Aa1!strongpw#2026'


class ForcePasswordChangeTests(TestCase):
    """First-login password change: accounts/middleware.py + accounts.views.password_change."""

    def test_new_user_is_flagged(self):
        user = User.objects.create_user(username='newfac', email='newfac@cud.ac.ae',
                                        password=TEMP_PASSWORD)
        self.assertTrue(user.must_change_password)

    def test_flagged_user_is_redirected_to_the_change_form(self):
        User.objects.create_user(username='newfac', email='newfac@cud.ac.ae',
                                 password=TEMP_PASSWORD)
        self.assertTrue(self.client.login(username='newfac@cud.ac.ae', password=TEMP_PASSWORD))

        response = self.client.get('/projects/')
        self.assertRedirects(response, CHANGE_URL, fetch_redirect_response=False)

    def test_change_form_itself_is_reachable(self):
        """Guards against a redirect loop."""
        User.objects.create_user(username='newfac', email='newfac@cud.ac.ae',
                                 password=TEMP_PASSWORD)
        self.client.login(username='newfac@cud.ac.ae', password=TEMP_PASSWORD)

        self.assertEqual(self.client.get(CHANGE_URL).status_code, 200)

    def test_weak_password_is_rejected(self):
        User.objects.create_user(username='newfac', email='newfac@cud.ac.ae',
                                 password=TEMP_PASSWORD)
        self.client.login(username='newfac@cud.ac.ae', password=TEMP_PASSWORD)

        response = self.client.post(CHANGE_URL, {'new_password1': 'short', 'new_password2': 'short'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'too short', response.content.lower())

    def test_successful_change_clears_the_flag_and_keeps_the_session(self):
        user = User.objects.create_user(username='newfac', email='newfac@cud.ac.ae',
                                        password=TEMP_PASSWORD)
        self.client.login(username='newfac@cud.ac.ae', password=TEMP_PASSWORD)

        response = self.client.post(CHANGE_URL, {'new_password1': NEW_PASSWORD,
                                                 'new_password2': NEW_PASSWORD})
        self.assertRedirects(response, '/', fetch_redirect_response=False)

        user.refresh_from_db()
        self.assertFalse(user.must_change_password)
        self.assertTrue(user.check_password(NEW_PASSWORD))

        # update_session_auth_hash kept them signed in.
        response = self.client.get('/projects/')
        self.assertNotEqual(response.get('Location'), CHANGE_URL)

    def test_existing_user_is_not_disturbed(self):
        user = User.objects.create_user(username='oldfac', email='oldfac@cud.ac.ae',
                                        password='Existing123!')
        User.objects.filter(pk=user.pk).update(must_change_password=False)
        self.client.login(username='oldfac@cud.ac.ae', password='Existing123!')

        response = self.client.get('/projects/')
        self.assertNotEqual(response.get('Location'), CHANGE_URL)

    def test_flagged_user_can_still_log_out(self):
        User.objects.create_user(username='stuck', email='stuck@cud.ac.ae', password=TEMP_PASSWORD)
        self.client.login(username='stuck@cud.ac.ae', password=TEMP_PASSWORD)

        self.assertIn(self.client.post('/logout/').status_code, (200, 302))
