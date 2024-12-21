import os
import jwt
import secrets
from datetime import datetime, timezone, timedelta
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

UTC = timezone.utc


def hash_password(password: str) -> str:
    """
    Hashes the provided password.

    :param password: The password to hash.
    :type password: str

    :returns: The hashed password.
    :rtype: str
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify whether the plain password matches the hashed password.

    :param plain_password: The plain password to verify.
    :type plain_password: str

    :param hashed_password: The hashed password to compare against.
    :type hashed_password: str

    :returns: True if the plain password matches the hashed password, False otherwise.
    :rtype: bool
    """
    return pwd_context.verify(plain_password, hashed_password)


def is_authenticated(user, password: str) -> bool:
    if not user or not user.hashed_password:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return True


def to_timestamp(date: datetime | None) -> int | None:
    """
    Convert a datetime object to a Unix timestamp.

    :param date: The datatime object to convert
    :type date: datetime | None

    :returns: The Unix timestamp corresponding to the input object,
              or None if the input is None
    :rtype: int | None
    """
    # If date is not None, set the time zone to UTC,
    # otherwise leave data as it is
    date = date.replace(tzinfo=timezone.utc) if date else date
    return int(date.timestamp()) if date else None


def utc_now():
    """
        Returns the current time in UTC format without time zone information.
    :returns: A datetime object representing the current time in UTC format without time zone information.
    """
    return datetime.now(UTC).replace(tzinfo=None)


def is_protected_username(username: str):
    """
    Check if a given username is in the list of protected usernames.

    This function verifies whether a provided username belongs to a set of
    reserved or system usernames that should not be used by regular users.
    It checks against a predefined list of usernames, which includes common
    administrative, technical, and service-related names.

    :param username: The username for check
    :type username: str

    :return: True if the username is protected, False otherwise.
    :rtype: bool
    """
    usernames = [
        ["admin", "blog", "dev", "ftp", "mail", "pop", "pop3", "imap", "smtp"],
        ["stage", "stats", "status", "www", "beta", "about", "access"],
        ["account", "accounts", "add", "address", "adm"],
        ["administration", "adult", "advertising", "affiliate", "affiliates"],
        ["ajax", "analytics", "android", "anon", "anonymous", "api"],
        ["app", "apps", "archive", "atom", "auth", "authentication"],
        ["avatar", "backup", "banner", "banners", "bin", "billing", "blog"],
        ["blogs", "board", "bot", "bots", "business", "chat"],
        ["cache", "cadastro", "calendar", "campaign", "careers"],
        ["cgi", "client", "cliente", "code", "comercial", "compare", "config"],
        ["connect", "contact", "contest", "create", "code", "compras"],
        ["css", "dashboard", "data", "db", "design", "delete"],
        ["demo", "design", "designer", "dev", "devel", "dir"],
        ["directory", "doc", "docs", "domain", "download", "downloads"],
        ["edit", "editor", "email", "ecommerce", "forum", "forums"],
        ["faq", "favorite", "feed", "feedback", "flog", "follow"],
        ["file", "files", "free", "ftp", "gadget", "gadgets"],
        ["games", "guest", "group", "groups", "help", "home", "homepage"],
        ["host", "hosting", "hostname", "html", "http", "httpd"],
        ["https", "hpg", "info", "information", "image", "img", "images"],
        ["imap", "index", "invite", "intranet", "indice", "ipad", "iphone"],
        ["irc", "java", "javascript", "job", "jobs", "js"],
        ["knowledgebase", "log", "login", "logs", "logout", "list", "lists"],
        ["mail", "mail1", "mail2", "mail3", "mail4", "mail5"],
        ["mailer", "mailing", "mx", "manager", "marketing"],
        ["master", "me", "media", "message", "microblog", "microblogs"],
        ["mine", "mp3", "msg", "msn", "mysql", "messenger"],
        ["mob", "mobile", "movie", "movies", "music", "musicas"],
        ["my", "name", "named", "net", "network", "new"],
        ["news", "newsletter", "nick", "nickname", "notes", "noticias"],
        ["ns", "ns1", "ns2", "ns3", "ns4", "ns5", "ns6", "ns7", "ns8"],
        ["ns9", "ns10", "old", "online", "operator", "order", "orders"],
        ["page", "pager", "pages", "panel", "password", "perl", "pic", "pics"],
        ["photo", "photos", "photoalbum", "php", "plugin", "plugins", "pop"],
        ["pop3", "post", "postmaster", "postfix", "posts"],
        ["profile", "project", "projects", "promo", "pub", "public", "python"],
        ["random", "register", "registration", "root", "ruby", "rss"],
        ["sale", "sales", "sample", "samples", "script", "scripts", "secure"],
        ["send", "service", "shop", "sql", "signup", "signin", "search"],
        ["security", "settings", "setting", "setup", "site"],
        ["sites", "sitemap", "smtp", "soporte", "ssh", "stage", "staging"],
        ["start", "subscribe", "subdomain", "suporte", "support", "stat"],
        ["static", "stats", "status", "store", "stores", "system"],
        ["tablet", "tablets", "tech", "telnet", "test", "test1", "test2"],
        ["test3", "teste", "tests", "theme", "themes", "tmp"],
        ["todo", "task", "tasks", "tools", "tv", "talk", "update", "upload"],
        ["url", "user", "username", "usuario", "usage", "vendas"],
        ["video", "videos", "visitor", "win", "ww", "www"],
        ["www1", "www2", "www3", "www4", "www5", "www6", "www7"],
        ["wwww", "wws", "wwws", "web", "webmail", "website", "websites"],
        ["webmaster", "workshop", "xxx", "xpg", "you"],
    ]

    usernames = list(set(item for sublist in usernames for item in sublist))

    return username.lower() in usernames

