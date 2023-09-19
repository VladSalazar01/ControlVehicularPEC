from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import csv


# Exportar a PDF
def export_generic_pdf(modeladmin, request, queryset, fields):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
        # Configuración del PDF
    p = SimpleDocTemplate(response, pagesize=A4)    
    # Datos
    data = [fields]
    for obj in queryset:
        data.append([getattr(obj, field, '') for field in fields])
    # Tabla
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))    
    p.build([t])
    return response

# Exportar a CSV
def export_generic_csv(modeladmin, request, queryset, fields):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte.csv"'    
    writer = csv.writer(response)
    writer.writerow(fields)    
    for obj in queryset:
        writer.writerow([getattr(obj, field, '') for field in fields])    
    return response
