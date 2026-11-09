# Directorio de Aplicaciones por Departamento

Aplicación local de Django y SQLite para registrar aplicaciones una sola vez y consultar qué áreas las utilizan. El ZIP incluye Bootstrap 5, JavaScript, las dependencias de Python y una base inicial con siete departamentos, sin usuarios ni aplicaciones de ejemplo.

## Primera ejecución en Windows

Instale Python 3.10 o superior compatible con Django 5.2. Descomprima el ZIP en una carpeta con permisos de escritura. Abra PowerShell en la carpeta que contiene manage.py y ejecute:

~~~powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index --find-links vendor -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver --insecure
~~~

Elija su nombre de usuario y contraseña. Al escribir la contraseña, la terminal oculta los caracteres. Abra http://127.0.0.1:8000/ e inicie sesión. Mantenga la terminal abierta mientras usa el directorio. La opción --insecure permite que el servidor de desarrollo sirva el CSS y el JavaScript locales con DEBUG desactivado. Este modo de ejecución es para uso en la propia computadora.

En macOS o Linux, cree el entorno con python3 -m venv .venv y sustituya .\.venv\Scripts\python.exe por .venv/bin/python en los pasos siguientes.

## Volver a levantar el servidor

Desde la misma carpeta, ejecute únicamente:

~~~powershell
.\.venv\Scripts\python.exe manage.py runserver --insecure
~~~

Ctrl+C detiene el servidor. Si olvidó su contraseña, use el siguiente comando cambiando NOMBRE por su usuario:

~~~powershell
.\.venv\Scripts\python.exe manage.py changepassword NOMBRE
~~~

## Cómo usar el directorio

- En Inicio se muestran los cuatro indicadores, las áreas y las cinco aplicaciones más recientes.
- En Departamentos puede crear un área, buscarla, editarla o desactivarla. Un área inactiva conserva sus asociaciones y deja de admitir nuevas.
- Abra Finanzas u otra área y pulse **+ Agregar aplicación**. Busque y seleccione una ficha del catálogo o despliegue **Crear una aplicación**. Si escribe un nombre existente, se reutiliza su ficha. La descripción de esa ficha se edita desde el catálogo.
- **Quitar** elimina solo la asociación con el área actual.
- En Aplicaciones puede buscar, editar o consultar en qué departamentos se utiliza cada ficha. Desde su detalle también puede agregarla a otro departamento activo. Solo se puede eliminar una ficha sin asociaciones.

## Actualizar desde SGPTD y conservar datos

El paquete original distribuido no contenía db.sqlite3. Si ya trabajó con SGPTD, detenga el servidor anterior y guarde una copia completa de su carpeta. Descomprima esta versión **en otra carpeta**. Antes de ejecutar migrate, copie allí su db.sqlite3 anterior, sustituyendo la base inicial del ZIP. Conserve también .local-key si existe. Instale las dependencias y ejecute migrate. Puede usar su usuario anterior.

La migración conserva departamentos, aplicaciones, fechas y usuarios. Convierte los accesos activos cuyo permiso era distinto de «Sin acceso» en una asociación por pareja y conserva la primera fecha disponible. Normaliza los espacios de los nombres y detiene la migración si encuentra nombres ambiguos o vacíos. Corríjalos en la versión anterior y repita la actualización desde la copia. Los cargos opcionales, módulos, perfiles, auditoría y campos técnicos quedan disponibles en su respaldo anterior. Para volver a esa versión, restaure la carpeta completa previa a la actualización.

## Respaldar y restaurar

1. Detenga el servidor con Ctrl+C y cierre cualquier otra aplicación que esté usando la base.
2. Copie db.sqlite3 a una carpeta segura con la fecha del respaldo. El archivo contiene el catálogo, las asociaciones y las cuentas locales. Conserve también el proyecto y su archivo .local-key.
3. Para restaurar, detenga el servidor, guarde una copia de la base actual y coloque el respaldo en la carpeta de manage.py con el nombre db.sqlite3. Use una versión del proyecto compatible con el respaldo.
4. Ejecute migrate y vuelva a iniciar el servidor.

## Pruebas

Ejecute los siguientes comandos dentro del entorno virtual. La suite usa una base temporal.

~~~powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
~~~

Las pruebas cubren departamentos, edición, búsqueda, catálogo, asociación en ambas direcciones, retiro, protección contra duplicados, eliminación y autenticación. Las migraciones se encuentran en gestion/migrations. La restricción de la tabla intermedia protege la combinación de departamento y aplicación.
