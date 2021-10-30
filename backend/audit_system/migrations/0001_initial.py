# Generated by Django 3.2.8 on 2021-10-30 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_id', models.CharField(editable=False, max_length=50, null=True)),
                ('request_status_current', models.CharField(choices=[('request_draft', 'Request Drafted'), ('requested', 'Consent Requested to landlord'), ('approved_by_landlord', 'Approved by landlord'), ('rejected_by_landlord', 'Rejected by landlord'), ('rejected_by_system', 'Rejected by system'), ('failed_due_to_limit_reach_of_landlord', 'Landlord has reached his limit of issuing consent ! Auto rejection'), ('updated', 'Aadhaar Details Updated')], max_length=150, null=True)),
                ('ip', models.TextField(default='NOT RECORDED', null=True)),
                ('ip_details', models.TextField(default='{}', null=True)),
                ('is_requester', models.BooleanField(null=True)),
                ('message', models.TextField(null=True)),
                ('error', models.TextField(null=True)),
                ('is_error', models.BooleanField(null=True)),
                ('event_timestamp', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
    ]