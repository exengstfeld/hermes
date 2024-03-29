import xml.etree.cElementTree as ET
from base64 import b64decode

from datetime import datetime, date
import time

token="PD94bWwgdmVyc2lvbj0iMS4wIj8+DQo8c3NvIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiIHhtbG5zOnhzZD0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEiPg0KICA8aWQgc3JjPSJjbj1BdXRoU2VydmVyLG91PUdTWVQsbz1BTlNFUyxjPUFSIiBkc3Q9ImNuPUFwbGljYWNpb25lcyxvdT1HU1lULG89QU5TRVMsYz1BUiIgdW5pcXVlX2lkPSI1NTkxQTVGRDUyNy0xLUU4MDAiIGdlbl90aW1lPSIxNDM1NjA0OTczIiBleHBfdGltZT0iMTQzNTYwODU3MyIgLz4NCiAgPG9wZXJhdGlvbiB0eXBlPSJsb2dpbiI+DQogICAgPGxvZ2luIHN5c3RlbT0iZm9ybWRpZ2kiIGVudGl0eT0iMzM2Mzc2MTc0NDkiIHVpZD0iQjg4NTUwMSIgdXNlcm5hbWU9IkI4ODU1MDEiIGF1dGhtZXRob2Q9Ik5UTE0iPg0KICAgICAgPGluZm8gbmFtZT0ibm9tYnJlIiB2YWx1ZT0iS09NTEVWIFNFUkdVRUkiIC8+DQogICAgICA8aW5mbyBuYW1lPSJlbWFpbCIgdmFsdWU9IiIgLz4NCiAgICAgIDxpbmZvIG5hbWU9Im9maWNpbmEiIHZhbHVlPSIiIC8+DQogICAgICA8aW5mbyBuYW1lPSJvZmljaW5hZGVzYyIgdmFsdWU9IlVTVUFSSU8gIE5PIEFTT0NJQURPIEEgVU5BIERFUEVOREVOQ0lBIiAvPg0KICAgICAgPGluZm8gbmFtZT0iaXAiIHZhbHVlPSIxMC44Ni4zMC4yNDEiIC8+DQogICAgICA8Z3JvdXBzPg0KICAgICAgICA8Z3JvdXAgbmFtZT0iQWRtaW5pc3RyYWRvciIgLz4NCiAgICAgIDwvZ3JvdXBzPg0KICAgIDwvbG9naW4+DQogIDwvb3BlcmF0aW9uPg0KPC9zc28+"
ip = "192483948"




parse = lambda token, sign: next(info for info in ET.fromstring(b64decode(token)).iter("info") if info.attrib['name'] == "ip").attrib['value'] != ip

print parse(token, "")


token_expiration_validation = lambda token_xml, time: long(next(id_tag for id_tag in token_xml.iter("id")).attrib["exp_time"]) < time

print time.time()
print token_expiration_validation(ET.fromstring(b64decode(token)), time.time())