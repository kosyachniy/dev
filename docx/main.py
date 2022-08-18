from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def _cell_border(cell, **kwargs):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()

    # check for tag existnace, if none found, then create one
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)

    # list over all available tags
    for edge in ('start', 'top', 'end', 'bottom', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'w:{}'.format(edge)

            # check for tag existnace, if none found, then create one
            element = tcBorders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                tcBorders.append(element)

            # looks like order of attributes is important
            for key in ["sz", "val", "color", "space", "shadow"]:
                if key in edge_data:
                    element.set(qn('w:{}'.format(key)), str(edge_data[key]))

def _cell_margin(cell, **kwargs):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')

    for m in [
        "top",
        "start",
        "bottom",
        "end",
    ]:
        if m in kwargs:
            node = OxmlElement("w:{}".format(m))
            node.set(qn('w:w'), str(kwargs.get(m)))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)

    tcPr.append(tcMar)

def _hr(paragraph, size=1, color='auto'):
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    pPr.insert_element_before(pBdr,
        'w:shd', 'w:tabs', 'w:suppressAutoHyphens', 'w:kinsoku', 'w:wordWrap',
        'w:overflowPunct', 'w:topLinePunct', 'w:autoSpaceDE', 'w:autoSpaceDN',
        'w:bidi', 'w:adjustRightInd', 'w:snapToGrid', 'w:spacing', 'w:ind',
        'w:contextualSpacing', 'w:mirrorIndents', 'w:suppressOverlap', 'w:jc',
        'w:textDirection', 'w:textAlignment', 'w:textboxTightWrap',
        'w:outlineLvl', 'w:divId', 'w:cnfStyle', 'w:rPr', 'w:sectPr',
        'w:pPrChange'
    )
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), str(size))
    bottom.set(qn('w:space'), '0.5')
    bottom.set(qn('w:color'), color)
    pBdr.append(bottom)

def _background_color(div, color):
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color)
    div.paragraph_format.element.get_or_add_pPr()
    div.paragraph_format.element.pPr.append(shd)


doc = Document()

sections = doc.sections
for section in sections:
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

doc.styles['Normal'].font.name = 'Arial'
doc.styles['Normal'].font.size = Pt(9)
doc.styles['Normal'].paragraph_format.space_before = 0
doc.styles['Normal'].paragraph_format.space_after = 0

doc.styles.add_style('H1', WD_STYLE_TYPE.PARAGRAPH)
doc.styles['H1'].font.name = 'Arial'
doc.styles['H1'].font.size = Pt(25)
doc.styles['H1'].font.bold = True
doc.styles['H1'].paragraph_format.space_before = Pt(18)
doc.styles['H1'].paragraph_format.line_spacing = Pt(15)

doc.styles.add_style('H2', WD_STYLE_TYPE.PARAGRAPH)
doc.styles['H2'].font.name = 'Arial'
doc.styles['H2'].font.size = Pt(11)
doc.styles['H2'].font.color.rgb = RGBColor(0xae, 0xae, 0xae)
doc.styles['H2'].paragraph_format.space_before = Pt(15)
doc.styles['H2'].paragraph_format.line_spacing = 0

doc.styles.add_style('H3', WD_STYLE_TYPE.PARAGRAPH)
doc.styles['H3'].font.name = 'Arial'
doc.styles['H3'].font.size = Pt(12)
doc.styles['H3'].font.bold = True
doc.styles['H3'].paragraph_format.space_before = 0
doc.styles['H3'].paragraph_format.space_after = 0

# doc.styles.add_style('H4', WD_STYLE_TYPE.PARAGRAPH)
# doc.styles['H4'].font.name = 'Arial'
# doc.styles['H4'].font.size = Pt(10)

doc.styles.add_style('H5', WD_STYLE_TYPE.PARAGRAPH)
doc.styles['H5'].font.name = 'Arial'
doc.styles['H5'].font.size = Pt(11)
doc.styles['H5'].paragraph_format.space_before = 0
doc.styles['H5'].paragraph_format.space_after = 0

doc.styles.add_style('H6', WD_STYLE_TYPE.PARAGRAPH)
doc.styles['H6'].font.name = 'Arial'
doc.styles['H6'].font.size = Pt(8)
doc.styles['H6'].font.color.rgb = RGBColor(0xae, 0xae, 0xae)
doc.styles['H6'].paragraph_format.space_before = 0
doc.styles['H6'].paragraph_format.space_after = Pt(8)

doc.styles.add_style('H7', WD_STYLE_TYPE.PARAGRAPH)
doc.styles['H7'].font.name = 'Arial'
doc.styles['H7'].font.size = Pt(9)
doc.styles['H7'].font.underline = True
doc.styles['H7'].paragraph_format.space_before = 0
doc.styles['H7'].paragraph_format.space_after = 0

# doc.styles.add_style('MARGIN', WD_STYLE_TYPE.PARAGRAPH)
# doc.styles['MARGIN'].font.size = Pt(5)

tbl = doc.add_table(rows=0, cols=2)
tbl.columns[0].width=Inches(1.5)
tbl.columns[1].width=Inches(5.5)

row = tbl.add_row().cells
row[0].paragraphs[0].add_run().add_picture('1.jpg', width=Inches(1.25))
row[1].paragraphs[0].text = 'Алексей Полоз'
row[1].paragraphs[0].style = 'H1'
row[1].add_paragraph('''Мужчина, 22 года, родился 7 октября 1998

+7 (969) 736-67-30
polozhev@mail.ru

Санкт-Петербург, Россия''')

row = tbl.add_row().cells
row[0].merge(row[1])
row[0].paragraphs[0].text = 'Должность'
row[0].paragraphs[0].style = 'H2'
_hr(row[0].paragraphs[0], 8, '#D8D8D8')
# _cell_margin(row[0], top=0, bottom=0, end=0)
# _cell_border(
#     row[0],
#     bottom={'sz': 5, 'color': '#D8D8D8', 'val': 'single'},
# )

row = tbl.add_row().cells
row[0].merge(row[1])
row[0].paragraphs[0].text = 'Программист: Python BackEnd, Web FullStack'
row[0].paragraphs[0].style = 'H3'
row[0].add_paragraph('Информационные технологии, Веб-разработка, Аналитика')
row[0].paragraphs[1].paragraph_format.space_after = Pt(8)

row = tbl.add_row().cells
row[0].merge(row[1])
row[0].paragraphs[0].text = 'Образование'
row[0].paragraphs[0].style = 'H2'
_hr(row[0].paragraphs[0], 8, '#D8D8D8')

row = tbl.add_row().cells
row[0].paragraphs[0].text = 'Бакалавр'
row[0].paragraphs[0].style = 'H5'
row[0].add_paragraph('2016 – 2020', style='H6')
row[1].paragraphs[0].text = 'Санкт-Петербургский государственный университет (СПбГУ)'
row[1].paragraphs[0].style = 'H3'
row[1].add_paragraph('Прикладная математика – процессы управления')
row[1].paragraphs[1].paragraph_format.space_after = Pt(8)

row = tbl.add_row().cells
row[0].merge(row[1])
row[0].paragraphs[0].text = 'Повышение квалификации, курсы'
row[0].paragraphs[0].style = 'H2'
_hr(row[0].paragraphs[0], 8, '#D8D8D8')

row = tbl.add_row().cells
row[0].paragraphs[0].text = '2019'
row[0].paragraphs[0].style = 'H6'
row[1].paragraphs[0].text = 'Y Combinator Startup School'
row[1].paragraphs[0].style = 'H3'
row[1].add_paragraph('Глобальное сообщество основателей стартапов')
row[1].paragraphs[1].paragraph_format.space_after = Pt(8)
row = tbl.add_row().cells
row[0].paragraphs[0].text = '2019'
row[0].paragraphs[0].style = 'H6'
row[1].paragraphs[0].text = 'HSE INC'
row[1].paragraphs[0].style = 'H3'
row[1].add_paragraph('Выпускник бизнес-инкубатора')
row[1].paragraphs[1].paragraph_format.space_after = Pt(8)

row = tbl.add_row().cells
row[0].merge(row[1])
row[0].paragraphs[0].text = 'Ключевые навыки'
row[0].paragraphs[0].style = 'H2'
_hr(row[0].paragraphs[0], 8, '#D8D8D8')

row = tbl.add_row().cells
row[0].paragraphs[0].text = 'Иностранные языки'
row[0].paragraphs[0].style = 'H6'
row[1].paragraphs[0].text = 'Русский — родной'
row[1].add_paragraph('Английский — B2')
row[1].paragraphs[-1].paragraph_format.space_after = Pt(8)
row = tbl.add_row().cells
row[0].paragraphs[0].text = 'Навыки'
row[0].paragraphs[0].style = 'H6'
row[1].paragraphs[0].text = ''
row[1].paragraphs[-1].paragraph_format.space_after = Pt(8)
blocks = 'Docker  Git  Python  FastAPI  Flask  JavaScript  React  Redux  MongoDB  SQL  WebSocket  Socket.IO  Server setup  NGINX  Bots for social networks & messengers  REST API  JSON-RPC  Long Polling  Webhook  Bash  *nix  asyncio  Pandas  NumPy  Data analysis  NLP  Automation of processes  Blockchain  Smart contracts  Microcontrollers'.split('  ')
for block in blocks:
    run = row[1].paragraphs[0].add_run()
    run.text = block
    run.font.highlight_color = WD_COLOR_INDEX.GRAY_25 #E6E6E6
    run = row[1].paragraphs[0].add_run()
    run.text = '  '

row = tbl.add_row().cells
row[0].merge(row[1])
row[0].paragraphs[0].text = 'Опыт работы'
row[0].paragraphs[0].style = 'H2'
_hr(row[0].paragraphs[0], 8, '#D8D8D8')

row = tbl.add_row().cells
row[0].paragraphs[0].text = '2018 – 2021'
row[0].paragraphs[0].style = 'H6'
row[1].paragraphs[0].text = 'Co-founder & Core dev at «Tensy»'
row[1].paragraphs[0].style = 'H3'
row[1].add_paragraph('Образовательная платформа для мгновенной P2P помощи (https://tensy.io/).')
row[1].paragraphs[1].paragraph_format.space_after = Pt(8)
row = tbl.add_row().cells
row[0].paragraphs[0].text = '2021 – н.в.'
row[0].paragraphs[0].style = 'H6'
row[1].paragraphs[0].text = 'Dev at «Yandex»'
row[1].paragraphs[0].style = 'H3'
row[1].add_paragraph('Транснациональная компания, лидер в IT сфере в России (https://yandex.ru/).')
row[1].paragraphs[1].paragraph_format.space_after = Pt(8)

doc.add_page_break()

tbl = doc.add_table(rows=0, cols=2)
tbl.columns[0].width=Inches(1.5)
tbl.columns[1].width=Inches(5.5)

row = tbl.add_row().cells
row[0].merge(row[1])
row[0].paragraphs[0].text = 'Проекты'
row[0].paragraphs[0].style = 'H2'
row[0].paragraphs[0].paragraph_format.space_before = 0
_hr(row[0].paragraphs[0], 8, '#D8D8D8')

row = tbl.add_row().cells
row[0].paragraphs[0].text = '2021'
row[0].paragraphs[0].style = 'H6'
row[1].paragraphs[0].text = '«Трейдинг бот на бирже»'
row[1].paragraphs[0].style = 'H7'
row[1].add_paragraph('Bot. Парсинг событий, подгрузка инвестиционных идей из различных источников. Технический анализ, формирование стратегии торговли, выставление заявок. Обработка ошибок API, ситуационных сценариев. Прогноз и аналитика.')
row[1].paragraphs[1].paragraph_format.space_after = Pt(8)
row = tbl.add_row().cells
row[0].paragraphs[0].text = '2021'
row[0].paragraphs[0].style = 'H6'
row[1].paragraphs[0].text = '«РосОпрос»'
row[1].paragraphs[0].style = 'H7'
row[1].add_paragraph('BackEnd. Создание древовидных опросов, формирование структуры по истории ответов. Анализ по пользователям и вопросам, подготовка данных для визуализации.')
row[1].paragraphs[1].paragraph_format.space_after = Pt(8)

row = tbl.add_row().cells
row[0].merge(row[1])
row[0].paragraphs[0].text = 'Соревнования'
row[0].paragraphs[0].style = 'H2'
_hr(row[0].paragraphs[0], 8, '#D8D8D8')

row = tbl.add_row().cells
row[0].paragraphs[0].text = '2019'
row[0].paragraphs[0].style = 'H6'
row[1].paragraphs[0].text = 'Final, Финляндия'
row[1].paragraphs[0].style = 'H7'
run = row[1].paragraphs[0].add_run()
run.text = ', Junction'
run.font.underline = False
row[1].add_paragraph('Проект: Сервис эмоциональной поддержки')
row[1].paragraphs[1].paragraph_format.space_after = Pt(8)
row = tbl.add_row().cells
row[0].paragraphs[0].text = '2019'
row[0].paragraphs[0].style = 'H6'
row[1].paragraphs[0].text = 'TOP 1, Россия'
row[1].paragraphs[0].style = 'H7'
run = row[1].paragraphs[0].add_run()
run.text = ', Hack.Moscow, трек «Education»'
run.font.underline = False
row[1].add_paragraph('Проект: Платформа для помощи с домашними заданиями')
row[1].paragraphs[1].paragraph_format.space_after = Pt(8)

doc.save('1.docx')
