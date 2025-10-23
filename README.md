# SENA Booking

## Descripción

SENA Booking es una plataforma web diseñada para facilitar la búsqueda y reserva de vuelos. El sistema proporciona una interfaz intuitiva que permite a los usuarios buscar vuelos disponibles, realizar reservaciones, procesar pagos de manera simulada y generar tiquetes en formato PDF para su conveniencia.

## Características Principales

- Búsqueda intuitiva de vuelos disponibles
- Sistema de reservas en tiempo real
- Simulación de procesamiento de pagos
- Generación y descarga de tiquetes en formato PDF
- Gestión de reservas de usuario
- Interfaz responsiva y amigable al usuario
- Panel de administración para gestión de vuelos

## Tecnologías Utilizadas

- Python
- Django (Framework web)
- TailwindCSS (CDN)
- Docker
- HTML5/CSS3
- JavaScript
- Postgresql

## Instalación

### Prerrequisitos

- Python (3.8 o superior)
- Docker y Docker Compose
- Git
- Pip (Gestor de paquetes de Python)

### Pasos de Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/dum4hx/prueba_senasoft.git
   cd prueba_senasoft
   ```

2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate

   # Linux MacOs
    source venv/bin/activate  
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecutar migraciones:
   ```bash
   python manage.py migrate
   ```

## Configuración

1. Copiar el archivo de configuración de ejemplo:
   ```bash
   cp .env.example .env
   ```

2. Abrir el archivo `.env` y reemplazar los valores de ejemplo con la configuración real:
   - SECRET_KEY
   - DATABASE_URL
   - DEBUG
   - ALLOWED_HOSTS

## Uso

1. Iniciar el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

2. Acceder a la aplicación en `http://localhost:8000`

## Estructura del Proyecto

```
├── App/                    # Aplicación principal
│   ├── static/            # Archivos estáticos
│   ├── templates/         # Plantillas HTML
│   ├── models.py          # Modelos de datos
│   └── views.py           # Vistas de la aplicación
├── Proyecto/              # Configuración del proyecto
└── manage.py             # Script de gestión de Django
```

## Despliegue

Para desplegar con Docker:

```bash
docker-compose up -d --build
```

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) en el repositorio para más detalles.

## Autores

- Julian Alzate Monzalve
- Santiago Duque Ordoñez

## Agradecimientos

Extendemos nuestro sincero agradecimiento a SENASOFT y a Fragma por su invaluable apoyo en el desarrollo de este proyecto. Su provisión de recursos, infraestructura y espacios de trabajo ha sido fundamental para hacer posible esta iniciativa.
