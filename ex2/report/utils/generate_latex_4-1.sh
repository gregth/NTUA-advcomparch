#!/bin/bash

filenames=`ls ../graphs/4-1/*`
for eachfile in $filenames
do
	file=${eachfile/../.}
   title=${file##*/}  # retain the part after the last slash
	title=${title/.png/}
   
   echo "
   \begin{minipage}{\textwidth}
      \begin{center}
         \fbox{\textlatin{\textbf{\textit{$title}}}}\\\\
         \vspace{3mm}
         \includegraphics[width=0.9\textwidth, frame]{$file}
         \vspace{6mm}
      \end{center}
   \end{minipage}"
done