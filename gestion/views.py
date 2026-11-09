from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import FormAplicacion, FormDepartamento, existente, normalizar
from .models import Aplicacion, Departamento, DepartamentoAplicacion as Asignacion


def departamentos():
    return Departamento.objects.annotate(total=Count("aplicaciones"))


@login_required
def inicio(request):
    areas = departamentos()
    metrics = [("Departamentos", areas.count()), ("Aplicaciones", Aplicacion.objects.count()),
               ("Asignaciones", Asignacion.objects.count()), ("Departamentos sin aplicaciones", areas.filter(total=0).count())]
    return render(request, "inicio.html", {"areas": areas, "metrics": metrics,
                  "recientes": Aplicacion.objects.order_by("-creado")[:5]})


def formulario(tipo):
    if tipo == "departamentos":
        return FormDepartamento
    if tipo == "aplicaciones":
        return FormAplicacion
    raise Http404


@login_required
def lista(request, tipo):
    formulario(tipo)
    q = request.GET.get("q", "").strip()
    items = departamentos() if tipo == "departamentos" else Aplicacion.objects.prefetch_related("departamentos")
    return render(request, "lista.html", {"tipo": tipo, "items": items.filter(nombre__icontains=q), "q": q})


@login_required
@transaction.atomic
def editar(request, tipo, pk=None):
    cls = formulario(tipo)
    obj = get_object_or_404(cls._meta.model, pk=pk) if pk else None
    form = cls(request.POST if request.method == "POST" else None, instance=obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, "Cambios guardados.")
        return redirect("detalle", tipo, obj.pk)
    return render(request, "form.html", {"form": form, "obj": obj, "tipo": tipo})


@login_required
def detalle(request, tipo, pk):
    obj = get_object_or_404(formulario(tipo)._meta.model, pk=pk)
    ctx = {"obj": obj, "tipo": tipo}
    if tipo == "departamentos":
        q = request.GET.get("q", "").strip()
        ctx.update(q=q, filas=Asignacion.objects.filter(departamento=obj, aplicacion__nombre__icontains=q)
                   .select_related("aplicacion"), disponibles=Aplicacion.objects.exclude(departamentos=obj))
    else:
        ctx["disponibles"] = Departamento.objects.filter(activo=True).exclude(aplicaciones=obj)
    return render(request, "detalle.html", ctx)


@login_required
@require_POST
@transaction.atomic
def asociar(request, tipo, pk):
    obj = get_object_or_404(formulario(tipo)._meta.model, pk=pk)
    destino = redirect("detalle", tipo, pk)
    area = obj if tipo == "departamentos" else Departamento.objects.filter(pk=id_post(request, "departamento")).first()
    if not area or not area.activo:
        messages.error(request, "Seleccione un departamento activo.")
        return destino
    if tipo == "aplicaciones":
        app = obj
    elif "aplicacion" in request.POST:
        app = Aplicacion.objects.filter(pk=id_post(request, "aplicacion")).first()
        if not app:
            messages.error(request, "Seleccione una aplicación del catálogo.")
            return destino
    else:
        nombre = normalizar(request.POST.get("nombre", ""))
        app = existente(Aplicacion, nombre)
        if not app:
            form = FormAplicacion(request.POST)
            if not form.is_valid():
                messages.error(request, "Ingrese un nombre de entre 1 y 140 caracteres.")
                return destino
            app = form.save()
    _, nueva = Asignacion.objects.get_or_create(departamento=area, aplicacion=app)
    messages.info(request, "Aplicación agregada." if nueva else "La aplicación ya está en este departamento.")
    return destino


def id_post(request, campo):
    valor = request.POST.get(campo, "")
    return int(valor) if valor.isascii() and valor.isdigit() and len(valor) <= 18 else None


@login_required
@require_POST
def quitar(request, pk, app):
    area = get_object_or_404(Departamento, pk=pk)
    borradas, _ = Asignacion.objects.filter(departamento=area, aplicacion_id=app).delete()
    messages.info(request, "Aplicación retirada del departamento." if borradas else "La asociación ya no existe.")
    return redirect("detalle", "departamentos", pk)


@login_required
@require_POST
@transaction.atomic
def eliminar(request, pk):
    app = get_object_or_404(Aplicacion, pk=pk)
    if app.departamentos.exists():
        messages.error(request, "Quite primero las asociaciones de esta aplicación.")
        return redirect("detalle", "aplicaciones", pk)
    app.delete()
    messages.success(request, "Aplicación eliminada del catálogo.")
    return redirect("lista", "aplicaciones")
