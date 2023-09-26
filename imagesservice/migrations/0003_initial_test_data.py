from django.db import migrations
from django.core.management import call_command


APP_NAME = 'imagesservice'


def insert_data(apps, schema_editor):
    call_command('loaddata', 'initial_data/initial_test_data.json', verbosity=2)


def reverse_func(apps, schema_editor):
    Users = apps.get_model('auth.user')    
    Users.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        (APP_NAME, '0002_initial_data'),
    ]

    operations = [
        migrations.RunPython(insert_data, reverse_func)
    ]
