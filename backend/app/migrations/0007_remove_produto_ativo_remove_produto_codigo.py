from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0006_produto_unidade_estoque_minimo"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="produto",
            name="ativo",
        ),
        migrations.RemoveField(
            model_name="produto",
            name="codigo",
        ),
    ]
