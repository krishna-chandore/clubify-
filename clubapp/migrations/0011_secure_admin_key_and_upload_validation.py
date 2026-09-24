from django.contrib.auth.hashers import make_password
from django.db import migrations, models
from django.core.validators import FileExtensionValidator
import clubapp.models


def hash_existing_admin_keys(apps, schema_editor):
    Club = apps.get_model('clubapp', 'Club')
    for club in Club.objects.all().iterator():
        key = club.admin_key
        if key and not key.startswith('$'):
            club.admin_key = make_password(key)
            club.save(update_fields=['admin_key'])


def reverse_hash_existing_admin_keys(apps, schema_editor):
    # Password hashes cannot be converted back to the original admin keys.
    # Keep the hashed value if this migration is reversed.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('clubapp', '0010_alter_club_admin_user_alter_event_club_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='admin_key',
            field=models.CharField(
                default=clubapp.models.generate_unique_admin_key,
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name='club',
            name='image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='club_images/',
                validators=[clubapp.models.validate_image_size],
            ),
        ),
        migrations.AlterField(
            model_name='clubgallerymedia',
            name='file',
            field=models.FileField(
                upload_to='club_gallery/',
                validators=[
                    FileExtensionValidator(
                        allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'mov']
                    ),
                    clubapp.models.validate_media_size,
                ],
            ),
        ),
        migrations.AlterField(
            model_name='clubresource',
            name='file',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='resources/',
                validators=[
                    FileExtensionValidator(
                        allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt']
                    ),
                    clubapp.models.validate_resource_size,
                ],
            ),
        ),
        migrations.AlterField(
            model_name='event',
            name='banner',
            field=models.ImageField(
                upload_to='event_banners/',
                validators=[clubapp.models.validate_image_size],
            ),
        ),
        migrations.RunPython(hash_existing_admin_keys, reverse_hash_existing_admin_keys),
    ]
