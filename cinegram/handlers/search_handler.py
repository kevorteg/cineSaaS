from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests
import logging

logger = logging.getLogger(__name__)

# Reusing the existing ArchiveService if possible, but we need search capability.
# We'll add a helper here or extend ArchiveService. For simplicity and modularity, 
# since `services/archive_service` was simple get_metadata, let's add search logic here
# or ideally update ArchiveService. Let's update ArchiveService first?
# No, let's keep specific search logic here or in a separate function to avoid messing with approved files unless needed.
# Actually, ArchiveService is the best place. I'll add a search method there in a moment.

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Searches Internet Archive for movies.
    Usage: /search <query>
    """
    if not context.args:
        await update.message.reply_text("🔎 Usage: `/search name of movie`", parse_mode="Markdown")
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"🔎 Searching for: **{query}**...", parse_mode="Markdown")

    # Perform Search
    # We want: mediatype:movies AND (title:query OR description:query) AND (language:spanish OR language:Spanish)
    # The Internet Archive Advanced Search API is complex.
    # Simple query: https://archive.org/advancedsearch.php
    
    base_url = "https://archive.org/advancedsearch.php"
    
    # Constructing a robust Lucene query
    # Prioritize Spanish but don't strictly exclude if user searches specific native title? 
    # User asked for: "que este en español latino" as preference.
    # We can perform a query AND language:spanish first. If 0 results, try broader?
    # Let's try restrictive first.
    
    lucene_query = f"(title:({query}) OR description:({query})) AND mediatype:(movies)"
    # Note: Language metadata in IA is often messy ("Spanish", "spa", "es", "Spanish; Castilian").
    # We'll try to sort by relevance.
    
    params = {
        "q": lucene_query,
        "fl": ["identifier", "title", "year", "language"],
        "rows": 5,
        "output": "json",
        "sort": ["downloads desc"] # Sort by popularity usually gives better results than relevance for movies
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        docs = data.get('response', {}).get('docs', [])

        if not docs:
            await update.message.reply_text("❌ No results found on Internet Archive.")
            return

        # Build Keyboard
        keyboard = []
        for doc in docs:
            title = doc.get('title', 'Unknown')[:30] # Limit length
            year = doc.get('year', 'N/A')
            identifier = doc.get('identifier')
            
            # Using a callback data prefix 'PROCESS_' to identify selection
            keyboard.append([InlineKeyboardButton(f"🎬 {title} ({year})", callback_data=f"IA_{identifier}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("👇 Select a movie to publish:", reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text("❌ Error searching Internet Archive.")

async def handle_search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the selection of a search result."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if not data.startswith("IA_"):
        return

    identifier = data.split("IA_")[1]
    
    # Send a message pretending a link was sent, or call processing directly.
    # We'll trigger the archive processing.
    # We need to import handle_archive_link logic. 
    # Since handle_archive_link expects a Message update, we can't just call it easily with a CallbackQuery update without mocking.
    # Better to create a shared processing function in archive_handler or just construct a link and call it if we refactor.
    
    # Let's send a feedback message and reuse logic by constructing a fake message object or refactoring?
    # Refactoring `archive_handler` to `process_identifier` function is best practice.
    # But to avoid touching too many files, I will just call the 'logic' by constructing the URL and passing it?
    # Actually, sending a real message from the user context is dirty.
    
    await query.edit_message_text(f"✅ Selected: `https://archive.org/details/{identifier}`\nProcessing...", parse_mode="Markdown")
    
    # We need to bridge to archive_handler. 
    # I will import the processing logic. But `handle_archive_link` parses `update.message.text`.
    # Let's do a cheat: Create a new update object or simply refactor `archive_handler.py` slightly 
    # to separate `process_url(url, update, context)`.
    
    # Plan: Modify archive_handler.py to expose `process_archive_url(url, update, context)`.
    from cinegram.handlers.archive_handler import process_archive_item
    
    # We will construct a link
    url = f"https://archive.org/details/{identifier}"
    await process_archive_item(update, context, url)
