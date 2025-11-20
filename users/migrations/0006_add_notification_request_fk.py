from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_create_notification'),
        ('requests_app', '0003_laundryrequest_service_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='related_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='requests_app.laundryrequest'),
        ),
    ]
