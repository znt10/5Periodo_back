from django.db import migrations, models


def normalizar_unidades(apps, schema_editor):
    Produto = apps.get_model("app", "Produto")
    mapa = {
        "un": "UNIDADE",
        "unidade": "UNIDADE",
        "kg": "QUILO",
        "quilo": "QUILO",
        "l": "LITRO",
        "litro": "LITRO",
        "cx": "CAIXA",
        "caixa": "CAIXA",
        "pct": "PACOTE",
        "pacote": "PACOTE",
        "g": "QUILO",
        "ml": "LITRO",
    }

    for produto in Produto.objects.all():
        unidade = (produto.unidade_medida or "").strip().lower()
        produto.unidade_medida = mapa.get(unidade, "UNIDADE")
        produto.save(update_fields=["unidade_medida"])


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0005_add_fogazzas_categoria"),
    ]

    operations = [
        migrations.RunPython(normalizar_unidades, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="produto",
            name="unidade_medida",
            field=models.CharField(
                choices=[
                    ("UNIDADE", "Unidade"),
                    ("CAIXA", "Caixa"),
                    ("PACOTE", "Pacote"),
                    ("QUILO", "Quilo"),
                    ("LITRO", "Litro"),
                ],
                default="UNIDADE",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="produto",
            name="quantidade_por_embalagem",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="produto",
            name="estoque_minimo_sugerido",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
