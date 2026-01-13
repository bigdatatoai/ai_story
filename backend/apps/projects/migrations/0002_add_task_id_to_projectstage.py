# Generated migration for adding task_id field to ProjectStage model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectstage',
            name='task_id',
            field=models.CharField(blank=True, db_index=True, default='', max_length=255, verbose_name='Celery任务ID'),
        ),
    ]
