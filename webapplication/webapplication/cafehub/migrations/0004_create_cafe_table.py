from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('cafehub', '0003_cafehubdatabase_delete_student'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cafe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('rating', models.FloatField(default=0.0)),
                ('address', models.TextField()),
                ('description', models.TextField(blank=True, null=True)),
                ('is_partner', models.BooleanField(default=False)),
                ('opening_hours', models.CharField(blank=True, max_length=100, null=True)),
                ('contact', models.CharField(blank=True, max_length=15, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cafes', to='cafehub.vendor')),
            ],
            options={
                'db_table': 'cafehub_cafe',
                'ordering': ['-rating'],
            },
        ),
    ]