INSTALLED_APPS = [
    # ...
    'diplomas',
]

# Add this block of code at the end of the file
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')