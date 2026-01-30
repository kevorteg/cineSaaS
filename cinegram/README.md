# Cinegram Bot 🎬

Bot de Telegram para la automatización de publicaciones de películas de dominio público desde Internet Archive.

## 📋 Características

- **Entrada**: Acepta enlaces de Internet Archive (`https://archive.org/details/...`).
- **Generación de Posters**: Crea imágenes Full HD (1920x1080) con título y sinopsis superpuestos.
- **Publicación Automatizada**: Envía la imagen generada seguida de la información de la película.
- **Integración Social**: Botón para redirigir a Instagram.
- **Open Source**: Código modular y limpio.

## 🚀 Instalación

1.  **Clonar el repositorio** (o descargar los archivos):
    ```bash
    git clone https://github.com/tu-usuario/cinegram.git
    cd cinegram
    ```

2.  **Crear entorno virtual** (Recomendado):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuración**:
    - Copia el archivo `.env.example` a `.env`:
      ```bash
      cp .env.example .env # O hazlo manualmente
      ```
    - Edita `.env` y añade tu `BOT_TOKEN` de Telegram y otros ajustes.

## 🏃‍♂️ Uso

1.  Inicia el bot:
    ```bash
    python bot.py
    ```
2.  En Telegram, envía `/start` al bot.
3.  Envía un enlace de una película de Internet Archive (ej: `https://archive.org/details/NightOfTheLivingDead`).
4.  El bot responderá con:
    - Poster generado con título y sinopsis.
    - Mensaje con metadatos (Año, Género, Idioma) y enlace al video.

## ⚠️ Aviso Legal

Este software está diseñado para trabajar exclusivamente con contenido de **Dominio Público** (Public Domain). El usuario es responsable de verificar los derechos de autor del material que procesa.

## 🛠️ Estructura del Proyecto

```
cinegram/
├── bot.py                  # Punto de entrada
├── config/                 # Configuraciones
├── handlers/               # Gestores de comandos y mensajes
├── services/               # Lógica de negocio (Archive API, Imagenes)
├── utils/                  # Ayudantes generales
└── assets/                 # Recursos (Fuentes, Plantillas)
```
