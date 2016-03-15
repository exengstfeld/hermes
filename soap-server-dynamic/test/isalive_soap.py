import lxml.etree as etree

#x = etree.parse("http://127.0.0.1:4500/soap/isalive?wsdl")

x = etree.parse("http://127.0.0.1:8000/?wsdl")
print etree.tostring(x, pretty_print = True)
