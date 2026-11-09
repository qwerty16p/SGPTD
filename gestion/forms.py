from django import forms
from .models import Aplicacion, Departamento


def normalizar(nombre):
    return " ".join(nombre.split())


def existente(modelo, nombre, excluir=None):
    for obj in modelo.objects.exclude(pk=excluir).only("nombre"):
        if normalizar(obj.nombre).casefold() == normalizar(nombre).casefold():
            return obj


class FormFicha(forms.ModelForm):
    def clean_nombre(self):
        nombre = normalizar(self.cleaned_data["nombre"])
        if existente(self._meta.model, nombre, self.instance.pk):
            raise forms.ValidationError("Ya existe un registro con ese nombre.")
        return nombre


class FormAplicacion(FormFicha):
    class Meta:
        model = Aplicacion
        fields = ["nombre", "descripcion"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}


class FormDepartamento(FormAplicacion):
    class Meta(FormAplicacion.Meta):
        model = Departamento
        fields = ["nombre", "descripcion", "activo"]
