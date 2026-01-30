from telegram import Update
from telegram.ext import ContextTypes
from cinegram.utils import helpers
from cinegram.services.archive_service import ArchiveService
from cinegram.services.metadata_parser import MetadataParser
from cinegram.services.image_generator import ImageGenerator
from cinegram.handlers.publish_handler import send_publication
import logging

logger = logging.getLogger(__name__)

async def handle_archive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles incoming messages that contain Internet Archive links.
    """
    text = update.message.text
    await process_archive_item(update, context, text)

async def process_archive_item(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    """
    Shared logic to process an IA URL (from message or search callback).
    """
    # 1. Validate URL
    if not helpers.is_valid_archive_url(url):
        # Only reply error if it came from a direct message, 
        # but here we assume 'url' passed is either from valid search or message.
        if update.message:
            await update.message.reply_text("❌ Please send a valid Internet Archive URL.")
        return

    # Reply target: Message or Callback Message
    message = update.message or update.callback_query.message
    await message.reply_text("🔍 Fetching metadata...")

    # 2. Extract Identifier
    identifier = helpers.extract_identifier(url)
    if not identifier:
        await message.reply_text("❌ Could not extract identifier from URL.")
        return

    # 3. Fetch Metadata
    data = ArchiveService.get_metadata(identifier)
    if not data:
        await message.reply_text("❌ Failed to fetch data from Internet Archive.")
        return

    # 4. Enhance with TMDB (Optional)
    from cinegram.services.tmdb_service import TmdbService
    tmdb_data = None
    
    # Try to find title/year from IA data first to search TMDB
    ia_title = data.get('metadata', {}).get('title')
    ia_date = data.get('metadata', {}).get('date', '')[:4]
    
    if ia_title:
        await message.reply_text(f"🎬 Searching TMDB for: {ia_title}...")
        tmdb_data = TmdbService.search_movie(ia_title, ia_date)

    # 5. Parse Metadata (Merge IA + TMDB)
    metadata = MetadataParser.parse(data, tmdb_data)
    if not metadata:
        await message.reply_text("❌ Could not parse metadata.")
        return

    # Add video link (simple construction)
    metadata['video_link'] = f"https://archive.org/details/{identifier}"
    
    # 6. Generate Image
    await message.reply_text("🎨 Generating poster...")
    try:
        if metadata.get('poster_url'):
            image_path = ImageGenerator.generate_poster(
                metadata['poster_url'],
                metadata['title'],
                metadata['description']
            )
        else:
            await message.reply_text("⚠️ No cover image found to generate poster.")
            return
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        await message.reply_text("❌ Image generation failed.")
        return

    # 7. Publish
    await message.reply_text("📤 Publishing...")
    
    # send_publication expects 'update' to get chat_id. 
    # Use helper that can handle both or extraction?
    # send_publication uses `update.effective_chat.id` which works for both Message and CallbackQuery updates.
    await send_publication(update, context, metadata, image_path)

