#!C:/python34/python.exe
#!python

import cgi, string, os, sys
import csv,codecs
import time

sys.stderr = sys.stdout # show error msgs
form = cgi.FieldStorage( ) # parse form data
print "Content-type: text/html\n" # with blank line

clientfile = form['clientfile'].value
filename = '%s.csv' % str(int(time.time()))

print """
<html><head><title>Putfile response page</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>
<h1>Putfile response page</h1><pre>"""
print '''<h3>[writing content into %s]</h3><hr>''' % filename
f = open(filename,'w')
f.write(str(clientfile))
f.close()
f = file(filename)
csvreader = csv.reader(file(filename)) #阅读CSV文件，写入的话，用csv.writer(file(filename))
csvreader = csv.reader(f)
for row in csvreader:
  print '<b>|</b>'.join(row)
f.close()
os.remove(filename)
print '''<hr><h3>[file %s has been removed]</h3>''' % filename
print """</pre></html>"""