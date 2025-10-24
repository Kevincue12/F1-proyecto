API F1 - Pilotos, Escuderías y Grandes Premios

Este proyecto es una API desarrollada con FastAPI y SQLAlchemy que permite gestionar información del mundo de la Fórmula 1, incluyendo pilotos, escuderías, grandes premios y resultados, además de generar reportes automáticos en Excel.

Características principales

Gestión de Escuderías

Crear, listar, editar y eliminar escuderías.

Cada escudería puede tener máximo 2 pilotos.

Gestión de Pilotos

Crear, listar, editar y eliminar pilotos.

Validación automática del número único de piloto.

Asociación de pilotos con sus respectivas escuderías.

Gestión de Grandes Premios

Registrar Grandes Premios con fecha obligatoria.

Consultar la lista de Grandes Premios creados.

Registro de Resultados

Asignar posiciones a pilotos en cada Gran Premio.

Ver tabla de resultados por cada GP.

Controla duplicados (no se repiten pilotos o posiciones en un mismo GP).

Campeonato de Pilotos

Calcula los puntos acumulados según las posiciones:

Posición	Puntos
1	25
2	18
3	15
4	12
5	10
6	8
7	6
8	4
9	2
10	1

Generación de Reportes Excel

Exporta datos de escuderías, pilotos, grandes premios, resultados y tabla del campeonato.

Archivo generado automáticamente como reportes_f1.xlsx.

Tecnologías utilizadas

Python 3.11+

FastAPI — Framework principal para la API.

SQLAlchemy — ORM para la gestión de base de datos.

SQLite — Base de datos ligera local.

Pandas — Para generación de reportes en Excel.

Uvicorn — Servidor ASGI para ejecutar la API.

Instalación y ejecución
Clonar el repositorio
git clone https://github.com/Kevincue12/F1-proyecto
cd api-f1

Crear y activar entorno virtual
python -m venv venv
source venv/Scripts/activate  # En Windows

source venv/bin/activate      # En Linux/Mac

Instalar dependencias
pip install -r requirements.txt

Ejecutar el servidor
uvicorn main:app --reload

Endpoints principales
Recurso	Método	Ruta	Descripción
Escuderías	POST	/escuderias/	Crear escudería
Escuderías	GET	/escuderias/	Listar escuderías
Escuderías	PUT	/escuderias/{id}	Editar escudería
Escuderías	DELETE	/escuderias/{id}	Eliminar escudería
Pilotos	POST	/pilotos/	Crear piloto
Pilotos	GET	/pilotos/	Listar pilotos
Pilotos	GET	/pilotos/numero/{numero}	Buscar por número
Pilotos	PUT	/pilotos/{id}	Editar piloto
Pilotos	DELETE	/pilotos/{id}	Eliminar piloto
Grandes Premios	POST	/grandes_premios/	Crear Gran Premio
Grandes Premios	GET	/grandes_premios/	Listar Grandes Premios
Resultados	POST	/resultados/	Agregar resultado
Resultados	GET	/resultados/gp/{id}	Ver resultados de un GP
Campeonato	GET	/campeonato/pilotos	Tabla del campeonato
Reportes	GET	/reportes/	Generar y descargar Excel


Estructura del proyecto
api-f1/
│
├── main.py                 # Punto de entrada principal (endpoints)
├── crud.py                 # Funciones CRUD de la lógica del negocio
├── models.py               # Modelos ORM (tablas de la base de datos)
├── schemas.py              # Modelos Pydantic (validación y respuestas)
├── database.py             # Configuración de conexión a la base de datos
├── requirements.txt        # Dependencias del proyecto
└── reportes_f1.xlsx        # (Se genera automáticamente)

Ejemplo de creación de Gran Premio (JSON)
{
  "nombre": "Gran Premio de México",
  "pais": "México",
  "fecha": "2025-11-02"
}


Generación de reportes

Para generar los reportes en Excel, simplemente accede a:

GET /reportes/


El archivo reportes_f1.xlsx incluirá hojas con:

Escuderías

Pilotos

Grandes Premios

Resultados

Campeonato de Pilotos

Autor

Kevin Cuevas
Estudiante de Ingeniería de Sistemas — Universidad Católica de Colombia
Materia: Desarrollo de Software

Licencia

Este proyecto fue desarrollado con fines académicos.
Puedes usarlo y modificarlo libremente para fines educativos o de práctica.