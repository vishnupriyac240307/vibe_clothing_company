import os
import requests
from config import Config

CATEGORY_FALLBACK_IMAGES = {
    't-shirts': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop&q=80',
    't-shirt': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop&q=80',
    'jeans': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=500&auto=format&fit=crop&q=80',
    'jackets': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&auto=format&fit=crop&q=80',
    'jacket': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&auto=format&fit=crop&q=80',
    'hoodies': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=500&auto=format&fit=crop&q=80',
    'hoodie': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=500&auto=format&fit=crop&q=80',
    'shirts': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500&auto=format&fit=crop&q=80',
    'dresses': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500&auto=format&fit=crop&q=80',
    'activewear': 'https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=500&auto=format&fit=crop&q=80'
}

DEFAULT_PRODUCT_IMAGE = 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=500&auto=format&fit=crop&q=80'

class ImageService:

    @staticmethod
    def get_product_image(product_name, category='T-Shirts'):
        """
        Attempts to fetch a relevant product image from Unsplash/Pexels API if key available,
        otherwise uses a category-matched curated fashion image CDN fallback.
        """
        api_key = Config.UNSPLASH_API_KEY
        if api_key:
            try:
                url = f"https://api.unsplash.com/search/photos?query={product_name}+clothing&per_page=1&client_id={api_key}"
                resp = requests.get(url, timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get('results') and len(data['results']) > 0:
                        return data['results'][0]['urls']['regular']
            except Exception as e:
                print(f"Unsplash API call skipped: {e}")

        # Category-based fallback
        cat_key = category.lower().strip() if category else 't-shirts'
        if cat_key in CATEGORY_FALLBACK_IMAGES:
            return CATEGORY_FALLBACK_IMAGES[cat_key]

        # Match keyword in product_name
        name_lower = product_name.lower() if product_name else ''
        for key, img_url in CATEGORY_FALLBACK_IMAGES.items():
            if key in name_lower:
                return img_url

        return DEFAULT_PRODUCT_IMAGE
