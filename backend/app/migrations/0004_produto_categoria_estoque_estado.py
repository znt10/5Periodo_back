from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0003_notificacao"),
    ]

    operations = [
        migrations.AddField(
            model_name="produto",
            name="categoria",
            field=models.CharField(
                choices=[
                    ("SALGADOS_GDE", "Salgados grande"),
                    ("SALGADOS_MINI", "Salgados mini"),
                    ("ESFIHAS_GDE", "Esfihas grande"),
                    ("ESFIHAS_MINI", "Esfihas mini"),
                    ("RECHEIOS", "Recheios"),
                    ("MERCADO", "Mercado"),
                ],
                default="MERCADO",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="estoque",
            name="estado",
            field=models.CharField(
                choices=[
                    ("NORMAL", "Normal"),
                    ("CONGELADO", "Congelado"),
                    ("RESFRIADO", "Resfriado"),
                ],
                default="NORMAL",
                max_length=20,
            ),
        ),
    ]
