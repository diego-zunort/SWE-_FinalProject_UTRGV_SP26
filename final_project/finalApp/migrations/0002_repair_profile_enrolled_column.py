# Generated manually to repair older local SQLite databases after migration squashing.

from django.db import migrations


def add_missing_enrolled_column(apps, schema_editor):
    Profile = apps.get_model("finalApp", "Profile")
    table_name = Profile._meta.db_table

    with schema_editor.connection.cursor() as cursor:
        existing_columns = {
            column.name
            for column in schema_editor.connection.introspection.get_table_description(
                cursor,
                table_name,
            )
        }

    if "enrolled" in existing_columns:
        return

    schema_editor.add_field(Profile, Profile._meta.get_field("enrolled"))


class Migration(migrations.Migration):
    dependencies = [
        ("finalApp", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_missing_enrolled_column, migrations.RunPython.noop),
    ]
