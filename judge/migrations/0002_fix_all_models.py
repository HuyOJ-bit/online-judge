from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    initial = True # Hoặc False nếu đã có 0001_initial, nhưng nếu bạn gom lại thì chỉnh dependencies trỏ đúng.

    dependencies = [
        ('judge', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contests', to='judge.group', verbose_name='Thuộc nhóm'),
        ),
        migrations.AddField(
            model_name='contest',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Người tạo'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contest',
            name='is_visible',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='contest',
            name='penalty_minutes',
            field=models.PositiveIntegerField(default=20, help_text='Penalty minutes added per wrong try before the AC.'),
        ),
        migrations.AddField(
            model_name='contest',
            name='problems',
            field=models.ManyToManyField(blank=True, related_name='contests', to='judge.problem', verbose_name='Bài tập trong cuộc thi'),
        ),
    ]
