from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0004_produto_categoria_estoque_estado"),
    ]

    operations = [
        migrations.AlterField(
            model_name="produto",
            name="categoria",
            field=models.CharField(
                choices=[
                    ("SALGADOS_GDE", "Salgados grande"),
                    ("SALGADOS_MINI", "Salgados mini"),
                    ("ESFIHAS_GDE", "Esfihas grande"),
                    ("ESFIHAS_MINI", "Esfihas mini"),
                    ("FOGAZZAS_GDE", "Fogazzas grande"),
                    ("FOGAZZAS_MINI", "Fogazzas mini"),
                    ("RECHEIOS", "Recheios"),
                    ("MERCADO", "Mercado"),
                ],
                default="MERCADO",
                max_length=30,
            ),
        ),
    ]
