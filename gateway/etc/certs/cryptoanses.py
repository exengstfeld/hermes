from M2Crypto import X509
from base64 import b64decode

def validatesigntoken(pathcert, token, sign):
    '''
    @author: Juan Manuel Carrascal
    @param pathcert: Complete PATH file cert anses
    @param token: String to sign encoded for ANSES
    @param token: String signed 
    '''
    pubkey = X509.load_cert(pathcert).get_pubkey()
    pubkey.reset_context(md='sha1')
    pubkey.verify_init() 
    pubkey.verify_update(str(b64decode(token)))
    if pubkey.verify_final(b64decode(sign)) != 1:
        return {"success": False, "msg": "El token no fue firmado por el certificado de Anses"}
    else:
        return {"success": True, "msg": "OK"}


    
def testvalidate():    
    token="PD94bWwgdmVyc2lvbj0iMS4wIj8+DQo8c3NvIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiIHhtbG5zOnhzZD0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEiPg0KICA8aWQgc3JjPSJjbj1BdXRoU2VydmVyLG91PUdTWVQsbz1BTlNFUyxjPUFSIiBkc3Q9ImNuPUFwbGljYWNpb25lcyxvdT1HU1lULG89QU5TRVMsYz1BUiIgdW5pcXVlX2lkPSI1NTkxQTVGRDUyNy0xLUU4MDAiIGdlbl90aW1lPSIxNDM1NjA0OTczIiBleHBfdGltZT0iMTQzNTYwODU3MyIgLz4NCiAgPG9wZXJhdGlvbiB0eXBlPSJsb2dpbiI+DQogICAgPGxvZ2luIHN5c3RlbT0iZm9ybWRpZ2kiIGVudGl0eT0iMzM2Mzc2MTc0NDkiIHVpZD0iQjg4NTUwMSIgdXNlcm5hbWU9IkI4ODU1MDEiIGF1dGhtZXRob2Q9Ik5UTE0iPg0KICAgICAgPGluZm8gbmFtZT0ibm9tYnJlIiB2YWx1ZT0iS09NTEVWIFNFUkdVRUkiIC8+DQogICAgICA8aW5mbyBuYW1lPSJlbWFpbCIgdmFsdWU9IiIgLz4NCiAgICAgIDxpbmZvIG5hbWU9Im9maWNpbmEiIHZhbHVlPSIiIC8+DQogICAgICA8aW5mbyBuYW1lPSJvZmljaW5hZGVzYyIgdmFsdWU9IlVTVUFSSU8gIE5PIEFTT0NJQURPIEEgVU5BIERFUEVOREVOQ0lBIiAvPg0KICAgICAgPGluZm8gbmFtZT0iaXAiIHZhbHVlPSIxMC44Ni4zMC4yNDEiIC8+DQogICAgICA8Z3JvdXBzPg0KICAgICAgICA8Z3JvdXAgbmFtZT0iQWRtaW5pc3RyYWRvciIgLz4NCiAgICAgIDwvZ3JvdXBzPg0KICAgIDwvbG9naW4+DQogIDwvb3BlcmF0aW9uPg0KPC9zc28+"
    sign="S5nFvkiTsOI0X6YGES1OExmAzrwfXtoianxrKQIVbbFbRnPvSHzCfqCub6vgoHcQYo8+w53AdMn9IKtitvUmMCN70JplBskj5Ig3UcajgsKi8ZVd0bW8wbWrDTPo447MkTpvxRZD3ayDe9QmCt25LuO2IZIgHUytcvcwIisBeG8="
    return validatesigntoken("/tmp/cert_anses.crt",token,sign )


