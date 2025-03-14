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
GROUP_NAME_POS = [-835, 580] # x, y
PAGE_POS = [580, 7] # x, y
def create_receipt(json_data: dict, FilePDF:str='Report.pdf'):

    if json_data["Filename"]:
        FilePDF = json_data["Filename"]

    c = canvas.Canvas(FilePDF, pagesize=A4)

    def exchange(sum:int):
        return f"{sum // 100} руб. {sum/100 - sum //100} коп."
    
    def draw_receipt(y_pos, PayerData):
        c.rect(10, y_pos+4, 560, 205)
        c.rect(10, y_pos+4, 120, 205)
        c.rect(130, y_pos+158, 440, 17)
        c.rect(130, y_pos+101, 440, 30)
        c.rect(130, y_pos+63, 440, 15)
        c.rect(130, y_pos+25, 440, 23)

        img = qrcode.make(PayerData["QrCodeText"])
        img.save(f"temp_{PayerData['Payer']}.png")
        c.drawImage(f"temp_{PayerData['Payer']}.png", 13, y_pos+54, 114, 114)

        c.setFont('calibri', 10)
        c.drawString(44, y_pos + 184, "Извещение")
        c.drawString(485, y_pos + 199, "Форма №пд-4")
        c.drawString(135, y_pos + 199, json_data['BankTitle'])
        c.drawString(135, y_pos + 179, json_data['Org'])
        c.drawString(140, y_pos + 162, json_data['OrgInn'])
        c.drawString(230, y_pos + 162, "КПП")
        c.drawString(330, y_pos + 162, "№ " + json_data['AccNumb'])
        c.drawString(135, y_pos + 135, json_data['Bankname'])
        c.drawString(285, y_pos + 135, "БИК " + json_data['BankBic'])
        c.drawString(135, y_pos + 116, "ОКТМО")
        c.drawString(195, y_pos + 116, "КБК")
        c.drawString(135, y_pos + 105, PayerData['Purpose'])
        c.drawString(135, y_pos + 81, "Ф.И.О. плательщика")
        c.drawString(235, y_pos + 81, PayerData['Payer'])
        c.drawString(135, y_pos + 67, "Адрес плательщика")
        c.drawString(235, y_pos + 67, PayerData['PayerAddress'])
        c.drawString(135, y_pos + 52, "ИНН плательщика")
        c.drawString(235, y_pos + 52, PayerData['PayerInn'])
        c.drawString(135, y_pos + 39, "Сумма платежа")
        c.drawString(210, y_pos + 39, exchange(PayerData['SumPayment']))
        c.drawString(295, y_pos + 39, f"Сумма платы за услуги    {exchange(PayerData['SumService'])}")
        c.drawString(135, y_pos + 29, "Итого")
        c.drawString(210, y_pos + 29, exchange(PayerData['SumTotal']))
        c.drawString(295, y_pos + 29, f"Дата    {PayerData['Date']}")
        
        c.setFont('calibri', 7)
        c.drawString(135, y_pos + 19, "С условиями приёма указанной в платежном документе суммы, в т.ч. с суммой взимаемой платы за услуги банка, ознакомлен и согласен")
        c.drawString(135, y_pos + 8, "Подпись плательщика ________________")
        c.drawString(270, y_pos + 170, "(наименование получателя платежа)")
        c.drawString(135, y_pos + 151, "(ИНН получателя платежа)")
        c.drawString(330, y_pos + 150, "(номер счета получателя платежа)")
        c.drawString(180, y_pos + 126, "(наименование банка получателя платежа)")
        c.drawString(170, y_pos + 94, "(наименование платежа)")
        c.drawString(300, y_pos + 93, "(рег.номер плательщика)")
        c.drawString(430, y_pos + 92, "(код принадлежности)")
        
        os.remove(f"temp_{PayerData['Payer']}.png")

    
    
    if len(json_data["Data"]) == 0:
        return 'Нет информации о плательщиках'
    
    receipt_index = 1
    page = 1
    for group_ind, group in enumerate(json_data['Data']):
        for payer_ind, payer in enumerate(json_data['Data'][group_ind]["Data"]):
            if json_data['Data'][group_ind]["Data"][payer_ind]["SumTotal"] > 0:
                draw_receipt(RECEIPT_POS[-1*receipt_index], json_data['Data'][group_ind]["Data"][payer_ind])
                c.setFont('calibri', 10)
                if receipt_index == 1:
                    if json_data['Data'][group_ind]['Group']:
                        c.rotate(-90)
                        c.drawString(GROUP_NAME_POS[0], GROUP_NAME_POS[1], json_data['Data'][group_ind]['Group'])
                        c.rotate(90)
                    c.drawString(PAGE_POS[0], PAGE_POS[1], f'{page}')
                    
                if receipt_index == 4:
                    receipt_index = 1
                    page += 1
                    c.showPage()
                else:
                    receipt_index += 1
    
    c.save()
    return FilePDF                