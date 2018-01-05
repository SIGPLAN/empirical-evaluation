#!/usr/bin/env python3
import sys
import getopt
import yaml
import string

def usage(errno):
    print ('usage: ',sys.argv[0], '-c config.yml')
    sys.exit(errno)


def genlatex(title,credits,date,halfrows,halfrulecolor):
    print("\documentclass{article}\n\\usepackage[left=1cm, right=1cm, top=1cm, bottom=1cm]{geometry}\n\\usepackage{multirow}\n\\usepackage[svgnames]{xcolor}\n\\usepackage{colortbl}\n\\usepackage{array}\n\\usepackage{svg}\n\\usepackage{graphicx}\n\\usepackage[scaled]{helvet} % see www.ctan.org/get/macros/latex/required/psnfss/psnfss2e.pdf\n\\usepackage{hhline}\n\\usepackage{amssymb}\n\setlength{\\arrayrulewidth}{.15em}\n\\begin{document}\n\pagenumbering{gobble}\n\sffamily\n\\begin{center}\\textbf{\LARGE "+title+" \large (alpha version)}\end{center}\n\scriptsize\n\\begin{centering}\\begin{tabular}{ccccccc}")

    
    rows = int((len(halfrows)+1)/2)
    for r in range(0, rows):
        print(halfrows[r],"&&",halfrows[r+rows],"\\\\ \\hhline{>{\\arrayrulecolor{"+halfrulecolor[r]+"}}->{\\arrayrulecolor{white}}-->{\\arrayrulecolor{white}}->{\\arrayrulecolor{"+halfrulecolor[r+rows]+"}}->{\\arrayrulecolor{white}}--}")

    print("\end{tabular}\n\end{centering}\n\\vfill\n\hfill \scriptsize "+date+". "+credits+"\n\end{document}")


def processgroup(group, halfrows, halfrulecolor):
    color=group['color']
    keyword=group['keyword']
    name=group['name'].replace(keyword, "\\textbf{"+keyword+"}")
    items=len(group['items'])
    for i in range(0, items):
        item=group['items'][i]
        ltx="\cellcolor{"+color+"}"
        if (i == items -1):
 #           ltx+= "\multirow{-"+str(items)+"}{*}{\smash{\\rotatebox[origin=tl]{90}{\\normalsize "+name+"~~~{\large $\square$}}}}"
            ltx+= "\multirow{-"+str(items)+"}{*}{\smash{\\rotatebox[origin=tl]{90}{\hspace{-2ex}\\normalsize {\setlength{\\fboxrule}{0.125pt}\\raisebox{.5ex}{\\fcolorbox{black}{white}{\\rule{0pt}{.5ex}~}}}~~~"+name+"}}}"
#            ltx+= "\multirow{-"+str(items)+"}{*}{\smash{\\rotatebox[origin=tl]{90}{\\normalsize "+name+"}}}"
            halfrulecolor.append('white')
        else:
            halfrulecolor.append(color)
        ltx+="& \cellcolor{"+color+"}\includegraphics[width=2.1cm]{"+item['figure']+"} &\cellcolor{"+color+"}\\begin{minipage}[b][2.1cm][t]{.3\\textwidth}\\vspace{1em}\\textbf{\small "+item['name']+"}\\\\"+item['desc']+"\end{minipage}"
        halfrows.append(ltx)
        
   
def gen(config):
    stream = open(config, "r")
    ol = yaml.load_all(stream)
    halfrows = []
    halfrulecolor = []
    for i in ol:
        groups=i['groups']
        for g in groups:
            processgroup(g, halfrows, halfrulecolor)
    stream.close()
    genlatex(i['title'],i['credits'],i['date'],halfrows,halfrulecolor)

def main(argv):
    config = None
  
    try:
        opts, args = getopt.getopt(argv,"c:",["config="])
    except getopt.GetoptError:
        usage(2)
    for opt, arg in opts:
        if opt == '-h':
            usage(0)
        elif opt in ("-c", "--config"):
            config = arg


    if config == None:
        print ('You must specify a config file')
        usage(2)
    else:
        gen(config)
        
    exit(0)


if __name__ == "__main__":
   main(sys.argv[1:])
