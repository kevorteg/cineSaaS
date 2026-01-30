from typing import Dict, Optional

class MetadataParser:
    @staticmethod
    def parse(data: dict, tmdb_data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Parses raw IA metadata into a standardized dictionary.
        Optionally merges with TMDB data (TMDB takes precedence for text/image).
        """
        if not data or 'metadata' not in data:
            return None

        metadata = data['metadata']
        files = data.get('files', [])
        server = data.get('server')
        dir_path = data.get('dir')

        # 1. Base IA Data
        ia_title = metadata.get("title", "Unknown Title")
        ia_year = metadata.get("date", "Unknown Year")[:4]
        ia_description = metadata.get("description", "No description available.")
        
        # 2. Extract IA Image (Improved Fallback)
        poster_path = None
        # Priority 1: Specifically marked images
        for f in files:
            if f.get('format') in ['JPEG', 'PNG', 'Thumbnail'] and 'thumb' not in f.get('name', '').lower():
                poster_path = f['name']
                break
        
        # Priority 2: Item Image default
        if not poster_path:
             for f in files:
                if f.get('format') == 'Item Image':
                    poster_path = f['name']
                    break
        
        # Priority 3: Any JPEG/PNG that isn't a spectrogram or xml
        if not poster_path:
            for f in files:
                name = f.get('name', '').lower()
                if (name.endswith('.jpg') or name.endswith('.png')) and 'spectrogram' not in name:
                    poster_path = f['name']
                    break

        ia_poster_url = f"https://{server}{dir_path}/{poster_path}" if poster_path and server and dir_path else None

        # 3. Merge with TMDB (if available)
        final_title = ia_title
        final_year = ia_year
        final_genre = metadata.get("subject", "Unknown Genre")
        final_description = ia_description
        final_poster_url = ia_poster_url
        rating = "N/A"

        if tmdb_data:
            final_title = tmdb_data.get('title') or final_title
            if tmdb_data.get('release_date'):
                final_year = tmdb_data.get('release_date')[:4]
            final_description = tmdb_data.get('overview') or final_description
            if tmdb_data.get('poster_path'):
                # TMDB posters are high quality, prefer them
                from cinegram.services.tmdb_service import TmdbService
                final_poster_url = TmdbService.get_poster_url(tmdb_data['poster_path'])
            
            # Genres from TMDB are IDs, we need to convert them (handled in service usually, but let's assume we passed raw)
            # Or assume service passed friendly names. 
            # In our service implementation we added get_genres helper but returned raw dict.
            # Let's use the helper here if we can import it, or just rely on IA subject if complex.
            # Actually, let's just use IA subject as fallback if TMDB genre is missing/complex to parse here.
            from cinegram.services.tmdb_service import TmdbService
            if tmdb_data.get('genre_ids'):
                 final_genre = TmdbService.get_genres(tmdb_data['genre_ids'])
            
            if tmdb_data.get('vote_average'):
                rating = str(round(tmdb_data['vote_average'], 1))

        return {
            "title": final_title,
            "year": final_year,
            "genre": final_genre,
            "language": metadata.get("language", "Unknown"),
            "description": final_description,
            "poster_url": final_poster_url,
            "rating": rating
        }
