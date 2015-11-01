import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'server',
    'ldap_sync',
)

AUTH_LDAP_SERVER_URI = "ldap://localhost"
LDAP_SYNC_URI = AUTH_LDAP_SERVER_URI


BASEDN = "dc=example,dc=com"
LDAP_SYNC_BASE = "ou=Users," + BASEDN

# AUTH_LDAP_START_TLS = True

AUTH_LDAP_BIND_DN = "cn=admin," + BASEDN
AUTH_LDAP_BIND_PASSWORD = 'password'

LDAP_SYNC_BASE_USER = AUTH_LDAP_BIND_DN
LDAP_SYNC_BASE_PASS = AUTH_LDAP_BIND_PASSWORD
LDAP_SYNC_USER_FILTER = "(&(objectClass=person))"


AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=Users," + BASEDN,
    ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups," + BASEDN,
    ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
    )

# name_attr='cn'
AUTH_LDAP_GROUP_TYPE = PosixGroupType()

#AUTH_LDAP_REQUIRE_GROUP = "cn=Admins,ou=groups," + BASEDN

AUTH_LDAP_USER_ATTR_MAP = {"email" : "mail"} #""first_name": "givenName", "last_name": "sn"}
AUTH_LDAP_PROFILE_ATTR_MAP = {"uid_number": "uidNumber", "email": "mail"}

LDAP_SYNC_USER_ATTRIBUTES = {
    "uid": "username",
    "mail": "email",
}

GROUP_BASE = "ou=groups," + BASEDN

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_active": "cn=Members," + GROUP_BASE,
    "is_staff": "cn=Members," + GROUP_BASE,
    "is_superuser": "cn=Admins," + GROUP_BASE
}

AUTH_LDAP_PROFILE_FLAGS_BY_GROUP = {
    "is_admin": ["cn=Admins," + GROUP_BASE]
}

#
# For TLS:
#
#AUTH_LDAP_GLOBAL_OPTIONS = {
#    ldap.OPT_X_TLS_REQUIRE_CERT: True,
#    ldap.OPT_X_TLS_DEMAND: True,
#}

# You will also need to set:
#
# SECRET_KEY
# probably a different DATABASE (https://docs.djangoproject.com/en/1.7/ref/settings/#databases)
#
# STATIC_ROOT (and run ./manage.py collectstatic to populate it)
# ALLOWED_HOSTS to the FQDN of your website
# LOGGING to somewhere the webserver can log to
# DEBUG = False
# CSRF_COOKIE_SECURE = True
# TEMPLATE_DEBUG = False
# SESSION_COOKIE_SECURE = True
#
# EMAIL_*, maybe
#
# and, last but not least:
# ACServer specific things
#
# ACS_API_KEY
# ACNODE_IP_RANGE
#
