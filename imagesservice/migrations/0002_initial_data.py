from django.db import migrations
from django.core.management import call_command


APP_NAME = 'imagesservice'


def insert_data(apps, schema_editor):
    call_command('loaddata', 'initial_data/initial_data.json', verbosity=2)


def reverse_func(apps, schema_editor):
    ThumbnailSize = apps.get_model(APP_NAME, 'ThumbnailSize')
    AccountTier = apps.get_model(APP_NAME, 'AccountTier')

    AccountTier.objects.all().delete()
    ThumbnailSize.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        (APP_NAME, '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_data, reverse_func)
    ]
