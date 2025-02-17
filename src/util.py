import getpass
import os


def set_sensitive_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


def set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = input(f"{var}: ")
