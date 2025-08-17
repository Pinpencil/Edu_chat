from django import template

register = template.Library()

@register.filter
def has_key(dictionary, key):
    """Check if a dictionary has a specific key."""
    return key in dictionary

@register.filter
def get_item(dictionary, key):
    """Retrieve a value from a dictionary by key."""
    return dictionary.get(key)

@register.filter
def is_image(url):
    """Check if a URL points to an image file based on its extension."""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    return any(url.lower().endswith(ext) for ext in image_extensions)
