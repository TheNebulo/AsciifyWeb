import re

def check_pass(p):
    if not re.fullmatch(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,20}$', p): return False
    return True

def check_name(n):
    if len(n) < 4 or len(n) > 10: return False
    return True

def check_email(e):
    if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', e): return False
    return True