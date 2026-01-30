from guessit import guessit
import logging

logger = logging.getLogger(__name__)

class FilenameParser:
    
    @staticmethod
    def parse_filename(filename: str):
        """
        Parses a messy filename and returns a clean dictionary with title and year.
        Example: 'Night.of.the.Living.Dead.1968.720p.mkv' -> {'title': 'Night of the Living Dead', 'year': '1968'}
        """
        try:
            # Pre-cleaning: Remove explicit spam before Guessit
            import re
            
            # 1. Remove @usernames (e.g. @cesser16)
            clean_name = re.sub(r'@\w+', '', filename)
            
            # 2. Remove URLs
            clean_name = re.sub(r'https?://\S+|www\.\S+', '', clean_name)
            
            # 3. Remove other common spam if needed
            clean_name = clean_name.replace('_', ' ') # Replace underscores
            
            # Strategy 1: Cleaned Name (Anti-Spam)
            data = guessit(clean_name)
            title = data.get('title')
            year = data.get('year')

            # Strategy 2: Original Name (Fallback if Cleaned fails)
            if not title:
                logger.warning(f"Strategy 1 failed for '{filename}'. Trying original...")
                data_orig = guessit(filename)
                title = data_orig.get('title')
                year = data_orig.get('year') or year # Keep year if found in strategy 1

            # Strategy 3: Raw Filename (Last Resort)
            if not title:
                logger.warning(f"Strategy 2 failed for '{filename}'. Using raw filename.")
                # Remove extension and basic separators to make a searchable title
                base = filename.rsplit('.', 1)[0]
                title = base.replace('.', ' ').replace('_', ' ').strip()
            
            # Final Validation
            if not title:
                return None
                
            return {
                "title": title,
                "year": str(year) if year else None
            }
            
        except Exception as e:
            logger.error(f"Error parsing filename {filename}: {e}")
            return None
