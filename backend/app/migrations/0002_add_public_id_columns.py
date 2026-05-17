from django.db import migrations


TABLES = [
    "app_loja",
    "app_produto",
    "app_pedido",
    "app_itempedido",
    "app_estoque",
]


def add_public_id_columns(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        for table in TABLES:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN public_id CHAR(32) NULL")
            cursor.execute(
                f"UPDATE {table} SET public_id = REPLACE(UUID(), '-', '') "
                "WHERE public_id IS NULL"
            )
            cursor.execute(f"ALTER TABLE {table} MODIFY public_id CHAR(32) NOT NULL")
            cursor.execute(f"ALTER TABLE {table} ADD UNIQUE (public_id)")


def remove_public_id_columns(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        for table in TABLES:
            cursor.execute(f"ALTER TABLE {table} DROP COLUMN public_id")


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_public_id_columns, remove_public_id_columns),
    ]
