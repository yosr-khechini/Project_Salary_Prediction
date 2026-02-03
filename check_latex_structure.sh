#!/bin/bash

echo "Checking LaTeX document structure..."
echo ""

# Count document environment
begin_doc=$(grep -c "\\begin{document}" internship_report.tex)
end_doc=$(grep -c "\\end{document}" internship_report.tex)

echo "Document environment:"
echo "  \\begin{document}: $begin_doc"
echo "  \\end{document}: $end_doc"
echo ""

# Count chapters
chapters=$(grep -c "\\chapter{" internship_report.tex)
echo "Total chapters: $chapters"
echo ""

# Count major environments
echo "Environment counts:"
echo "  itemize: $(grep -c "\\begin{itemize}" internship_report.tex) begin, $(grep -c "\\end{itemize}" internship_report.tex) end"
echo "  enumerate: $(grep -c "\\begin{enumerate}" internship_report.tex) begin, $(grep -c "\\end{enumerate}" internship_report.tex) end"
echo "  lstlisting: $(grep -c "\\begin{lstlisting}" internship_report.tex) begin, $(grep -c "\\end{lstlisting}" internship_report.tex) end"
echo ""

# Check for common LaTeX issues
echo "Basic validation:"
if [ $begin_doc -eq 1 ] && [ $end_doc -eq 1 ]; then
    echo "  ✓ Document environment is properly closed"
else
    echo "  ✗ Document environment issue detected"
fi

if [ $chapters -ge 10 ]; then
    echo "  ✓ All chapters are present ($chapters chapters)"
else
    echo "  ✗ Missing chapters (found only $chapters)"
fi

# Check file size
size=$(stat -f%z internship_report.tex 2>/dev/null || stat -c%s internship_report.tex)
if [ $size -gt 40000 ]; then
    echo "  ✓ Document has substantial content (${size} bytes)"
else
    echo "  ⚠ Document might be incomplete (${size} bytes)"
fi

echo ""
echo "Structure check complete!"
