from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('cafehub', '0004_create_cafe_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='cafe',
            name='cafe_type',
            field=models.CharField(default='vendor', max_length=50),
            preserve_default=False,
        ),
    ]