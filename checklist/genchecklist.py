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
\usepackage{hyperref}
\usepackage{url}
\usepackage[T1]{fontenc}
\usepackage{inconsolata}
\usepackage[scaled]{helvet} % see www.ctan.org/get/macros/latex/required/psnfss/psnfss2e.pdf
\setlength{\arrayrulewidth}{.05em}
\usepackage{titlesec}
\titleformat*{\paragraph}{\normalsize\color{gray}\sffamily\bfseries}
\usepackage{flushend}
\usepackage{hyperref}
\hypersetup{colorlinks=true,urlcolor=cyan}

\newlength{\cellpad}\setlength{\cellpad}{2.1ex}
\newlength{\rowheight}\setlength{\rowheight}{2.1cm}
\newlength{\figwidth}\setlength{\figwidth}{1.65cm}
\newlength{\descwidth}\setlength{\descwidth}{.30\textwidth}

\newcommand{\checkbox}{{\hspace*{.3ex}\setlength{\fboxrule}{0.125pt}\raisebox{-.6ex}{\fcolorbox{black}{white}{\rule{0pt}{2ex}\hspace{2ex}}}}}
\newlength{\vcbsize}
\newcommand{\verticalwithcheckbox}[2]{\setlength{\vcbsize}{\dimexpr(\rowheight*#1)\relax}\multirow{-#1}{*}{\hspace*{-.5ex}\smash{\rotatebox[origin=l]{90}{\hspace*{-1ex}\mbox{\parbox{\vcbsize}{\centering \normalsize #2\hspace*{1ex}\checkbox \\{\raisebox{-0ex}{\scriptsize Example Problems}}}}}}}}

\begin{document}
\pagenumbering{gobble}
\sffamily

\begin{center}
  \textbf{\huge $title {\normalsize $version}}\\
  \textit{\color{gray} \scriptsize $subtitle}
\end{center}

\scriptsize
\begin{centering}
  \arrayrulecolor{white}
  \begin{tabular}{c|cccc|cc}
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
  \cellcolor{$color}\includegraphics[width=\figwidth]{$figure} &
  \cellcolor{$color}
  \begin{minipage}[b][\rowheight][t]{\descwidth}\vspace{1em}
    \color{darkgray}
    \textbf{$name}\\
    $description
  \end{minipage}"""

# latex group name and checkbox in rotated box
ltxgroupname = r"""\verticalwithcheckbox{$rows}{$name}"""

# latex epilog
ltxepilog = r"""
  \end{tabular}
\end{centering}
\vspace*{-4ex}
\scriptsize \href{$pdfurl}{\hspace*{-0ex}\raisebox{-.25cm}{\includegraphics[width=.75cm]{pdf.png}}}~PDF: \url{$url} \hfill $date. $credits
\twocolumn
\begin{center}
  \textbf{\color{gray}\huge FAQ}
\end{center}
\color{gray}\small
\paragraph{Why a checklist?}
Our goal is to help ensure that current, accepted best practices are followed. Per the \href{https://en.wikipedia.org/wiki/The_Checklist_Manifesto}{Checklist Manifesto}, checklists help to do exactly this. Our interest is the good practices for carrying out empirical evaluations as part of PL research. While some practices are clearly wrong, many require careful consideration: Not every case under every category in the checklist applies to every evaluation -- expert judgment is required. The checklist is meant to assist expert judgment, not substitute for it. \href{http://www.everup.com/2016/01/25/about-the-checklist-manifesto-atul-gawande-takeaways/}{`Failure isn't due to ignorance. According to best-selling author Atul Gawande, it's because we haven't properly applied what we already know.'} We've kept the list to a single page to make it easier to use and refer back to.

\paragraph{Why now?}
When best practices are not followed, there is a greater-than-necessary risk that the benefits reported by an empirical evaluation are illusory, which harms further progress and stunts industry adoption. The members of the committee have observed many recent cases in which practices in the present checklist are not followed. Our hope is that this effort will help focus the community on presenting the most appropriate evidence for a stated claim, where the form of this evidence is based on accepted norms.

\paragraph{Is use of the checklist going to be formally integrated into SIGPLAN conference review processes?}
There are no plans to do so, but in time, doing so may make sense.

\paragraph{How do you see authors using this checklist?}
We believe the most important use of the checklist is to assist authors in carrying out a meaningful empirical evaluation.

\paragraph{How do you see reviewers using this checklist?}

We also view the checklist as a way to remind reviewers of important elements of a good empirical evaluation, which they can take into account when carrying out their assessment. However, we emphasize that proper use of the checklist requires nuance. Just because a paper has every box checked doesn't mean it should be accepted. Conversely, a paper with one or two boxes unchecked may still merit acceptance. Even whether a box is checked or not may be subject to debate. The point is to organize a reviewer's thinking about an empirical evaluation to reduce the chances than an important aspect is overlooked. When a paper fails to check a box, it deserves some scrutiny in that category.

\paragraph{How did you determine which items to include?}

The committee examined a sampling of papers from the last several years of ASPLOS, ICFP, OOPSLA, PLDI, and POPL, and considered those that contained some form of empirical evaluation. We also considered past efforts examining empirical work (Gernot Heiser's \href{https://www.cse.unsw.edu.au/~gernot/benchmarking-crimes.html}{``Systems Benchmarking Crimes''}, the \href{https://dl.acm.org/citation.cfm?id=2983574}{``Pragmatic Guide to Assessing Empirical Evaluations''}, and the \href{http://evaluate.inf.usi.ch/}{``Evaluate Collaboratory''}). Through regular discussions over several months, we identified common patterns and anti-patterns, which we grouped into the present checklist. Note that we explicitly did not intend for the checklist to be exhaustive; rather, it reflects what appears to us to be common in PL empirical evaluations.

\paragraph{Why did you organize the checklist as a series of categories, each with several cases?}

The larger categories represent the general breadth of evaluations we saw, and the cases are intended to be helpful in being concrete, and common. For less common empirical evaluations, other cases may be relevant, even if not presented in the checklist explicitly. For example, for work studying human factors, the Adequate Data Analysis category might involve cases focusing on the use of statistical tests to relate outcomes in a control group to those in an experimental group. More on this kind of work below.\vspace*{2ex}

\paragraph{Why did you use checkboxes instead of something more nuanced, like a score?}

The boxes next to each item are not intended to require a binary ``yes/no'' decision. In our own use of the list, we have often marked entries as partially filling a box (e.g., with a dash to indicate a ``middle'' value) or by coloring it in (e.g., red for egregious violation, green for pass, yellow for something in the middle).

\paragraph{What about human factors or other areas that require empirical evaluation?}

PL research sometimes involves user studies, and these are different in character than, say, work that evaluates a new compiler optimization or test generation strategy. Because user studies are currently relatively infrequent in the papers we examined, we have not included them among the category cases. It may be that new, different cases are required for such studies, or that the present checklist will evolve to contain examples drawn from user studies. Nonetheless, the seven category items are broadly applicable and should be useful to authors of any empirical evaluation for a SIGPLAN conference.

\paragraph{How does the checklist relate to the \href{http://www.artifact-eval.org/}{artifact evaluation process?}}

Artifact evaluation typically occurs after reviewing a paper, to check that the claims and evidence given in the paper match reality, in the artifact. The checklist is meant to be used by reviewers while judging the paper, and by authors when carrying out their research and writing their paper.

\paragraph{How will this checklist evolve over time?}

Our manifesto is: Usage should determine content. We welcome feedback from users of the checklist to indicate how frequently they use certain checklist items or how often papers reviewed adhere to them. We also welcome feedback pointing to papers that motivate the inclusion of new items. As the community increasingly adheres to the guidelines present in the checklist, the need for their inclusion may diminish. We also welcome feedback on presentation: please share points of confusion about individual items, so we can improve descriptions or organization.

\end{document}
"""

#
# Generate the latex for the whole document
#
def genlatex(ltxfile,title,subtitle,version,url,pdfurl,credits,date,halfrows,halfrulecolor):
    with open(ltxfile,'w') as f:
        t=Template(ltxprolog)
        if version:
            version = "("+version+")"
        f.write(t.substitute({ 'title': title, 'version': version, 'subtitle': subtitle}))
        
        rows = int((len(halfrows)+1)/2)
        t=Template(ltxrow)
        for r in range(0, rows):
            f.write(t.substitute({ 'halfrowl' : halfrows[r], 'halfrowr' : halfrows[r+rows], 'colorl' : halfrulecolor[r], 'colorr' : halfrulecolor[r+rows] }))
            
        t=Template(ltxepilog)
        f.write(t.substitute({ 'url': url, 'pdfurl': pdfurl, 'date': date, 'credits': credits}))
    f.closed
    
#
# Process a complete checklist group, creating half-rows and rule colors
#
def processgroup(group, halfrows, halfrulecolor):
    color=group['color']
    keyword=group['keyword']
    name=group['name'].replace(keyword, "\\textbf{"+keyword+"}")
    # filter out those items that are to be included in the printed checklist
    ltxitems = []
    for i in range(0, len(group['items'])):
        if group['items'][i]['include']:
            ltxitems.append(group['items'][i])
    count=len(ltxitems)
    for i in range(0, count):
        item=ltxitems[i]
        if item['include']:
            ltx="% checklist item '"+item['name']+"'\n  \cellcolor{"+color+"}"
            if (i == count - 1):
                t=Template(ltxgroupname)
                ltx+= t.substitute({ 'rows' : str(count), 'keyword' : keyword, 'name' : name})
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
    genlatex(ltxfile,i['title'],i['subtitle'],i['version'],i['url'],i['pdfurl'],i['credits'],i['date'],halfrows,halfrulecolor)


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
