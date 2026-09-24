from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('clubapp', '0011_secure_admin_key_and_upload_validation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(max_length=122),
        ),
    ]
