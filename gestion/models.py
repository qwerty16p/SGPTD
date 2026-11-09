from django.db import models
from django.db.models.functions import Lower


class Ficha(models.Model):
    nombre = models.CharField(max_length=140)
    descripcion = models.TextField("Descripción", blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Departamento(Ficha):
    activo = models.BooleanField(default=True)

    class Meta(Ficha.Meta):
        constraints = [models.UniqueConstraint(Lower("nombre"), name="departamento_unico")]


class Aplicacion(Ficha):
    departamentos = models.ManyToManyField(Departamento, through="DepartamentoAplicacion",
                                          related_name="aplicaciones")

    class Meta(Ficha.Meta):
        constraints = [models.UniqueConstraint(Lower("nombre"), name="aplicacion_unica")]


class DepartamentoAplicacion(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    aplicacion = models.ForeignKey(Aplicacion, on_delete=models.PROTECT)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["aplicacion__nombre"]
        constraints = [models.UniqueConstraint(fields=["departamento", "aplicacion"],
                                               name="asignacion_unica")]
