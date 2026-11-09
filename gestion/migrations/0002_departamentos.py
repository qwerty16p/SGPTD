from django.db import migrations


def inicializar(apps, schema_editor):
    departamento = apps.get_model("gestion", "Departamento")
    for nombre in ("Finanzas", "RRHH", "Ventas", "IT", "Mercadeo", "Legal", "Gerencia de País"):
        departamento.objects.get_or_create(nombre=nombre)


class Migration(migrations.Migration):
    dependencies = [("gestion", "0001_initial")]
    operations = [migrations.RunPython(inicializar, migrations.RunPython.noop)]
