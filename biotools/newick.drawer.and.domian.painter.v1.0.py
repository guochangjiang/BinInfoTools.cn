#!C:/python34/python.exe
#-*- coding: utf-8 -*-

import cgi
import re
import svgwrite

#################
##子例程

#获取分支数目和总长
def GetCladeNumLength(info):
    AllName = []
    AllClLen = {}
    tname = re.findall("([\w\d\.\-\_\\/]+):", info) #获取所有基因名
    for name in tname:
        if re.search("[a-zA-Z\_\\/]+", name):
            AllName.append(name)
    for name in AllName:
        AllClLen[name] = GetCladeLen(name, info)

    return AllName, AllClLen

#获取每个基因的分支长度
def GetCladeLen(name,data):
    #print(name)
    #index = data.find(name)
    fb_index = []
    rb_index = []
    index1 = 0
    while index1 < len(data) -1:
        if data[index1] != "(":
            index1 += 1
            continue
        index2 = index1 + 1
        while index2 < len(data):
            if data[index2] != ")":
                index2 += 1
                continue
            substr = data[index1:index2+1]
            if substr.count("(") == substr.count(")"):
                fb_index.append(index1)
                rb_index.append(index2)
            index2 += 1
        index1 += 1
    i = 0
    uselessinfo = []
    while i < len(fb_index):
        subinfo = data[fb_index[i]:rb_index[i]+1]
        if name not in subinfo:
            uselessinfo.append(subinfo)
        i += 1
    for nouse in uselessinfo:
        #data = re.sub(nouse+"[\d\.:]+", "", data)
        data = data.replace(nouse, "")
    n = re.search(name+":([\d\.]+)", data)
    len1 = float(n.group(1))
    p = re.findall("\)([\d\.\:]+)", data)
    len2 = 0
    for num in p:
        if ":" not in num:
            len2 += float(num)
        else:
            m = re.search("([\d\.]+):([\d\.]+)", num)
            len2 += float(m.group(2))

    return(len1,len2+len1)

#获取最小共享分支
def GetMinClade(info):
    fbindex = []
    rbindex = []
    data2return = []
    index = 0
    while index < len(info):
        if info[index] == "(":
            fbindex.append(index)
        if info[index] == ")":
            rbindex.append(index)
        index += 1
    index1 = 0
    while index1 < len(fbindex):
            index2 = 0
            while index2 < len(rbindex):
                if fbindex[index1]< rbindex[index2]:
                    data = info[fbindex[index1]+1:rbindex[index2]]
                    if ")" not in data and "(" not in data:
                        data2return.append(data)
                index2 += 1
            index1 += 1
    return data2return

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


################
##主程序
print("Content-Type: text/html; charset=utf-8\n\n")
form = cgi.FieldStorage()
try:
    nwkdata = form["nwkinfo"].value
except:
    print("<h2 style=\"color:red;font-size:20px\"> The Newick information cannnot be blank</h2>")

nwkdata = nwkdata.strip()
nwkdata2 = ''
for line in nwkdata.splitlines():
    line = line.strip()
    line = re.sub("\s+", "", line)
    if line == '':
        continue
    else:
        nwkdata2 += line
nwkdata = nwkdata2

(AllGeneName, AllCladeLen) = GetCladeNumLength(nwkdata)
MaxCladeLength = 0
#print("该系统进化树中的所有基因名、本身支长及其到根部的支长为: ")
for name in AllGeneName:
    #print(name, ":%.4f - %.4f" % (AllCladeLen[name][0], AllCladeLen[name][1]))
    if MaxCladeLength < AllCladeLen[name][1]:
        MaxCladeLength = AllCladeLen[name][1]

#print("该系统进化树的最长分支长度为: %.4f" % MaxCladeLength)
#print()
#print("-"*25)

#print(nwkdata)
GeneInterval = float(form["GeneInterval"].value)    #相邻分支间距
FontSize = float(form["FontSize"].value)            #基因名字号
MaxCladePx = float(form["MaxCladePx"].value)        #最长分支画图长度
painty0 = 25                                        #起始y轴位置
paintx0=25                                          #起始x轴位置
linecolor = form["linecolor"].value                 #线颜色
genecolor = form["genecolor"].value                 #基因名颜色
bootcolor = form["bootcolor"].value                 #bootstrap值颜色
nameback = 10                                       #基因名与线距离
strokewidth = float(form["strokewidth"].value)      #线宽
textdown = 6                                        #基因名名称下移量
scalestrokewidth = 2                                #比例尺线宽
scaleunit = float(form["scaleunit"].value)          #比例尺大小
scalecolor = form["scalecolor"].value               #比例尺颜色
scaletextcolor = form["scaletextcolor"].value       #比例尺字体颜色
unit = MaxCladePx/MaxCladeLength

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
try:
    protinfo = form["proteininfo"].value
except:
    print("<h2 style=\"color:red;font-size:20px\"> The information of protein structure cannnot be blank</h2>")
protinfo = protinfo.strip()
data = protinfo.splitlines()

if len(data[0].split()) != 5:
    print("<h2 style=\"color:red;font-size:20px\"> The information format of protein structure is illegal</h2>")
aalength = form["pxperaa"].value
try:
    aalength = float(aalength)
except:
    pass

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
# 获取最长蛋白
maxlength = ProtLenDic[proteinlist[0]]
maxprot = proteinlist[0]
for key in sorted(ProtLenDic.keys()):
    if maxlength < ProtLenDic[key]:
        maxlength = ProtLenDic[key]
        maxprot = key

domainpaintx0 = MaxCladePx + 200

svgheight = GeneInterval * len(AllGeneName) + 100
svgweihht = domainpaintx0 + maxlength * aalength + 25
treepaint = svgwrite.Drawing("tmp.nwk.domain.svg", (svgweihht, svgheight) )
#treepaint.add(treepaint.text("test tree", insert=(20, 20), font_size = 16,fill = 'red'))
#找出每一个基因的y轴绘图位置
AllGenePy = {}
y = painty0
for gene in AllGeneName:
    AllGenePy[gene]=y
    y += GeneInterval

cladeid = 1
two = 1
flag = True
while flag:
    minclaseinfo = GetMinClade(nwkdata) #找出没有嵌套括号的括号内容
    for mininfo in minclaseinfo:
        if mininfo.count(":") > 2:
            flag = False
            last = re.findall("([a-zA-Z0-9\-/_#]+):", mininfo)
            miny = AllGenePy[last[0]]
            maxy = AllGenePy[last[0]]
            for ln in last:
                treepaint.add(treepaint.line(
                    ((AllCladeLen[ln][1]-AllCladeLen[ln][0]) * unit + paintx0, AllGenePy[ln]),
                    (AllCladeLen[ln][1] * unit + paintx0, AllGenePy[ln]),
                    stroke_width=strokewidth,
                    stroke=linecolor))
                if "#" not in ln and "merge" not in ln:
                    treepaint.add(treepaint.text(ln, insert=(AllCladeLen[ln][1] * unit + paintx0 + nameback, AllGenePy[ln]+textdown), font_size = FontSize,fill = genecolor))
                if miny > AllGenePy[ln]:
                    miny = AllGenePy[ln]
                if maxy < AllGenePy[ln]:
                    maxy = AllGenePy[ln]
            treepaint.add(treepaint.line(
                        (paintx0, miny - strokewidth / 2.0),
                        (paintx0, maxy + strokewidth / 2.0),
                        stroke_width=strokewidth,
                        stroke=linecolor))
            break
        clademergeid = "#"+str(cladeid)+"merge"
        m = re.search("^(.+):([\d\.]+),(.+):([\d\.]+)", mininfo)
        treepaint.add(treepaint.line(
                    ((AllCladeLen[m.group(1)][1]-AllCladeLen[m.group(1)][0]) * unit + paintx0, AllGenePy[m.group(1)]),
                    (AllCladeLen[m.group(1)][1] * unit + paintx0, AllGenePy[m.group(1)]),
                    stroke_width=strokewidth,
                    stroke=linecolor))
        if "#" not in m.group(1) and "merge" not in m.group(1):
            treepaint.add(treepaint.text(m.group(1), insert=(AllCladeLen[m.group(1)][1] * unit + paintx0 + nameback, AllGenePy[m.group(1)]+textdown), font_size = FontSize,fill = genecolor))
        treepaint.add(treepaint.line(
                    ((AllCladeLen[m.group(3)][1]-AllCladeLen[m.group(3)][0]) * unit + paintx0, AllGenePy[m.group(3)]),
                    (AllCladeLen[m.group(3)][1] * unit + paintx0, AllGenePy[m.group(3)]),
                    stroke_width=strokewidth,
                    stroke=linecolor))
        if "#" not in m.group(3) and "merge" not in m.group(3):
            treepaint.add(treepaint.text(m.group(3), insert=(AllCladeLen[m.group(3)][1] * unit + paintx0 + nameback, AllGenePy[m.group(3)]+textdown), font_size = FontSize,fill = genecolor))

        treepaint.add(treepaint.line(
                    ((AllCladeLen[m.group(1)][1]-AllCladeLen[m.group(1)][0]) * unit + paintx0, AllGenePy[m.group(1)] - strokewidth / 2.0),
                    ((AllCladeLen[m.group(3)][1]-AllCladeLen[m.group(3)][0]) * unit + paintx0, AllGenePy[m.group(3)] + strokewidth / 2.0),
                    stroke_width=strokewidth,
                    stroke=linecolor))
        n = re.search(mininfo + "\)([\d\.:]+)", nwkdata)
        mergelen = 0.0
        if ":" in n.group(1):
            b = re.search("^([\d\.]+):([\d\.]+)", n.group(1))
            boot =float(b.group(1))
            mergelen = float(b.group(2))
            boot = int(boot * 100)
            chnum = len(str(boot))
            treepaint.add(treepaint.text(str(boot), insert=((AllCladeLen[m.group(1)][1]-AllCladeLen[m.group(1)][0]) * unit + paintx0 - chnum * 8, (AllGenePy[m.group(1)] + AllGenePy[m.group(3)])/2.0 - 4), font_size = FontSize - 2, fill = bootcolor))
            nwkdata = nwkdata.replace("("+mininfo+")"+b.group(1), clademergeid)
        else:
            nwkdata = nwkdata.replace("("+mininfo+")", clademergeid)
            mergelen = float(n.group(1))
        AllCladeLen[clademergeid] = ([mergelen, AllCladeLen[m.group(1)][1]-AllCladeLen[m.group(1)][0]])
        AllGenePy[clademergeid] = (AllGenePy[m.group(1)] + AllGenePy[m.group(3)])/2.0
        cladeid += 1
    two += 1

#比例尺绘画
treepaint.add(treepaint.line(
    (paintx0 + 25, svgheight - 50),
    (paintx0 + 25 + scaleunit * unit, svgheight - 50),
    stroke_width = scalestrokewidth,
    stroke = scalecolor))
treepaint.add(treepaint.line(
    (paintx0 + 25, svgheight - 50 - scalestrokewidth * 4),
    (paintx0 + 25, svgheight - 50 + scalestrokewidth * 4),
    stroke_width = scalestrokewidth,
    stroke = scalecolor))
treepaint.add(treepaint.line(
    (paintx0 + 25 + scaleunit * unit, svgheight - 50 - scalestrokewidth * 4),
    (paintx0 + 25 + scaleunit * unit, svgheight - 50 + scalestrokewidth * 4),
    stroke_width = scalestrokewidth,
    stroke = scalecolor))
treepaint.add(treepaint.text(
    str(scaleunit),
    insert = (paintx0 + 25 + scaleunit * unit * 0.5 - len(str(scaleunit)) * 6 * 0.5, svgheight - 35),
    font_size = FontSize,
    fill = scaletextcolor))

#蛋白结构域绘制
for protname in proteinlist:
    if protname not in AllGeneName:
        continue
    #绘制蛋白总长
    protinfo = GetProtInfo(protname, 'protein', data)
    for info in protinfo:
        (start, end) = info.split("--")
        start = int(start)
        end = int(end)
        length = end - start + 1
        length = length * aalength
        treepaint.add(treepaint.line(
            ((start - 1) * aalength + domainpaintx0 + 1, AllGenePy[protname] ),
            ((end - 1) * aalength + domainpaintx0 + 1, AllGenePy[protname]),
            stroke_width = 3,
            stroke = "gray",
            fill = "gray",
            opacity = 1.0  #不透明度（待添加功能）
            ))
    #绘制domain
    domaininfo = GetDomainInfo(protname, 'domain', data)
    doheight = form["domainheight"].value
    height = float(doheight)
    for line in domaininfo:
        (domain, aa1, aa2) = line.split("--")
        aa1 = int(aa1)
        aa2 = int(aa2)
        length= aa2 - aa1 + 1
        vertical_gradient_domain = treepaint.linearGradient((0, 0), (0, 1))
        treepaint.defs.add(vertical_gradient_domain)
        vertical_gradient_domain.add_stop_color(0, tagcolors[domain])
        vertical_gradient_domain.add_stop_color(1, 'white')
        treepaint.add(treepaint.rect(
                insert = ((aa1 - 1) * aalength + domainpaintx0 + 1, AllGenePy[protname] - height/2),
                size = (str(length * aalength) + "px", doheight + "px"),
                stroke_width = 1,
                stroke = "black",
                fill = vertical_gradient_domain.get_paint_server(default='currentColor')
            ))


treepaint.save()
print("SVG editing tool: Inkscape(powerful, free, open source, general purpose)<br>\n")
print("Download:<br> <a href=https://inkscape.org>https://inkscape.org</a> <br><br>\n")
print("<img src=\"tmp.nwk.domain.svg\"  alt=\"svg结构成果图\"/>")
