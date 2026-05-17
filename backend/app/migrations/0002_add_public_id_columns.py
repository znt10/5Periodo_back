from django.db import migrations


TABLES = [
    "app_loja",
    "app_produto",
    "app_pedido",
    "app_itempedido",
    "app_estoque",
]


def column_exists(connection, table, column):
    if connection.vendor == "mysql":
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = %s
                  AND COLUMN_NAME = %s
                """,
                [table, column],
            )
            return cursor.fetchone() is not None

    with connection.cursor() as cursor:
        existing_columns = connection.introspection.get_table_description(cursor, table)
    return any(existing_column.name == column for existing_column in existing_columns)


def uuid_sql(connection):
    if connection.vendor == "mysql":
        return "REPLACE(UUID(), '-', '')"
    return "LOWER(HEX(RANDOMBLOB(16)))"


def add_public_id_columns(apps, schema_editor):
    connection = schema_editor.connection
    with schema_editor.connection.cursor() as cursor:
        for table in TABLES:
            if not column_exists(connection, table, "public_id"):
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN public_id CHAR(32) NULL")
            cursor.execute(
                f"UPDATE {table} SET public_id = {uuid_sql(connection)} "
                "WHERE public_id IS NULL"
            )
            if connection.vendor == "mysql":
                cursor.execute(f"ALTER TABLE {table} MODIFY public_id CHAR(32) NOT NULL")


def remove_public_id_columns(apps, schema_editor):
    connection = schema_editor.connection
    with schema_editor.connection.cursor() as cursor:
        for table in TABLES:
            if column_exists(connection, table, "public_id"):
                cursor.execute(f"ALTER TABLE {table} DROP COLUMN public_id")


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_public_id_columns, remove_public_id_columns),
    ]
