#!C:/python34/python.exe

import cgi
import re
#import os

print("Content-Type: text/html; charset=utf-8\n\n")

form = cgi.FieldStorage()
try:
    protinfo = form["proteininfo"].value
except:
    print("<h2 style=\"color:red;font-size:20px\"> The information of protein structure cannnot be blank</h2>")
    #os._exit(0)





################
##子程序
################

#获取蛋白列表
def GetProtList(info):
    plist=[]
    for line in info:
        line = line.strip()
        if line == '' or re.search("^#", line):
            continue
        else:
            line = re.sub("\s+", "\t", line)
            columns = line.split("\t")
            if columns[0] not in plist:
                plist.append(columns[0])
                #print(columns[0])
    return plist

#获取蛋白长度
def GetProtLen(info):
    plen={}
    for line in info:
        line = line.strip()
        if line == '' or re.search("^#", line):
            continue
        else:
            line = re.sub("\s+", "\t", line)
            columns = line.split("\t")
            label = columns[1]
            label = label.lower()
            if label == "protein":
                try:
                    columns[3] = int(columns[3])
                    columns[2] = int(columns[2])
                except:
                    pass
                plen[columns[0]] = columns[3]
    return plen

#获取标签列表
def GetTagList(info):
    tlist=[]
    for line in info:
        line = line.strip()
        if line == '' or re.search("^#", line):
            continue
        else:
            line = re.sub("\s+", "\t", line)
            columns = line.split("\t")
            label = columns[1]
            tag = columns[4]
            label = label.lower()
            if columns[1] == "domain" or columns[1] == "motif" or columns[1] == "marker":
                if tag not in tlist:
                    tlist.append(tag)
    return tlist

#获取蛋白全长信息
def GetProtInfo(locus, tag, info):
    posdata=[]
    for line in info:
        line = line.strip()
        if line =='':
            continue
        line = re.sub("\s+", "\t", line)
        if locus in line:
            columns = line.split("\t")
            if tag in columns[1].lower():
                posdata.append(columns[2] + "--" + columns[3])
    return posdata

#获取domain信息
def GetDomainInfo(locus, tag, info):
    posdata=[]
    for line in info:
        line = line.strip()
        if line =='':
            continue
        line = re.sub("\s+", "\t", line)
        if locus in line:
            columns = line.split("\t")
            if columns[1].lower() == tag:
                posdata.append(columns[4] + "--" + columns[2] + "--" + columns[3])
    return posdata

#获取motif,marker信息
def GetTagInfo(locus, info):
    posdata=[]
    for line in info:
        line = line.strip()
        if line =='':
            continue
        line = re.sub("\s+", "\t", line)
        if locus in line:
            columns = line.split("\t")
            if columns[1].lower() in ["marker", "motif"]:
                posdata.append(columns[4] + "--" + columns[2] + "--" + columns[3])
    return posdata

#######################
##颜色处理
#######################
tagcolors = {}
defaultcolors_ori=["green", "red", "orange", "blue", "hotpink", "magenta",
               "darkorange", "royalblue", "deeppink", "springgreen","teal",
               "blue", "chartreuse", "yellow", "brown", "aqua"]
defaultcolors = []

try:
    colordata = form["colors"].value
except:
    colordata= ''

if colordata:
    for pair in colordata.split(";"):
        cpair = pair.split(":")
        tagcolors[cpair[0]] = cpair[1]
for color in defaultcolors_ori:
    if color not in tagcolors.values():
        defaultcolors.append(color)

######################
#信息处理
######################

protinfo = protinfo.strip()
data = protinfo.splitlines()

if len(data[0].split()) != 5:
    print("<h2 style=\"color:red;font-size:20px\"> The information format of protein structure is illegal</h2>")

#获取蛋白列表
proteinlist = GetProtList(data)
#获取蛋白标签
taglist = GetTagList(data)
i = 0
for tl in taglist:
    if tl not in tagcolors.keys():
        if i >= len(defaultcolors):
            i = 0
        tagcolors[tl] = defaultcolors[i]
        i += 1
#获取蛋白长度
ProtLenDic = GetProtLen(data)
#获取最短蛋白
minlength = ProtLenDic[proteinlist[0]]
minprot = proteinlist[0]
for key in sorted(ProtLenDic.keys()):
    if minlength > ProtLenDic[key]:
        minlength = ProtLenDic[key]
        minprot = key
# 获取最长基因
maxlength = ProtLenDic[proteinlist[0]]
maxprot = proteinlist[0]
for key in sorted(ProtLenDic.keys()):
    if maxlength < ProtLenDic[key]:
        maxlength = ProtLenDic[key]
        maxprot = key


######################
##绘画准备
######################
import svgwrite
painty0 = 25                             #起始y轴位置
paintx0=10                               #起始x轴位置
legendx0 = 900                           #图例x轴位置
legendboxx0 = legendx0 - 5               #图例框x轴位置
piclength = 1000.0                       #基因图长度
geneinterval = 50.0                      #相邻基因间隔


aalength = form["pxperaa"].value
try:
    aalength = float(aalength)
except:
    pass

gspaint = svgwrite.Drawing("tmp.protein.svg", (maxlength * aalength + paintx0 + 20, 320 * len(proteinlist)))

######################
#按照蛋白列表进行绘画
######################

for protname in proteinlist:
    charnummax = 1
    legendx0 = ProtLenDic[protname] * aalength - 75
    legendboxx0 = legendx0 - 5
    #显示基因名
    if form["showname"].value == "on":
        gspaint.add(gspaint.text(
            protname,
            insert=(paintx0, painty0),
            font_size = 16,
            fill = 'black'))
        if form["scalecontrol"].value == "on":
            painty0 += 10
        else:
            painty0 += 50

    unit = 100.0
    segments = int(ProtLenDic[protname] / unit)
    #绘制比例尺
    if form["scalecontrol"].value == "on":
        gspaint.add(gspaint.line(
                (paintx0+1, painty0),
                (paintx0+1, painty0+5),
                stroke_width=2,
                stroke="gray"))
        gspaint.add(gspaint.text(
                "0",
                insert=(paintx0, painty0+15),
                font_size = 10,
                fill = 'black'))
        i = 1
        while i <= segments:
            gspaint.add(gspaint.line(
                    (paintx0 + 1 + i * unit * aalength, painty0),
                    (paintx0 + 1 + i * unit * aalength, painty0+5),
                    stroke_width=2,
                    stroke="gray"))
            flag = i * 100
            gspaint.add(gspaint.text(
                    str(flag),
                    insert=(paintx0 + 1 + i * unit * aalength - 5, painty0+15),
                    font_size = 10,
                    fill = 'black'))
            i += 1
        gspaint.add(gspaint.line(
                (paintx0, painty0),
                (ProtLenDic[protname] * aalength + paintx0 + 1, painty0),
                stroke_width=3,
                stroke="black"))
        painty0 += 50

    #绘制总长
    protinfo = GetProtInfo(protname, 'protein', data)
    for info in protinfo:
        (start, end) = info.split("--")
        start = int(start)
        end = int(end)
        length = end - start + 1
        length = length * aalength
        gspaint.add(gspaint.line(
            ((start - 1) * aalength + paintx0 + 1, painty0 + 7.5),
            ((end - 1) * aalength + paintx0 + 1, painty0 + 7.5),
            stroke_width = 3,
            stroke = "gray",
            fill = "gray",
            opacity = 1.0  #不透明度（待添加功能）
            ))

    #绘制domain
    domaininfo = GetDomainInfo(protname, 'domain', data)
    domainsave=[]
    legendy0 = painty0 + 60
    legendboxy0 = legendy0 - 5
    doheight = form["domainheight"].value
    height = float(doheight)
    for line in domaininfo:
        (domain, aa1, aa2) = line.split("--")
        aa1 = int(aa1)
        aa2 = int(aa2)
        length= aa2 - aa1 + 1
        vertical_gradient_domain = gspaint.linearGradient((0, 0), (0, 1))
        gspaint.defs.add(vertical_gradient_domain)
        vertical_gradient_domain.add_stop_color(0, tagcolors[domain])
        vertical_gradient_domain.add_stop_color(1, 'white')
        gspaint.add(gspaint.rect(
                insert = ((aa1 - 1) * aalength + paintx0 + 1, painty0 + 7.5 - height/2),
                size = (str(length * aalength) + "px", doheight + "px"),
                stroke_width = 1,
                stroke = "black",
                fill = vertical_gradient_domain.get_paint_server(default='currentColor')
            ))
        if form["showdomain"].value == "on":
            domainchr = len(domain)
            gspaint.add(gspaint.text(
                domain,
                insert = (((aa2-aa1+1)*aalength - domainchr*10)/2 + (aa1 - 1) * aalength + paintx0 + 1, painty0 + 12),
                font_size = 14,
                fill = 'black'))
        if form["showlegend"].value == "on":
            #绘制domain图例
            if domain not in domainsave:
                gspaint.add(gspaint.rect(
                    insert = (legendx0, legendy0),
                    size = ("40px", "25px"),
                    stroke_width = 1,
                    stroke = "black",
                    fill = vertical_gradient_domain.get_paint_server(default='currentColor')
                    ))
                gspaint.add(gspaint.text(
                    domain,
                    insert = (legendx0 + 50, legendy0+16.5),
                    font_size = 12,
                    fill = 'black'))
                legendy0 += 35
                domainsave.append(domain)
                if len(domain) > charnummax:
                    charnummax = len(domain)
    if form["showlegend"].value == "on":
        #绘制图例框
        legendy0 -= 5
        lines = gspaint.add(gspaint.g(stroke_width=2, stroke='gray', fill='none'))
        endlegendx = legendboxx0 + 65 + charnummax * 7
        lines.add(gspaint.polyline(
            [(legendboxx0, legendboxy0), (endlegendx, legendboxy0),
            (endlegendx, legendy0), (legendboxx0, legendy0),
            (legendboxx0, legendboxy0)]))

    #绘制marker,motif
    if form["showmm"].value == "on":
        mminfo = GetTagInfo(protname, data)
        for info in mminfo:
            (mm, start, end) = info.split("--")
            start = int(start)
            end = int(end)
            length = end - start + 1
            if length < 2:
                length = 2
            gspaint.add(gspaint.rect(
                insert = ((start - 1) * aalength + paintx0 + 1, painty0 - 12.5),
                size = (str(length * aalength) + "px", "40px"),
                stroke_width = 1,
                stroke = tagcolors[mm],
                fill = tagcolors[mm]))
            mm = mm.strip('\"')
            charnum = len(mm)
            gspaint.add(gspaint.text(
                mm,
                insert = (((end-start+1)*aalength - charnum*5)/2 + (start - 1) * aalength + paintx0 + 1, painty0 -20),
                font_size = 10,
                #font_family="sans-serif",
                fill = 'red'))

    painty0 = legendy0 + geneinterval   #下个基因绘制y轴位置

######################
##保存图像
gspaint.save()
#tmpout = open("pgs.out.template.txt", "r")
#for line in tmpout:
#    print(line)
#tmpout.write("<h3>运行成功，基因结构图如下</h3>\n")
print("SVG editing tool: Inkscape(powerful, free, open source, general purpose)<br>\n")
print("Download:<br> <a href=https://inkscape.org>https://inkscape.org</a> <br><br>\n")
print("<img src=\"tmp.protein.svg\"  alt=\"svg结构成果图\"/>")


