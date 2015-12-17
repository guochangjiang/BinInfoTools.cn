#!C:/python34/python.exe
#!-*- coding=utf-8-*-
outfile=open("tmp.txt", "w")
outfile.write("1.this is a test.中文\n")
outfile.write("2.this is a test.中文")
outfile.close()