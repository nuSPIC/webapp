import cjson
#import ujson

def decode(*args, **kwargs):
    try:
        return ujson.decode(*args, **kwargs)
    except:
        return cjson.decode(*args, **kwargs)
    
def encode(*args, **kwargs):
    try:
        return ujson.encode(*args, **kwargs)
    except:
        return cjson.encode(*args, **kwargs)

