import os
import ConfigParser

config = ConfigParser.ConfigParser()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
config.read(os.path.join(BASE_DIR, 'utopia.conf'))
KEY_DIR = os.path.join(BASE_DIR, 'upuser/keys')

# ======== Database info ==========
DB_HOST = config.get('db', 'host')
DB_PORT = config.getint('db', 'port')
DB_USER = config.get('db', 'user')
DB_PASSWD = config.get('db', 'password')
DB_DATABASE = config.get('db', 'database')

# ======== salt info ==========
SALT_HOST=config.get('salt', 'host')
SALT_PORT=config.get('salt', 'port')
SALT_USER=config.get('salt', 'user')
SALT_PASSWD=config.get('salt', 'password')

# ======== ETCD info ==========
ETCD1_HOST = config.get('etcd','host1')
ETCD2_HOST = config.get('etcd','host2')
ETCD3_HOST = config.get('etcd','host3')
ETCD_PORT = config.getint('etcd','port')
ETCD_USER = config.get('etcd','user')
ETCD_PASSWD = config.get('etcd','password')

# =========== BASE info ==============
REDIS_HOST = config.get('redis','host')
REDIS_PORT = config.get('redis','port')


# =========== BASE info ==============
LOG_DIR = os.path.join(BASE_DIR, 'logs')
SSH_KEY_DIR = os.path.join(BASE_DIR, 'upuser/keys/role_keys')
KEY = config.get('base', 'key')
URL = config.get('base', 'url')
LOG_LEVEL = config.get('base', 'log')
WEB_SOCKET_HOST = config.get('websocket', 'web_socket_host')

# ========== mail info ============
MAIL_ENABLE = config.get('mail', 'mail_enable')
EMAIL_HOST = config.get('mail', 'email_host')
EMAIL_PORT = config.get('mail', 'email_port')
EMAIL_HOST_USER = config.get('mail', 'email_host_user')
EMAIL_HOST_PASSWORD = config.get('mail', 'email_host_password')
EMAIL_USE_TLS = config.getboolean('mail', 'email_use_tls')
EMAIL_TIMEOUT = 5


SECRET_KEY = 't1*x+9uq-s@o@au32+g(g!gn_hzpqjp--cod*-^+$(h&ct1efn'

DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0/8']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_crontab',
    'bootstrapform',
    'utopia',
    'upuser',
    'upasset',
    'upperm',
    'uplog',
    'upetcd',
    'upenv',
    'upapp',
    'upgray',
]

MIDDLEWARE_CLASSES = [
#    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'utopia.urls'

WSGI_APPLICATION = 'utopia.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_DATABASE,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'utopia.context_processors.name_proc',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

LANGUAGE_CODE = 'zh_CN'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

BOOTSTRAP_COLUMN_COUNT = 10

CRONJOBS = [
    ('0 1 * * *', 'upasset.asset_api.asset_ansible_update_all')
]


AUTH_USER_MODEL = 'upuser.User'

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'utopia.settings'