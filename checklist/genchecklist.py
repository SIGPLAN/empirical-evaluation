#!/usr/bin/env python3
#
# This script will take a yaml description of a checklist and
# produce a latex file from which a pdf can be generated.
#
# The latex is encoded as template strings near the top of
# this string.
#
# Example usage:
#
# % genchecklist.py -c config.yml -l checklist.tex
# % pdflatex checklist.tex
#
#
import sys
import getopt
import yaml
import string
from string import Template

def usage(errno):
    print ('usage: ',sys.argv[0], '-c config.yml -l checklist.tex')
    sys.exit(errno)

# latex prolog
ltxprolog = r"""
\documentclass{article}
\usepackage[left=1cm, right=1cm, top=1cm, bottom=1cm]{geometry}
\usepackage{multirow}
\usepackage[svgnames]{xcolor}
\usepackage{colortbl}
\usepackage{array}
\usepackage{svg}
\usepackage{graphicx}
\usepackage{hhline}
\usepackage[scaled]{helvet} % see www.ctan.org/get/macros/latex/required/psnfss/psnfss2e.pdf
\setlength{\arrayrulewidth}{.15em}

\begin{document}
\pagenumbering{gobble}
\sffamily

\begin{center}
  \textbf{\huge $title {\normalsize ($version)}}
\end{center}

\scriptsize
\begin{centering}
  \begin{tabular}{ccccccc}
"""

# latex row
ltxrow =  r"""
  $halfrowl&
  &

  $halfrowr%
  \\ \hhline{>{\arrayrulecolor{$colorl}}->{\arrayrulecolor{white}}-->{\arrayrulecolor{white}}->{\arrayrulecolor{$colorr}}->{\arrayrulecolor{white}}--}
"""

# latex halfrow
ltxhalfrow = r"""&
  \cellcolor{$color}\includegraphics[width=1.8cm]{$figure} &
  \cellcolor{$color}
  \begin{minipage}[b][2.1cm][t]{.305\textwidth}\vspace{1em}
    \textbf{\small $name}\\
    $description
  \end{minipage}"""

# latex group name and checkbox in rotated box
ltxgroupname = r"""  % vertical text for group $keyword (placed in last row because subsequent \cellcolor macros will overwrite it otherwise)
  \multirow{-$rows}{*}{\smash{\rotatebox[origin=tl]{90}{\hspace{-2ex}\normalsize {\setlength{\fboxrule}{0.125pt}\raisebox{.5ex}{\fcolorbox{black}{white}{\rule{0pt}{.5ex}~}}}~~~$name}}}"""

# latex epilog
ltxepilog = r"""
  \end{tabular}
\end{centering}
\vfill
\hfill \scriptsize $date. $credits
\end{document}
"""

#
# Generate the latex for the whole document
#
def genlatex(ltxfile,title,version,credits,date,halfrows,halfrulecolor):
    with open(ltxfile,'w') as f:
        t=Template(ltxprolog)
        f.write(t.substitute({ 'title': title, 'version': version}))
        
        rows = int((len(halfrows)+1)/2)
        t=Template(ltxrow)
        for r in range(0, rows):
            f.write(t.substitute({ 'halfrowl' : halfrows[r], 'halfrowr' : halfrows[r+rows], 'colorl' : halfrulecolor[r], 'colorr' : halfrulecolor[r+rows] }))
            
        t=Template(ltxepilog)
        f.write(t.substitute({ 'date': date, 'credits': credits}))
    f.closed
    
#
# Process a complete checklist group, creating half-rows and rule colors
#
def processgroup(group, halfrows, halfrulecolor):
    color=group['color']
    keyword=group['keyword']
    name=group['name'].replace(keyword, "\\textbf{"+keyword+"}")
    items=len(group['items'])
    for i in range(0, items):
        item=group['items'][i]
        ltx="% checklist item '"+item['name']+"'\n  \cellcolor{"+color+"}"
        if (i == items -1):
            t=Template(ltxgroupname)
            ltx+= t.substitute({ 'rows' : str(items), 'keyword' : keyword, 'name' : name})
            halfrulecolor.append('white')
        else:
            halfrulecolor.append(color)

        t=Template(ltxhalfrow)
        ltx+=t.substitute({ 'color': color, 'figure': item['figure'], 'name': item['name'], 'description': item['desc'] })
        halfrows.append(ltx)
        
#
# parse the yaml and generate the latex
#
def parseandgen(config, ltxfile):
    stream = open(config, "r")
    ol = yaml.load_all(stream)
    halfrows = []
    halfrulecolor = []
    for i in ol:
        groups=i['groups']
        for g in groups:
            processgroup(g, halfrows, halfrulecolor)
    stream.close()
    genlatex(ltxfile,i['title'],i['version'],i['credits'],i['date'],halfrows,halfrulecolor)


def main(argv):
    config = None
    ltxfile = None
  
    try:
        opts, args = getopt.getopt(argv,"c:l:",["config=","latex="])
    except getopt.GetoptError:
        usage(2)

    for opt, arg in opts:
        if opt == '-h':
            usage(0)
        elif opt in ("-c", "--config"):
            config = arg
        elif opt in ("-l", "--latex"):
            ltxfile = arg

    if config == None:
        print ('You must specify a yaml input config file')
        usage(2)
    elif ltxfile == None:
        print ('You must specify an output latex file')
        usage(2)
    else:
        parseandgen(config, ltxfile)
        
    exit(0)


if __name__ == "__main__":
   main(sys.argv[1:])
