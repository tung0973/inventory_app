# utils/helpers.py

def safe_int(v, default=0):
    try:
        return int(v)
    except:
        return default

def safe_float(v, default=0.0):
    try:
        return float(v)
    except:
        return default