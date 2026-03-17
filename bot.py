from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import ttfonts
from reportlab.pdfbase import pdfmetrics

from datetime import datetime
import random

# TOKEN BOT
TOKEN = "8738092979:AAFVcuOVmkqGO4p0dlN-KT_16IEXUuDAYkU"

# GIÁ ĐIỆN
GIADIEN = 4000

# đăng ký font tiếng Việt
pdfmetrics.registerFont(ttfonts.TTFont('VN', 'NotoSans-Regular.ttf'))

styles = getSampleStyleSheet()

title = ParagraphStyle(
    "title",
    fontName="VN",
    fontSize=20,
    alignment=1,
    textColor=colors.darkblue
)

header = ParagraphStyle(
    "header",
    fontName="VN",
    fontSize=14,
    alignment=1
)

normal = ParagraphStyle(
    "normal",
    fontName="VN",
    fontSize=11
)


# VẼ KHUNG HÓA ĐƠN
def draw_border(canvas, doc):

    width, height = A4

    canvas.setStrokeColor(colors.darkblue)

    canvas.setLineWidth(3)
    canvas.rect(1*cm,1*cm,width-2*cm,height-2*cm)

    canvas.setLineWidth(1)
    canvas.rect(1.4*cm,1.4*cm,width-2.8*cm,height-2.8*cm)


# TẠO PDF
def tao_pdf(phong, diencu, dienmoi, nuoc, dv, phongtien):

    sodien = dienmoi - diencu
    tiendien = sodien * GIADIEN

    tong = tiendien + nuoc + dv + phongtien

    now = datetime.now()

    thang = f"Tháng {now.month}/{now.year}"

    mahoadon = f"HD{random.randint(10000,99999)}"

    file = f"hoadon_{phong}.pdf"

    elements = []

    # logo
    logo = Image("logo.png",4*cm,4*cm)
    elements.append(logo)

    elements.append(Paragraph("NHÀ TRỌ 441 ĐBP",header))
    elements.append(Paragraph("HÓA ĐƠN TIỀN TRỌ",title))

    elements.append(Spacer(1,10))

    elements.append(Paragraph(f"Mã hóa đơn: {mahoadon}",normal))
    elements.append(Paragraph(thang,normal))

    elements.append(Spacer(1,20))

    data = [

        ["Khoản","Chi tiết"],

        ["Phòng",phong],

        ["Điện cũ",f"{diencu:03d}"],
        ["Điện mới",f"{dienmoi:03d}"],
        ["Số điện",f"{sodien:03d}"],

        ["Tiền điện",f"{sodien} x {GIADIEN:,} = {tiendien:,} VNĐ"],

        ["Tiền nước",f"{nuoc:,} VNĐ"],

        ["Tiền dịch vụ",f"{dv:,} VNĐ"],

        ["Tiền phòng",f"{phongtien:,} VNĐ"],

        ["TỔNG",f"{tong:,} VNĐ"]

    ]

    table = Table(data,colWidths=[8*cm,8*cm])

    table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.lightblue),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("FONTNAME",(0,0),(-1,-1),"VN"),

        ("ALIGN",(1,1),(-1,-1),"RIGHT"),

        ("BACKGROUND",(0,-1),(-1,-1),colors.lightgrey)

    ]))

    elements.append(table)

    elements.append(Spacer(1,40))

    sign = [

        ["Người nộp tiền","Chủ trọ"],

        ["(Ký, ghi rõ họ tên)","(Ký, ghi rõ họ tên)"]

    ]

    sign_table = Table(sign,colWidths=[8*cm,8*cm])

    sign_table.setStyle(TableStyle([

        ("FONTNAME",(0,0),(-1,-1),"VN"),
        ("ALIGN",(0,0),(-1,-1),"CENTER")

    ]))

    elements.append(sign_table)

    pdf = SimpleDocTemplate(

        file,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm

    )

    pdf.build(elements,onFirstPage=draw_border,onLaterPages=draw_border)

    return file


# LỆNH START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
BOT TÍNH TIỀN TRỌ 441 ĐBP

Nhập theo mẫu:

phong,diencu,dienmoi,nuoc,dichvu,tienphong

Ví dụ:

101,120,135,100000,50000,2500000
"""

    await update.message.reply_text(text)


# XỬ LÝ DỮ LIỆU
async def tinh(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        data = [x.strip() for x in update.message.text.split(",")]

        if len(data) != 6:

            await update.message.reply_text(
                "❌ Sai cú pháp\n\nVí dụ đúng:\n101,120,135,100000,50000,2500000"
            )

            return

        phong = data[0]
        diencu = int(data[1])
        dienmoi = int(data[2])
        nuoc = int(data[3])
        dv = int(data[4])
        phongtien = int(data[5])

        if dienmoi < diencu:

            await update.message.reply_text(
                "❌ Điện mới phải lớn hơn điện cũ"
            )

            return

        file = tao_pdf(phong,diencu,dienmoi,nuoc,dv,phongtien)

        await update.message.reply_document(open(file,"rb"))

    except:

        await update.message.reply_text(
            "❌ Dữ liệu không hợp lệ."
        )


# CHẠY BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start",start))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tinh))

app.run_polling()