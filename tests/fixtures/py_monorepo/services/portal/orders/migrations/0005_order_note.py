from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("orders", "0004_order_status")]
    operations = [migrations.AddField("order", "note", None)]
