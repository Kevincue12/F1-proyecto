 🏎️ API F1 - Pilotos, Escuderías y Grandes Premios

Autor: Kevin Cuevas  
Universidad Católica de Colombia
Materia: Desarrollo de Software  

---

Descripción General

Este proyecto es una API REST desarrollada con FastAPI y SQLAlchemy que permite gestionar información del mundo de la Fórmula 1, incluyendo pilotos, escuderías, grandes premios y resultados, además de generar reportes automáticos en Excel.

El objetivo es demostrar la correcta implementación de relaciones entre modelos, persistencia de datos, reglas de negocio y la interacción completa mediante los métodos HTTP (GET, POST, PUT, PATCH, DELETE).

---

Características principales

Gestión de Escuderías
- Crear, listar, editar y eliminar escuderías.
- Cada escudería puede tener máximo 2 pilotos.

Gestión de Pilotos
- Crear, listar, editar y eliminar pilotos.
- Validación automática del número único de piloto.
- Asociación de pilotos con sus respectivas escuderías.

Gestión de Grandes Premios
- Registrar grandes premios.
- Consultar la lista de grandes premios creados.

Registro de Resultados
- Asignar posiciones a pilotos en cada gran premio.
- Control de duplicados (no se repiten pilotos o posiciones en un mismo GP).
- Ver tabla de resultados por cada GP.

 Campeonato de Pilotos
Calcula los puntos acumulados según las posiciones:

| Posición | Puntos |
|-----------|---------|
| 1 | 25 |
| 2 | 18 |
| 3 | 15 |
| 4 | 12 |
| 5 | 10 |
| 6 | 8 |
| 7 | 6 |
| 8 | 4 |
| 9 | 2 |
| 10 | 1 |

Generación de Reportes Excel
- Exporta datos de escuderías, pilotos, grandes premios, resultados y tabla del campeonato.  
- Archivo generado automáticamente como **`reportes_f1.xlsx`**.

---

 Relaciones entre modelos

| Relación | Tipo | Descripción |
|-----------|------|-------------|
| Escudería → Pilotos | 1:N | Una escudería puede tener hasta dos pilotos |
| Piloto ↔ Grandes Premios | N:M | Un piloto puede participar en varios grandes premios |
| Piloto → PerfilPiloto | 1:1 | Cada piloto tiene un perfil único |

---
Mapa de Endpoints

 Endpoints de Pilotos

| Método | Endpoint | Descripción | Parámetros | Ejemplo |
|--------|-----------|-------------|-------------|----------|
| GET | `/pilotos` | Obtiene todos los pilotos registrados | — | `/pilotos` |
| GET | `/pilotos/{id}` | Consulta un piloto por su ID | `id: int` | `/pilotos/3` |
| POST | `/pilotos` | Crea un nuevo piloto | JSON (nombre, nacionalidad, escuderia_id) | — |
| PUT | `/pilotos/{id}` | Actualiza un piloto completo | `id: int` + JSON | `/pilotos/2` |
| PATCH | `/pilotos/{id}` | Actualiza parcialmente un piloto | `id: int` | `/pilotos/5` |
| DELETE | `/pilotos/{id}` | Borrado lógico del piloto | `id: int` | `/pilotos/4` |

 Endpoints de Escuderías

| Método | Endpoint | Descripción | Parámetros | Ejemplo |
|--------|-----------|-------------|-------------|----------|
| GET | `/escuderias` | Lista todas las escuderías | — | `/escuderias` |
| GET | `/escuderias/{id}` | Muestra una escudería con sus pilotos | `id: int` | `/escuderias/1` |
| POST | `/escuderias` | Crea una nueva escudería | JSON (nombre, país, año_fundación) | — |
| PUT | `/escuderias/{id}` | Actualiza una escudería | `id: int` + JSON | `/escuderias/2` |
| PATCH | `/escuderias/{id}` | Actualización parcial | `id: int` | `/escuderias/3` |
| DELETE | `/escuderias/{id}` | Borrado lógico de la escudería | `id: int` | `/escuderias/1` |

 Endpoints de Grandes Premios

| Método | Endpoint | Descripción | Parámetros | Ejemplo |
|--------|-----------|-------------|-------------|----------|
| GET | `/grandes_premios` | Lista todos los grandes premios | — | `/grandes_premios` |
| GET | `/grandes_premios/{id}` | Muestra información de un GP | `id: int` | `/grandes_premios/5` |
| POST | `/grandes_premios` | Crea un nuevo GP (fecha obligatoria) | JSON (nombre, país, fecha) | — |
| PUT | `/grandes_premios/{id}` | Modifica un GP | `id: int` + JSON | `/grandes_premios/2` |
| DELETE | `/grandes_premios/{id}` | Elimina un GP | `id: int` | `/grandes_premios/3` |

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



Generación de reportes

Para generar los reportes en Excel, simplemente accede a:

GET /reportes/


El archivo reportes_f1.xlsx incluirá hojas con:

Escuderías

Pilotos

Grandes Premios

Resultados

Campeonato de Pilotos


Este proyecto fue desarrollado con fines académicos.
Puedes usarlo y modificarlo libremente para fines educativos o de práctica.