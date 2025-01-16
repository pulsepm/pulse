import re

PACKAGE_RE = r"^([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)([:#@])?([^\s:#@]*)?$"


def package_parse(package):
    match = re.match(PACKAGE_RE, package)
    if match:
        return match.groups()  # (author, repo, sep, ver)
    return None