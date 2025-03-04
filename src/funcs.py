import os

import json
import qrcode

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

styles = getSampleStyleSheet()

pdfmetrics.registerFont(TTFont('calibri', "./docs/calibri.ttf"))

RECEIPT_POS = [1, 210, 419, 628]  # Позиции по вертикали (y) для каждой квитанции
GROUP_NAME_POS = [] # x, y
PAGE_POS = [] # x, y
def create_receipt(json_data: str, FilePDF:str='Квитанции.pdf'):
    c = canvas.Canvas(FilePDF, pagesize=A4)

    try:
        json_data = json.loads(json_data)
    except json.JSONDecodeError:
        return 'Ошибка при парсинге JSON'
    
    if len(json_data["Data"]) == 0:
        return 'Нет информации о плательщиках'
    
    receipt_index = 1
    page = 1
    for group in json_data['Data']:
        for payer in group:
            if json_data['Data'][group]["Data"][payer]["SumTotal"] > 0:
                if receipt_index == 1:
                    if json_data['Data'][group]['Group']:
                        c.drawString(GROUP_NAME_POS[0], GROUP_NAME_POS[1], json_data['Data'][group]['Group'])
                    c.drawString(PAGE_POS[0], PAGE_POS[1], page)
                




    
                
