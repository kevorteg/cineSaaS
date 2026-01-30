import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from cinegram.config import settings
from cinegram.handlers import start, archive_handler, video_handler, external_handler, search_handler

# Configure Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    if not settings.BOT_TOKEN:
        print("Error: BOT_TOKEN not found in environment variables.")
        return

    application = ApplicationBuilder().token(settings.BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start.start_command))
    application.add_handler(CommandHandler("search", search_handler.search_command))
    application.add_handler(CallbackQueryHandler(search_handler.handle_search_callback))
    
    # 1. Video Flow (Autonomous)
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, video_handler.video_entry))

    # 2. Archive.org Links (Specific regex or checks handled inside)
    # Note: archive_handler currently checks validates internally. 
    # To prevent overlap with generic links, we can filter by Regex here or just order them.
    # Archive handler is more specific, so check it first or use strict filter.
    # Let's use a regex filter for archive.org
    application.add_handler(MessageHandler(filters.Regex(r'archive\.org/details/'), archive_handler.handle_archive_link))

    # 3. Generic Links (Everything else starting with http)
    application.add_handler(MessageHandler(filters.Entity("url") | filters.Regex(r'^http'), external_handler.handle_external_link))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
