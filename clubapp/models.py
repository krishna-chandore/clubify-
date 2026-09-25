import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from cloudinary_storage.storage import VideoMediaCloudinaryStorage

from .admin_key_crypto import encrypt_admin_key


MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_MEDIA_SIZE = 20 * 1024 * 1024
MAX_RESOURCE_SIZE = 10 * 1024 * 1024


def validate_file_size(uploaded_file, max_size):
    if uploaded_file and uploaded_file.size > max_size:
        raise ValidationError(
            f'File size must be {max_size // (1024 * 1024)} MB or smaller.'
        )


def validate_image_size(uploaded_file):
    validate_file_size(uploaded_file, MAX_IMAGE_SIZE)


def validate_media_size(uploaded_file):
    validate_file_size(uploaded_file, MAX_MEDIA_SIZE)


def validate_resource_size(uploaded_file):
    validate_file_size(uploaded_file, MAX_RESOURCE_SIZE)


def generate_unique_admin_key():
    return encrypt_admin_key(uuid.uuid4().hex)


class Contact(models.Model):
    name = models.CharField(max_length=122)
    email = models.EmailField(max_length=122)
    phone = models.CharField(max_length=12)
    message = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.email


class Club(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    mission = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='club_images/',
        blank=True,
        null=True,
        validators=[validate_image_size],
    )
    past_events = models.TextField(blank=True, help_text='Add each event on a new line.')
    admin_name = models.CharField(max_length=100)
    admin_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='administered_clubs',
    )
    admin_key = models.CharField(max_length=256, default=generate_unique_admin_key)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.admin_key:
            self.admin_key = encrypt_admin_key(self.admin_key)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.memberships.count()

    @property
    def upcoming_events_count(self):
        return self.events.filter(date_time__gte=timezone.now()).count()


class ClubMembership(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='club_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('club', 'user')

    def __str__(self):
        return f'{self.user.username} → {self.club.name}'


class ClubGalleryMedia(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='gallery_media')
    file = models.FileField(
        upload_to='club_gallery/',
        storage=VideoMediaCloudinaryStorage(),
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    'jpg', 'jpeg', 'png', 'gif', 'webp',
                    'mp4', 'webm', 'mov'
                ]
            ),
            validate_media_size,
        ],
    )

    def __str__(self):
        return f'{self.club.name} - {self.file.name}'


class ClubResource(models.Model):
    club = models.ForeignKey(Club, related_name='resources', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='resources/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt']
            ),
            validate_resource_size,
        ],
    )
    link = models.URLField(blank=True, null=True)

    def clean(self):
        if not self.file and not self.link:
            raise ValidationError('Add either a resource file or a resource link.')

    def __str__(self):
        return self.title


class Event(models.Model):
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='events',
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_time = models.DateTimeField()
    banner = models.ImageField(upload_to='event_banners/', validators=[validate_image_size])
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return self.title

