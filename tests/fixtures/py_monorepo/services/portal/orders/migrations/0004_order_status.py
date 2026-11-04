from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("orders", "0003_backfill_totals")]
    operations = [migrations.AddField("order", "status", None)]
