from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Club, Event
from .admin_key_crypto import decrypt_admin_key


PNG_1X1 = __import__('base64').b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M/wHwAF/gL+JwAAAABJRU5ErkJggg=='
)


def image_file(name='banner.png'):
    return SimpleUploadedFile(name, PNG_1X1, content_type='image/png')


class ClubifySecurityTests(TestCase):
    def setUp(self):
        self.admin_one = User.objects.create_user(
            username='admin1@example.com',
            email='admin1@example.com',
            password='StrongPass123!',
        )
        self.admin_two = User.objects.create_user(
            username='admin2@example.com',
            email='admin2@example.com',
            password='StrongPass123!',
        )
        self.club_one = Club.objects.create(
            name='Club One',
            description='Club one',
            admin_name='Admin One',
            admin_user=self.admin_one,
        )
        self.club_two = Club.objects.create(
            name='Club Two',
            description='Club two',
            admin_name='Admin Two',
            admin_user=self.admin_two,
        )
        self.event_two = Event.objects.create(
            club=self.club_two,
            title='Private Event',
            description='Private event',
            date_time='2030-01-01T12:00:00Z',
            banner=image_file(),
            created_by=self.admin_two,
            is_approved=True,
        )

    def test_admin_cannot_delete_another_clubs_event(self):
        self.client.force_login(self.admin_one)
        response = self.client.post('/home/', {
            'delete_event': '1',
            'event_id': self.event_two.id,
        })

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Event.objects.filter(pk=self.event_two.pk).exists())

    def test_unapproved_event_detail_is_not_public(self):
        self.event_two.is_approved = False
        self.event_two.save(update_fields=['is_approved'])
        self.client.force_login(self.admin_one)

        response = self.client.get(f'/event/{self.event_two.id}/')

        self.assertEqual(response.status_code, 404)

    def test_admin_key_is_encrypted_and_verified(self):
        self.club_one.admin_key = 'admin-secret'
        self.club_one.save(update_fields=['admin_key'])

        self.assertTrue(self.club_one.admin_key.startswith('enc$'))
        response = self.client.post(
            reverse('club_admin_login'),
            {
                'username': self.admin_one.username,
                'password': 'password123',
                'admin_key': 'admin-secret',
            },
        )
        self.assertRedirects(response, reverse('home'))

    def test_admin_key_recovery_emails_existing_key(self):
        self.club_one.admin_key = 'admin-secret'
        self.club_one.save(update_fields=['admin_key'])

        response = self.client.post(
            reverse('club_admin_login'),
            {'recover_key': '1', 'recovery_email': self.admin_one.email},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('admin-secret', mail.outbox[0].body)
        self.assertEqual(self.club_one.admin_key.startswith('enc$'), True)

    def test_admin_key_can_be_edited_from_admin_form(self):
        from clubapp.admin import ClubAdminForm

        form = ClubAdminForm(
            instance=self.club_one,
            data={
                'name': self.club_one.name,
                'slug': self.club_one.slug,
                'description': self.club_one.description,
                'mission': self.club_one.mission,
                'past_events': self.club_one.past_events,
                'admin_name': self.club_one.admin_name,
                'admin_user': self.admin_one.pk,
                'admin_key': 'changed-secret',
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        club = form.save()
        self.assertEqual(decrypt_admin_key(club.admin_key), 'changed-secret')

    def test_wrong_admin_key_does_not_crash(self):
        self.club_one.admin_key = 'admin-secret'
        self.club_one.save(update_fields=['admin_key'])
        response = self.client.post(
            reverse('club_admin_login'),
            {
                'username': self.admin_one.username,
                'password': 'password123',
                'admin_key': 'wrong-key',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid admin credentials.')
