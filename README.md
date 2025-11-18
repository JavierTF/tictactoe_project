# TicTacToe - Django

Juego de TicTacToe (Tres en Raya) implementado con Django como prueba técnica.

## 📋 Características

- ✅ Juego local para dos jugadores (misma computadora)
- ✅ Interfaz simple y responsive
- ✅ Sin necesidad de login para jugar
- ✅ Panel de administración para gestionar partidas
- ✅ Backend robusto con Django 5.0
- ✅ Arquitectura limpia y escalable

## 🚀 Demo

![TicTacToe Screenshot](screenshot.png)

## 🛠️ Tecnologías

- **Backend**: Django 5.0
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: HTML5, CSS Grid, JavaScript Vanilla
- **Estilos**: CSS Puro
- **Testing**: Pytest

## 📦 Instalación

### Requisitos previos

- Python 3.11+
- Git

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/JavierTF/tictactoe_project.git
cd tictactoe_project
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements/development.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
```

Edita `.env` si necesitas cambiar alguna configuración.

5. **Ejecutar migraciones**
```bash
python manage.py migrate
```

6. **Crear superusuario (para acceder al admin)**
```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear tu usuario administrador.

7. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

8. **Abrir en el navegador**

Visita: http://127.0.0.1:8000/

## 🎮 Cómo jugar

1. Abre http://127.0.0.1:8000/ en tu navegador
2. El juego comienza automáticamente con el jugador X
3. Haz clic en una casilla para colocar tu símbolo
4. El turno alterna automáticamente entre X y O
5. El juego termina cuando hay un ganador o empate
6. Haz clic en "Nueva Partida" para jugar de nuevo

## 🔐 Panel de Administración

El panel de administración permite gestionar las partidas guardadas en la base de datos.

**Acceso:**
- URL: http://127.0.0.1:8000/admin/
- Credenciales: Las que creaste con `createsuperuser`

**Funcionalidades:**
- Ver historial de partidas
- Ver tablero visual de cada partida
- Gestionar usuarios
- Ver estadísticas

## 📁 Estructura del Proyecto
```
tictactoe_project/
├── apps/
│   └── game/                   # Aplicación principal
│       ├── migrations/         # Migraciones de base de datos
│       ├── templates/          # Templates HTML
│       │   └── game/
│       │       └── simple_game.html
│       ├── tests/              # Tests
│       ├── admin.py            # Configuración del admin
│       ├── models.py           # Modelos (Game, Move)
│       ├── views.py            # Vistas
│       ├── services.py         # Lógica de negocio
│       ├── serializers.py      # Serializers (API)
│       └── urls.py             # URLs de la app
│
├── config/                     # Configuración del proyecto
│   ├── settings/               # Settings modulares
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py                 # URLs principales
│   ├── asgi.py                 # ASGI config
│   └── wsgi.py                 # WSGI config
│
├── requirements/               # Dependencias
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── static/                     # Archivos estáticos
├── templates/                  # Templates globales
├── .env.example                # Variables de entorno ejemplo
├── .gitignore
├── manage.py
└── README.md
```

## 🧪 Testing

Ejecutar todos los tests:
```bash
pytest
```

Ejecutar tests con cobertura:
```bash
pytest --cov=apps --cov-report=html
```

Ver reporte de cobertura:
```bash
# En Windows
start htmlcov/index.html

# En Linux/Mac
open htmlcov/index.html
```

## 🎨 Code Quality

El proyecto incluye herramientas de calidad de código:
```bash
# Formatear código
black .

# Ordenar imports
isort .

# Linting
flake8

# Type checking
mypy .
```

## 📊 Modelos de Base de Datos

### Game
Representa una partida de TicTacToe.

**Campos:**
- `id` (UUID): Identificador único
- `player1` (FK User): Jugador 1 (X)
- `player2` (FK User): Jugador 2 (O)
- `status`: Estado (waiting, in_progress, finished, draw)
- `board` (JSON): Estado del tablero
- `current_turn`: Turno actual (X/O)
- `winner` (FK User): Ganador
- `created_at`, `updated_at`, `finished_at`: Timestamps

### Move
Representa un movimiento en una partida.

**Campos:**
- `id` (UUID): Identificador único
- `game` (FK Game): Partida asociada
- `player` (FK User): Jugador que hizo el movimiento
- `position` (int): Posición en el tablero (0-8)
- `symbol` (char): Símbolo (X/O)
- `created_at`: Timestamp

## 🌐 Despliegue

### Variables de entorno necesarias
```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=tudominio.com
DB_NAME=nombre_db
DB_USER=usuario_db
DB_PASSWORD=contraseña_db
DB_HOST=host_db
DB_PORT=5432
```

### Comandos de producción
```bash
# Colectar archivos estáticos
python manage.py collectstatic --noinput

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar con gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Buenas Prácticas Implementadas

- ✅ Configuración modular (base, development, production)
- ✅ Variables de entorno para secrets
- ✅ Modelos con UUIDs para IDs públicos
- ✅ Custom managers para queries comunes
- ✅ Separación de lógica de negocio (services)
- ✅ Validadores personalizados
- ✅ Admin personalizado con visualización de tablero
- ✅ Testing setup completo
- ✅ Code quality tools configuradas
- ✅ Requirements separados por entorno
- ✅ .gitignore apropiado
- ✅ Documentación completa

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la [MIT License](LICENSE).

## 👤 Autor

**Javier Torres**

- GitHub: [@JavierTF](https://github.com/JavierTF)
- Repositorio: [tictactoe_project](https://github.com/JavierTF/tictactoe_project)

## 🙏 Agradecimientos

Proyecto desarrollado como prueba técnica demostrando conocimientos en:
- Django y Python
- Arquitectura de software
- Buenas prácticas de desarrollo
- Testing
- Despliegue de aplicaciones web

---

**¿Preguntas o sugerencias?** Abre un issue en GitHub.