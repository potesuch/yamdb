# Generated by Django 3.2.23 on 2024-02-29 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='confirmation_code',
            field=models.CharField(max_length=12, null=True, verbose_name='Код подтверждения'),
        ),
    ]
