from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
import os

def generate_receipt(user, event):
    receipt_dir = os.path.join(settings.MEDIA_ROOT, "receipts")
    os.makedirs(receipt_dir, exist_ok=True)

    filename = f"receipt_{user.id}_{event.id}.pdf"
    file_path = os.path.join(receipt_dir, filename)

    c = canvas.Canvas(file_path, pagesize=A4)
    text = c.beginText(50, 800)

    text.textLine("Event Payment Receipt")
    text.textLine("-------------------------")
    text.textLine(f"User: {user.username}")
    text.textLine(f"Event: {event.title}")
    text.textLine(f"Amount Paid: ₹{event.price}")
    text.textLine("Status: Paid")

    c.drawText(text)
    c.showPage()
    c.save()

    return f"receipts/{filename}"
