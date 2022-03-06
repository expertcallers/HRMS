# Generated by Django 4.0.2 on 2022-03-05 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ams', '0002_employeeleavebalance'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentActiveStatusHist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emp_id', models.CharField(blank=True, max_length=20, null=True)),
                ('emp_name', models.CharField(blank=True, max_length=30, null=True)),
                ('current_status', models.CharField(blank=True, max_length=20, null=True)),
                ('new_status', models.CharField(blank=True, max_length=20, null=True)),
                ('date', models.DateField()),
                ('reason', models.TextField()),
                ('changed_by', models.CharField(max_length=30)),
                ('approved_by', models.CharField(max_length=50)),
                ('hr_response', models.TextField(blank=True, null=True)),
                ('status_by_hr', models.CharField(max_length=50)),
                ('ticket_status', models.BooleanField(default=False)),
            ],
        ),
    ]
