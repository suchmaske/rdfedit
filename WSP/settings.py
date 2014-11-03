# Django settings for WSP project.

import os
PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_ROOT, "database", "database.sqlite3"), # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# Get the sindice config directory
SINDICE_API_URL = "http://api.sindice.com/v3/search?"
SINDICE_CONFIG_QUERY = os.path.join(PROJECT_ROOT, "rdfedit", "static", "rdfedit", "sindice-fetcher-config", "query-config.json")
SINDICE_CONFIG_MAPPING = os.path.join(PROJECT_ROOT, "rdfedit", "static", "rdfedit", "sindice-fetcher-config", "mapping-config.json")


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'dajaxice.finders.DajaxiceFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '$$%!n^-&d!ujv2p6^&cbe%um3#@xwa^232l=uhh!2*3t$3fp)7'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'WSP.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'WSP.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'WSP.rdfedit',
    'widget_tweaks',
    'dajaxice',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

NAMESPACES_DICT = {
"dc":"http://purl.org/dc/elements/1.1/",
"DOLCE-Lite":"http://www.loa-cnr.it/ontologies/DOLCE-Lite.owl#",
"foaf":"http://xmlns.com/foaf/0.1/",
"ore":"http://www.openarchives.org/ore/terms/",
"dcmitype":"http://purl.org/dc/dcmitype/",
"rdfs":"http://www.w3.org/2000/01/rdf-schema#",
"xsd":"http://www.w3.org/2001/XMLSchema#",
"owl":"http://www.w3.org/2002/07/owl#",
"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
"cidoc_crm_v5":"http://www.cidoc-crm.org/rdfs/cidoc_crm_v5.0.2_english_label.rdfs#",
"core":"http://purl.org/vocab/frbr/core#",
"dcterms":"http://purl.org/dc/terms/",
"skos":"http://www.w3.org/2004/02/skos/core#",
"vs":"http://www.w3.org/2003/06/sw-vocab-status/ns#",
"gnd":"http://d-nb.info/standards/elementset/gnd#",
"edm":"http://www.europeana.eu/schemas/edm/",
"wsp":"http://wsp.normdata.rdf/",
"dbpedia": "http://dbpedia.org/resource/",
"dbpprop": "http://dbpedia.org/property/",
"gn": "http://www.geonames.org/ontology#",
"wspo": "http://wsp.bbaw.de/avh/Orinoco/",
"ex": "http://www.example.org/"
}


