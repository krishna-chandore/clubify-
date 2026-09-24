from django.db import migrations, models
from clubapp.models import generate_unique_admin_key


def encrypt_existing_keys(apps, schema_editor):
    from clubapp.admin_key_crypto import encrypt_admin_key
    Club = apps.get_model('clubapp', 'Club')
    for club in Club.objects.all().iterator():
        if club.admin_key and not club.admin_key.startswith('enc$'):
            if club.admin_key.startswith(('pbkdf2_', 'argon2$', 'bcrypt')):
                continue
            club.admin_key = encrypt_admin_key(club.admin_key)
            club.save(update_fields=['admin_key'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [('clubapp', '0012_alter_contact_email'),]
    operations = [
        migrations.AlterField(
            model_name='club',
            name='admin_key',
            field=models.CharField(max_length=256, default=generate_unique_admin_key),
        ),
        migrations.RunPython(encrypt_existing_keys, noop_reverse),
    ]
