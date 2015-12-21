#!C:/python34/python.exe

import cgi, os
import cgitb
import re
cgitb.enable()

print("Content-Type: text/html; charset=utf-8\n\n")
#print("<p>hello中国")
form = cgi.FieldStorage()
fileitem = form["FILE"].value
print(form["FILE"].value.decode())
if form["FILE"].value.decode() == '':
    print("No file upload<br>")
tmpout = open("tmp/tmp.file.upload.txt", "w")
filecontent = re.sub("\r\n", "\n", fileitem.decode())
tmpout.write(filecontent)
#print(fileitem)
#print("<p>content of file</p><p>" + str(fileitem))

print('<a href="tmp/tmp.file.upload.txt" > download </a>')
