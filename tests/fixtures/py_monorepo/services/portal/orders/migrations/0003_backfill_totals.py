from django.db import migrations


def forwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("orders", "0002_order_total")]
    operations = [migrations.RunPython(forwards)]
