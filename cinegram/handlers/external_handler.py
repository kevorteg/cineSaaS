from telegram import Update
from telegram.ext import ContextTypes
from cinegram.services.tmdb_service import TmdbService
from cinegram.services.image_generator import ImageGenerator
from cinegram.handlers.publish_handler import send_publication
import logging

logger = logging.getLogger(__name__)

async def handle_external_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles generic links with manual metadata format:
    URL | TITLE | YEAR | GENRE (Optional)
    """
    text = update.message.text.strip()
    parts = [p.strip() for p in text.split('|')]

    if len(parts) < 2:
        await update.message.reply_text(
            "⚠️ Format for external links:\n"
            "`URL | Title | Year`\n"
            "Example: `https://example.com/video.mp4 | The Matrix | 1999`",
            parse_mode="Markdown"
        )
        return

    url = parts[0]
    title = parts[1]
    year = parts[2] if len(parts) > 2 else ""
    
    await update.message.reply_text(f"🔍 Processing: {title} ({year})...")

    # 1. Enhance with TMDB
    tmdb_data = None
    if title:
        tmdb_data = TmdbService.search_movie(title, year)

    # 2. Construct Metadata
    # Defaults
    description = "No description available."
    genre = "Cine"
    poster_url = None
    rating = "N/A"

    if tmdb_data:
        title = tmdb_data.get('title') or title
        if tmdb_data.get('release_date'):
            year = tmdb_data.get('release_date')[:4] or year
        description = tmdb_data.get('overview') or description
        if tmdb_data.get('poster_path'):
            poster_url = TmdbService.get_poster_url(tmdb_data.get('poster_path'))
        if tmdb_data.get('genre_ids'):
            genre = TmdbService.get_genres(tmdb_data['genre_ids'])
        if tmdb_data.get('vote_average'):
            rating = str(round(tmdb_data['vote_average'], 1))

    metadata = {
        "title": title,
        "year": year,
        "genre": genre,
        "language": "Unknown",
        "description": description,
        "poster_url": poster_url,
        "rating": rating,
        "video_link": url # Use the provided URL
    }

    # 3. Generate Image
    await update.message.reply_text("🎨 Generating poster...")
    try:
        if metadata.get('poster_url'):
            image_path = ImageGenerator.generate_poster(
                metadata['poster_url'],
                metadata['title'],
                metadata['description']
            )
        else:
            # TODO: Add logic to generate text-only poster if no image found?
            # For now, just warn.
            await update.message.reply_text("⚠️ No poster found on TMDB. Using placeholder?")
            # We could add a 'generate_text_poster' method, but for now let's rely on fallback or error.
            # actually ImageGenerator handles invalid URL by making a black placeholder, 
            # but we need a URL to trigger it.
            # Let's give it a dummy if none found so it makes a title card.
            image_path = ImageGenerator.generate_poster(
                "https://dummyimage.com/1920x1080/000/fff&text=No+Image", 
                metadata['title'], 
                metadata['description']
            )

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        await update.message.reply_text("❌ Image generation failed.")
        return

    # 4. Publish
    await update.message.reply_text("📤 Publishing...")
    await send_publication(update, context, metadata, image_path)
