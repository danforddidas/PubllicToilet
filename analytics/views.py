import io
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from .models import ToiletStatus


def dashboard(request):
    """Automatically populates the 4 toilets if empty, then loads dashboard with graph data."""
    if not ToiletStatus.objects.exists():
        for i in range(1, 5):
            ToiletStatus.objects.create(toilet_id=i, is_occupied=False)

    toilets = ToiletStatus.objects.all().order_by('toilet_id')

    # Peak weekly analytics data (Simulated total uses per day for the week)
    weekly_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_data = [45, 58, 72, 50, 85, 95, 40]  # Saturday (95) is our highest peak usage day!

    context = {
        'toilets': toilets,
        'weekly_labels': weekly_labels,
        'weekly_data': weekly_data,
    }
    return render(request, 'analytics/dashboard.html', context)


def toggle_status(request, id):
    """Simulates sensor triggers by flipping the toilet occupancy state."""
    toilet = get_object_or_404(ToiletStatus, toilet_id=id)
    toilet.is_occupied = not toilet.is_occupied
    toilet.save()
    return redirect('dashboard')


def generate_pdf(request):
    """Generates a weekly PDF report featuring cards and a custom vector weekly traffic bar graph."""
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer)
    p.setPageSize((595, 842))  # Standard A4 Document Size

    # ---------------------------------------------------------
    # 1. HEADER BANNER
    # ---------------------------------------------------------
    p.setFillColor(HexColor("#1e293b"))
    p.rect(0, 740, 595, 102, fill=True, stroke=False)

    p.setFillColor(HexColor("#ffffff"))
    p.setFont("Helvetica-Bold", 22)
    p.drawString(40, 795, "SMART PUBLIC TOILET SYSTEM")

    p.setFont("Helvetica", 11)
    p.setFillColor(HexColor("#cbd5e1"))
    p.drawString(40, 775, "Weekly Usage Analytics & Peak Traffic Performance Charts")

    # ---------------------------------------------------------
    # 2. REAL-TIME TOILET STATES (CARD WRAPPERS)
    # ---------------------------------------------------------
    p.setFillColor(HexColor("#0f172a"))
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, 715, "Current System Module Statuses")

    y_position = 655
    for t in ToiletStatus.objects.all().order_by('toilet_id'):
        if t.is_occupied:
            status_text = "OCCUPIED"
            badge_bg = HexColor("#f8d7da")
            badge_text = HexColor("#721c24")
        else:
            status_text = "AVAILABLE"
            badge_bg = HexColor("#d4edda")
            badge_text = HexColor("#155724")

        # Draw background container row
        p.setStrokeColor(HexColor("#e2e8f0"))
        p.setFillColor(HexColor("#f8fafc"))
        p.roundRect(40, y_position - 12, 515, 42, 4, fill=True, stroke=True)

        p.setFillColor(HexColor("#334155"))
        p.setFont("Helvetica-Bold", 11)
        p.drawString(55, y_position + 14, f"Toilet Unit Module #{t.toilet_id}")

        p.setFont("Helvetica-Oblique", 8.5)
        p.setFillColor(HexColor("#64748b"))
        p.drawString(55, y_position,
                     f"Last sensor synchronization state change: {t.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")

        # Draw status indicator pill badge
        p.setFillColor(badge_bg)
        p.roundRect(445, y_position + 1, 90, 20, 3, fill=True, stroke=False)

        p.setFillColor(badge_text)
        p.setFont("Helvetica-Bold", 9)
        p.drawCentredString(490, y_position + 7, status_text)

        y_position -= 52

    # ---------------------------------------------------------
    # 3. WEEKLY TRAFFIC PEAK BAR CHART GRAPHICS
    # ---------------------------------------------------------
    # Move further down past the module rows
    chart_y = y_position - 20

    p.setStrokeColor(HexColor("#e2e8f0"))
    p.line(40, chart_y + 40, 555, chart_y + 40)

    p.setFillColor(HexColor("#0f172a"))
    p.setFont("Helvetica-Bold", 13)
    p.drawString(40, chart_y + 15, "Weekly Traffic Distribution (Peak Identification)")

    # Dataset values matching our simulation setup
    weekly_dataset = [
        {"day": "Monday", "uses": 45},
        {"day": "Tuesday", "uses": 58},
        {"day": "Wednesday", "uses": 72},
        {"day": "Thursday", "uses": 50},
        {"day": "Friday", "uses": 85},
        {"day": "Saturday", "uses": 95},  # Peak Highest Day
        {"day": "Sunday", "uses": 40}
    ]

    # Find maximum usage value dynamically to set the highlight color
    max_uses = max(item["uses"] for item in weekly_dataset)

    bar_y = chart_y - 20
    for data in weekly_dataset:
        # Label text positioning
        p.setFillColor(HexColor("#475569"))
        p.setFont("Helvetica-Bold", 10)
        p.drawString(40, bar_y + 4, data["day"])

        # Calculate dynamic horizontal bar width length based on value (scaling multiplier)
        bar_width = data["uses"] * 3.2

        # Highlight peak day (Saturday) in an explicit bright color, others regular gray-blue
        if data["uses"] == max_uses:
            p.setFillColor(HexColor("#ef4444"))  # Bright Red alert color for peak day
        else:
            p.setFillColor(HexColor("#3b82f6"))  # Clean standard chart Blue

        # Draw the solid vector chart block row
        p.roundRect(140, bar_y, bar_width, 14, 2, fill=True, stroke=False)

        # Overlay count text to the right of each individual bar line
        p.setFillColor(HexColor("#64748b"))
        p.setFont("Helvetica-Bold", 9)
        p.drawString(145 + bar_width, bar_y + 3, f"{data['uses']} uses")

        # Step down to avoid overlapping chart bars
        bar_y -= 26

    # ---------------------------------------------------------
    # 4. FOOTER RUNNING HEADERS
    # ---------------------------------------------------------
    p.setStrokeColor(HexColor("#1e293b"))
    p.setLineWidth(1.5)
    p.line(40, 45, 555, 45)

    p.setFillColor(HexColor("#94a3b8"))
    p.setFont("Helvetica", 8.5)
    p.drawString(40, 30,
                 "System Notice: Peak usage analytics are auto-compiled based on simulated gateway traffic logs.")
    p.drawRightString(555, 30, "Page 1 of 1")

    p.showPage()
    p.save()

    buffer.seek(0)
    pdf_data = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="weekly_toilet_report.pdf"'
    return response