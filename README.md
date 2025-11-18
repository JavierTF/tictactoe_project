# TicTacToe - Django

Juego de TicTacToe (Tres en Raya) implementado con Django.

## 📋 Características

- ✅ Juego local para dos jugadores
- ✅ Interfaz simple y responsive
- ✅ Backend robusto con Django 5.0
- ✅ Arquitectura limpia y escalable
- ✅ Juego completamente en el navegador

## 🛠️ Tecnologías

- **Backend**: Django 5.0
- **Base de datos**: SQLite
- **Frontend**: JavaScript Vanilla, CSS Grid
- **Arquitectura**: Pensado inicialmente para que fuera online y escalable, pero llevado a versión simple.

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
6. Haz clic en "🔄 Nueva Partida" para jugar de nuevo

## 🔐 Panel de Administración

*Pensado inicialmente para una versión online, pero simplificado.*

El panel de administración permite gestionar el sistema.

**Acceso:**
- URL: http://127.0.0.1:8000/admin/
- Credenciales: Las que creaste con `createsuperuser`

**Funcionalidades:**
- Gestión de partidas de TicTacToe
- Gestión de usuarios del sistema

## 🌐 Despliegue (Producción)

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

## 📁 Estructura del Proyecto
```
tictactoe_project/
├── apps/game/              # Aplicación principal
├── config/                 # Configuración Django
├── requirements/           # Dependencias
├── static/                 # Archivos estáticos
├── templates/              # Templates globales
├── manage.py
└── README.md
```

## 👤 Autor

**Javier Torres**

- GitHub: [@JavierTF](https://github.com/JavierTF)
- Repositorio: [tictactoe_project](https://github.com/JavierTF/tictactoe_project)

---

Proyecto desarrollado como prueba técnica demostrando conocimientos en Django, Python y buenas prácticas de desarrollo.