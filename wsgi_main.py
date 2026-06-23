import os
import sys

sys.path.insert(1, os.path.expanduser('~/laonte/public_html/'))

activate_this = os.path.expanduser('~/laonte/venv/bin/activate_this.py')
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
