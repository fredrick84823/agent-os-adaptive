from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("orders", "0001_initial")]
    operations = [migrations.AddField("order", "total", None)]
