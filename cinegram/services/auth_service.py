import json
import os
import logging
from cinegram.config import settings

logger = logging.getLogger(__name__)

class AuthService:
    WHITELIST_FILE = os.path.join(settings.ASSETS_DIR, "whitelist.json")

    @staticmethod
    def _load_whitelist():
        if not os.path.exists(AuthService.WHITELIST_FILE):
            return []
        try:
            with open(AuthService.WHITELIST_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading whitelist: {e}")
            return []

    @staticmethod
    def _save_whitelist(whitelist):
        try:
            with open(AuthService.WHITELIST_FILE, 'w') as f:
                json.dump(whitelist, f)
        except Exception as e:
            logger.error(f"Error saving whitelist: {e}")

    @staticmethod
    def is_authorized(user_id: int) -> bool:
        # 1. Admin is always authorized
        if user_id == settings.ADMIN_ID:
            return True
            
        # 2. Check whitelist
        whitelist = AuthService._load_whitelist()
        return user_id in whitelist

    @staticmethod
    def authorize_user(user_id: int):
        whitelist = AuthService._load_whitelist()
        if user_id not in whitelist:
            whitelist.append(user_id)
            AuthService._save_whitelist(whitelist)
            logger.info(f"User {user_id} authorized.")
