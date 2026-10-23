"""Generate a deliberately TAMPERED certificate PDF for demo purposes.

Copies the real record for CC-2024-53537-WSU but alters CGPA and course,
so the verification engine should flag it as TAMPERED.
"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

OUT = "fake_certificate_TAMPERED.pdf"

fields = [
    ("Credential ID:", "CC-2024-53537-WSU"),
    ("Student Full Name:", "Priya Sharma"),
    ("Roll Number:", "AD2026-001"),
    ("Issue Date:", "2026-10-23"),
    ("CGPA:", "10.0"),  # TAMPERED (real: 9.8)
    ("Course / Academic Degree:", "Master of Technology in Artificial Intelligence"),  # TAMPERED
    ("Institution:", "MMCOE"),
]

c = canvas.Canvas(OUT, pagesize=landscape(A4))
w, h = landscape(A4)
c.setFont("Helvetica-Bold", 26)
c.drawCentredString(w / 2, h - 80, "Certificate of Academic Achievement")
c.setFont("Helvetica", 12)
c.drawCentredString(w / 2, h - 105, "Office of the Registrar - MMCOE")

y = h - 170
for label, value in fields:
    c.setFont("Helvetica-Bold", 13)
    c.drawString(90, y, label)
    c.setFont("Helvetica", 13)
    c.drawString(300, y, value)
    y -= 34

c.save()
print("Wrote", OUT)
