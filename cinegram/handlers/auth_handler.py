from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from cinegram.services.auth_service import AuthService
from cinegram.config import settings
from functools import wraps

# --- Decorator ---
def auth_required(func):
    """Decorator to restrict access to authorized users only."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if AuthService.is_authorized(user_id):
            return await func(update, context, *args, **kwargs)
        else:
            await send_access_denied(update, context)
    return wrapper

async def send_access_denied(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the paywall/login message."""
    user = update.effective_user
    text = (
        f"⛔ **Acceso Denegado**\n\n"
        f"Hola {user.first_name}, este bot es privado.\n"
        "Para usarlo, necesitas desbloquear tu acceso.\n\n"
        "🔓 **Opciones:**\n"
        "1. 🔑 **Contraseña:** Si la tienes, escríbela tal cual en el chat.\n"
        "2. ⭐ **Pagar:** Compra acceso de por vida con Estrellas."
    )
    
    # Invoice Button (Stars)
    # Note: Telegram Stars invoices use 'XTR' currency
    prices = [LabeledPrice("Acceso Vitalicio", settings.STARS_PRICE)] 
    
    await update.message.reply_invoice(
        title="Acceso CineGram Bot",
        description="Desbloquea todas las funciones del bot para siempre.",
        payload="cinegram_access_v1",
        provider_token="", # Empty for Stars
        currency="XTR",
        prices=prices,
        start_parameter="pay_access"
    )

# --- Handlers ---

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checks if the user sent the correct password."""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # If already authorized, ignore (let other handlers handle it? No, middleware logic needed in bot.py)
    # This handler matches TEXT, so it might conflict if not careful.
    # But if we use a specific filter in bot.py (Filters.TEXT & ~Authorized), it works.
    
    if AuthService.is_authorized(user_id):
        return # Should assume next handler picks it up, but in python-telegram-bot we might need grouping.
               # Simpler: This handler is only added for unauthorized users? 
               # Or we check explicitly.
        pass

    if text == settings.ACCESS_PASSWORD:
        AuthService.authorize_user(user_id)
        await update.message.reply_text("✅ **¡Acceso Concedido!**\nBienvenido a CineGram. Usa /start para comenzar.")
    else:
        # Optional: Don't reply to everything to avoid spam, or reply generic.
        # But for password attempt, we should reply.
        await update.message.reply_text("❌ Contraseña incorrecta.")

# --- Payment Handlers ---

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Answers the PreCheckoutQuery."""
    query = update.pre_checkout_query
    if query.invoice_payload != "cinegram_access_v1":
        await query.answer(ok=False, error_message="Payload error")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirms successful payment."""
    user_id = update.effective_user.id
    AuthService.authorize_user(user_id)
    await update.message.reply_text("🌟 **¡Pago Recibido!**\n\nTu acceso ha sido desbloqueado permanentemente. ¡Disfruta CineGram!")
