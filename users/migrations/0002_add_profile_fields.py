from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='mobile_number',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(upload_to='profile_pics/', null=True, blank=True),
        ),
    ]
