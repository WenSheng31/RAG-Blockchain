from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("knowledge", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="keyword",
            name="definition",
            field=models.TextField(blank=True, verbose_name="定義"),
        ),
    ]
