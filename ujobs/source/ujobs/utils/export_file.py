#!/usr/bin/env python
# -*- coding:utf-8 -*-

# --------------------------------
# Author: wx
# Date: 2015/7/13
# Usage: export file
# --------------------------------

from django.http import HttpResponse

def download_csv_file(request):
    # CSV  
    import csv      
    response = HttpResponse(mimetype='text/csv')  
    response['Content-Disposition'] = 'attachment; filename=my.csv'  
    writer = csv.writer(response)  
    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])  
    writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])  
    return response

def download_txt_file(request,content,filename):
    # Text file  
    response = HttpResponse()
    response["Content-Type"] = "txt/plain; charset=utf-8" 
    response["Content-Disposition"] = 'attachment; filename=%s'%filename
    response.write(content)
    return response

def download_pdf_file(request):
    # PDF file   
    #http://code.djangoproject.com/svn/django/branches/0.95-bugfixes/docs/outputting_pdf.txt  
#     from reportlab.pdfgen import canvas
#     response = HttpResponse(mimetype='application/pdf')  
#     response['Content-Disposition'] = 'attachment; filename=somefilename.pdf'  
#     p = canvas.Canvas(response)  
#     p.drawString(100, 100, "Hello world.")  
#     p.showPage()  
#     p.save()  
#     return response        
    