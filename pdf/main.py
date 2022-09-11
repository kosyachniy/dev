from pdflatex import PDFLaTeX

pdfl = PDFLaTeX.from_texfile('data/main.tex')

# pdf, log, completed_process = pdfl.create_pdf(keep_pdf_file=True, keep_log_file=True)
pdf, log, cp = pdfl.create_pdf()

print(pdf, log, cp)
