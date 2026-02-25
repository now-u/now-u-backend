from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    help = "Reset PostgreSQL sequences for all models to fix duplicate key errors"

    def add_arguments(self, parser):
        parser.add_argument(
            "--app",
            type=str,
            help="Only reset sequences for a specific app (e.g. --app causes)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print SQL without executing it",
        )

    def handle(self, *args, **options):
        app_filter = options.get("app")
        dry_run = options.get("dry_run")

        all_models = apps.get_models()

        if app_filter:
            all_models = [
                m for m in all_models
                if m._meta.app_label == app_filter
            ]

        if not all_models:
            self.stdout.write(self.style.WARNING("No models found."))
            return

        with connection.cursor() as cursor:
            for model in all_models:
                table = model._meta.db_table

                # Only process models with an integer auto primary key
                pk = model._meta.pk
                if pk is None or pk.get_internal_type() not in (
                    "AutoField", "BigAutoField", "SmallAutoField"
                ):
                    continue

                pk_col = pk.column

                sql = f"""
                    SELECT setval(
                        pg_get_serial_sequence('{table}', '{pk_col}'),
                        COALESCE((SELECT MAX({pk_col}) FROM "{table}"), 1)
                    );
                """

                if dry_run:
                    self.stdout.write(sql.strip())
                else:
                    try:
                        cursor.execute(sql)
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Reset sequence for {table}")
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"✗ Skipped {table}: {e}")
                        )

        if not dry_run:
            self.stdout.write(self.style.SUCCESS("\nAll sequences reset successfully."))
