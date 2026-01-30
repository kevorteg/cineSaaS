import os
from telegram import Update
from telegram.ext import ContextTypes
from cinegram.config import settings

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message with verification."""
    user = update.effective_user
    
    # Verify Channel Access
    channel_status = "✅ **Conectado y listo**"
    try:
        # We need to know the bot's ID. context.bot.id is available.
        bot_member = await context.bot.get_chat_member(chat_id=settings.CHANNEL_ID, user_id=context.bot.id)
        if bot_member.status not in ['administrator', 'creator']:
             channel_status = "⚠️ **Alerta:** El bot NO es administrador en el canal. No podré publicar."
    except Exception as e:
        channel_status = f"❌ **Error:** No puedo acceder al canal `{settings.CHANNEL_ID}`.\n(Asegúrate de agregar al bot como Admin)"

    caption = (
        f"👋 ¡Hola {user.first_name}! **Soy Cinegram Bot** 🤖\n\n"
        "🎥 **¿Qué hago por ti?**\n"
        "Acomodo, edito los metadatos y envío tus películas automáticamente al canal, "
        "dejándolas listas con portada y calidad profesional.\n\n"
        "📡 **Verificación de Canal**:\n"
        f"🎯 Destino: `{settings.CHANNEL_ID}`\n"
        f"🔌 Estado: {channel_status}\n\n"
        "👇 **¿Cómo usarme?**\n"
        "1️⃣ **Reenvía un video** de otro canal.\n"
        "2️⃣ **Envía un Link** de Internet Archive o genérico.\n"
        "3️⃣ **Usa** `/search Nombre` para buscar películas.\n\n"
        "🚀 *¡Manos a la obra!*"
    )

    # Path to image
    image_path = os.path.join(settings.ASSETS_DIR, "portada bot", "portada.avif")
    
    try:
        if os.path.exists(image_path):
            # Convert AVIF/Image to PNG compatible stream
            from PIL import Image
            from io import BytesIO
            
            with Image.open(image_path) as img:
                bio = BytesIO()
                bio.name = 'welcome.png'
                img.save(bio, 'PNG')
                bio.seek(0)
                await update.message.reply_photo(photo=bio, caption=caption, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"⚠️ No encontré la imagen de portada en `{image_path}`\n\n{caption}", parse_mode="Markdown")
    except Exception as e:
        # Fallback to text
        await update.message.reply_text(caption, parse_mode="Markdown")
