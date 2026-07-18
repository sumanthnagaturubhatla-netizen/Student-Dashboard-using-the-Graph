# Generated migration for adding is_active field to Student model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_refreshtoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Check to allow student access'),
        ),
    ]
