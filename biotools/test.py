#!C:/python34/python.exe

import cgi
form = cgi.FieldStorage()
print("Content-Type: text/html")
print("")
print("<html>")
print("<h2>CGI Script Output</h2>")
print("<p>")
print("The user entered data are:<br>")
print("<b>First Name:</b> "+ form["firstName"].value +"<br>")
print("<b>Last Name:</b> "+ form["lastName"].value +"<br>")
print("<b>Position:</b> "+ form["position"].value +"<br>")
print("</p>")
print("</html>")