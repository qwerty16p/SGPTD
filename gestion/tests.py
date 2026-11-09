from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from .models import Departamento, Aplicacion, DepartamentoAplicacion


class DirectorioTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user("prueba")
        cls.it = Departamento.objects.get(nombre="IT")
        cls.fin = Departamento.objects.get(nombre="Finanzas")
        cls.ventas = Departamento.objects.get(nombre="Ventas")

    def setUp(self):
        self.client.force_login(self.usuario)

    def post(self, ruta, args, **datos):
        return self.client.post(reverse(ruta, args=args), datos, follow=True)

    def asignar(self, area, **datos):
        return self.post("asociar", ["departamentos", area.pk], **datos)

    def test_departamentos(self):
        self.assertSetEqual(set(Departamento.objects.values_list("nombre", flat=True)),
                            {"Finanzas", "RRHH", "Ventas", "IT", "Mercadeo", "Legal", "Gerencia de País"})
        for nombre in ["  Diseño   Web ", "DISEÑO WEB", " "]:
            self.post("crear", ["departamentos"], nombre=nombre, activo="on")
        self.assertEqual(Departamento.objects.count(), 8)
        area = Departamento.objects.get(nombre="Diseño Web")
        self.post("editar", ["departamentos", area.pk], nombre="Diseño", descripcion="Equipo")
        area.refresh_from_db()
        self.assertFalse(area.activo)
        self.assertEqual(area.descripcion, "Equipo")
        self.assertContains(self.client.get("/gestion/departamentos/?q=Diseño"), "Consultar Diseño")

    def test_catalogo(self):
        for nombre in ["Microsoft Excel", "Microsoft Outlook", "SAN", " microsoft   EXCEL ", "  "]:
            self.post("crear", ["aplicaciones"], nombre=nombre)
        self.assertEqual(Aplicacion.objects.count(), 3)
        app = Aplicacion.objects.get(nombre="SAN")
        self.post("editar", ["aplicaciones", app.pk], nombre="SAN", descripcion="Actualizada")
        listado = self.client.get("/gestion/aplicaciones/?q=SAN")
        self.assertContains(listado, "Actualizada")
        self.assertNotContains(listado, "Outlook")
        self.post("eliminar", [app.pk])
        self.assertFalse(Aplicacion.objects.filter(pk=app.pk).exists())

    def test_asociaciones(self):
        self.asignar(self.fin, nombre="Microsoft Excel")
        app = Aplicacion.objects.get()
        self.post("asociar", ["aplicaciones", app.pk], departamento=self.it.pk)
        self.asignar(self.it, nombre=" microsoft   EXCEL ")
        self.assertEqual(app.departamentos.count(), 2)
        self.assertEqual(Aplicacion.objects.count(), 1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            DepartamentoAplicacion.objects.create(departamento=self.it, aplicacion=app)
        detalle = self.client.get(reverse("detalle", args=["aplicaciones", app.pk]))
        for area in [self.fin, self.it]:
            self.assertContains(detalle, reverse("detalle", args=["departamentos", area.pk]))
        self.post("eliminar", [app.pk])
        self.post("quitar", [self.fin.pk, app.pk])
        self.assertEqual(list(app.departamentos.all()), [self.it])
        self.assertEqual(Aplicacion.objects.count(), 1)

    def test_creacion_desde_ventas(self):
        respuesta = self.asignar(self.ventas, nombre="CRM", descripcion="Ventas")
        self.assertContains(respuesta, "CRM")
        self.assertEqual(self.ventas.aplicaciones.get(), Aplicacion.objects.get(nombre="CRM"))
        self.assertNotContains(self.client.get(respuesta.request["PATH_INFO"], {"q": "ZZZ"}), ">CRM</a>")
        self.assertContains(self.client.get("/"), "CRM")

    def test_validaciones(self):
        self.it.activo = False
        self.it.save()
        self.asignar(self.it, nombre="Prueba")
        self.asignar(self.fin, aplicacion=999999)
        self.asignar(self.fin, nombre=" ")
        self.assertFalse(Aplicacion.objects.exists())
        app = Aplicacion.objects.create(nombre="Prueba")
        for valor in [999999, "x", self.it.pk]:
            self.post("asociar", ["aplicaciones", app.pk], departamento=valor)
        self.assertFalse(DepartamentoAplicacion.objects.exists())

    def test_autenticacion(self):
        self.post("logout", [])
        for ruta in ["/", "/gestion/departamentos/", "/gestion/aplicaciones/crear/"]:
            self.assertEqual(self.client.get(ruta).status_code, 302)
        self.assertContains(self.client.get("/ingresar/"), "Iniciar sesión")
