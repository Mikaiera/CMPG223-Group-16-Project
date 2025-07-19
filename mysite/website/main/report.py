from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import reportlab 

# Create a PDF object and specify the file name
pdf_file = "example.pdf"
pdf = canvas.Canvas(pdf_file, pagesize=letter)

# Set the title and add some text
pdf.setTitle("My PDF Document")
pdf.drawString(100, 750, "Hello, World!")
pdf.drawString(100, 735, "This is an example PDF created with reportlab.")

# Draw a line
pdf.line(100, 720, 500, 720)

# Draw a rectangle
pdf.rect(100, 600, 400, 100)

# Add more text within the rectangle
pdf.drawString(110, 670, "This is some text inside a rectangle.")
pdf.drawString(110, 655, "You can customize the content as needed.")

# Save the PDF
pdf.save()

print(f"PDF created: {pdf_file}")
