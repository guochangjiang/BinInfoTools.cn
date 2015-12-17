#!C:/python34/python.exe

import cgi
import svgwrite
import os
form = cgi.FieldStorage()

#print("Content-Type: text/html")
#print("")
#print("hello中国")
os.system("python tmp.py")
#infile=open("tmp.txt", "r")
#for line in infile:
#    print("<pre>" + line + "</pre>")
'''
dwg = svgwrite.Drawing("tmp.svg", debug=True)
dwg.add(dwg.text(
    "chr",
    insert=(0, 0),
    font_size = 16,
    fill='black'))

dwg.add(dwg.line(
    (0, 0),
    (100, 100),
    stroke_width=2,
    stroke="black"))
    
dwg.save()
print("success")
'''