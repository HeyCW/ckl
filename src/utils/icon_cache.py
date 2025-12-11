"""
Icon/Logo Caching System
Menghindari loading dan resize berulang kali untuk performa lebih baik
"""

from PIL import Image, ImageTk

class IconCache:
    """Singleton cache untuk icon/logo aplikasi"""

    _instance = None
    _cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IconCache, cls).__new__(cls)
        return cls._instance

    def get_icon(self, path="assets/logo.jpg", size=(32, 32)):
        """
        Get cached icon atau load jika belum ada

        Args:
            path: Path ke file icon
            size: Tuple (width, height) untuk resize

        Returns:
            ImageTk.PhotoImage object atau None jika error
        """
        cache_key = f"{path}_{size[0]}x{size[1]}"

        # Return dari cache jika sudah ada
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Load dan cache jika belum ada
        try:
            icon_image = Image.open(path)
            icon_image = icon_image.resize(size, Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)

            # Cache untuk penggunaan berikutnya
            self._cache[cache_key] = icon_photo

            return icon_photo

        except Exception as e:
            print(f"Warning: Could not load icon from {path}: {e}")
            return None

    def clear_cache(self):
        """Clear semua cached icons"""
        self._cache.clear()

# Global instance untuk easy access
icon_cache = IconCache()
