from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=254, null=True, blank=True)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('read', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='users.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
