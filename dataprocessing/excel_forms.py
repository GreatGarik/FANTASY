from datetime import datetime
import os
from typing import List
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image
from io import BytesIO
from database.database import get_actual_gp_async, show_result, show_points_all, get_user_team, show_points_team_all, get_teams_fonts_colors, get_name_gp, get_maximus, get_all_users, get_predictions_by_gp

async def entry_list():
    users_list: List[dict] = await get_all_users()

    # Сортируем по общему количеству очков
    users_list.sort(key=lambda x: (x['Number'] if x['Number'] else float('inf'), x['User']))

    # Создаем новый Excel файл
    wb = Workbook()
    ws = wb.active
    ws.title = "ENTRY LIST"

    # Вставляем 5 пустых строк в начале
    ws.insert_rows(1, amount=5)
    ws.row_dimensions[3].height = 22.5

    # Объединяем ячейки в третьем и четвертом столбцах (C и D)
    #ws.merge_cells(start_row=4, start_column=3, end_row=4, end_column=4)
    #ws.merge_cells(start_row=5, start_column=3, end_row=5, end_column=4)
    ws.cell(row=3, column=3).font = Font(name='Formula1 Display Bold', size=11, bold=True, color='000000')
    ws['C3'] = f'FORMULA 1 FANTASY SERIES BY SILLY FORMULA'
    ws['C3'].alignment = Alignment(horizontal='center', vertical='center')
    ws.cell(row=4, column=3).font = Font(name='Formula1 Display Bold', size=10, bold=True, color='000000')
    ws['C4'] = f"ENTRY LIST"
    ws['C4'].alignment = Alignment(horizontal='center', vertical='center')

    img_path = os.path.join('logos', 'Shirokoe_logo_bez_fona_silli.png')  # Укажите путь к вашему изображению
    img = Image(img_path)
    # Указываем процент изменения размера
    resize_percentage = 6  # % от оригинального размера
    # Рассчитываем новый размер
    img.width = int(img.width * (resize_percentage / 100))
    img.height = int(img.height * (resize_percentage / 100))
    img.anchor = f'A1'  # Устанавливаем позицию изображения
    ws.add_image(img)

    # Заголовки таблицы
    header = ['№'] + ['Driver'] + ['Team'] + ['']

    ws.append(header)  # Добавляем заголовки в первую строку
    ws.row_dimensions[ws.max_row].height = 17

    # Устанавливаем шрифт и фон для заголовков
    header_font = Font(name='Formula1 Display Bold', size=11, bold=False, color='FFFFFF')  # Белый цвет
    header_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')  # Красный цвет

    # Создаем черную границу
    thin_border = Border(left=Side(style='thin', color='000000'),
                         right=Side(style='thin', color='000000'),
                         top=Side(style='thin', color='000000'),
                         bottom=Side(style='thin', color='000000'))

    for cell in ws[7]:  # Перебираем ячейки заголовка
        cell.font = header_font
        cell.fill = header_fill
        cell.border = thin_border
        # Объединяем ячейки в третьем и четвертом столбцах (C и D)
        ws.merge_cells(start_row=ws.max_row, start_column=3, end_row=ws.max_row, end_column=4)
    teams_fonts: dict = await get_teams_fonts_colors()
    # Добавляем данные в файл
    for entry in users_list:
        row = [entry['Number'] if entry['Number'] else 'N/A'] + [entry['User']] + [entry['Team']] + ['']
        ws.append(row)  # Добавляем строку с данными
        ws.row_dimensions[ws.max_row].height = 17
        wight_font = Font(name='Formula1 Display Bold', size=11, bold=False, color='FFFFFF')  # Белый цвет
        black_fill = PatternFill(start_color='000001', end_color='000001', fill_type='solid')  # Черный цве
        for cell in ws[ws.max_row]:
            cell.alignment = Alignment(vertical='center')
            if cell.column_letter in ['A', 'B', 'C', 'D', 'E']:
                cell.font = wight_font  # Устанавливаем белый шрифт
            else:
                cell.font = Font(name='Formula1 Display Regular', size=11, bold=False, color='FFFFFF')
            cell.fill = black_fill  # Устанавливаем черный фон

        # Устанавливаем фон для ячейки для команд
        if teams_fonts.get(entry['Team'], None):
            team = teams_fonts[entry['Team']]
            # Устанавливаем фон для ячейки, например, в колонке
            font = Font(name='Formula1 Display Bold', size=11, bold=False, color=team['text_color'])
            fill = PatternFill(start_color=team['background_color'], end_color=team['background_color'],
                               fill_type='solid')
            font_number = Font(name=team['number_font'], size=14, bold=True, italic=team['number_italic'],
                               color=team['number_color'])
            ws.cell(row=ws.max_row, column=1).font = font_number
            ws.cell(row=ws.max_row, column=2).font = font
            ws.cell(row=ws.max_row, column=3).font = font
            ws.cell(row=ws.max_row, column=1).fill = fill
            ws.cell(row=ws.max_row, column=2).fill = fill
            ws.cell(row=ws.max_row, column=3).fill = fill
            ws.cell(row=ws.max_row, column=4).fill = fill
            # Вставляем изображение в четвертый столбец (колонка Е)
            if team['logo']:
                img_path = os.path.join('logos', team['logo'])  # Укажите путь к вашему изображению
            else:
                img_path = os.path.join('logos', 'personal.png')  # Укажите путь к вашему изображению
            img = Image(img_path)
            # Указываем процент изменения размера
            resize_percentage = 46  # % от оригинального размера
            # Рассчитываем новый размер
            img.width = int(img.width * (resize_percentage / 100))
            img.height = int(img.height * (resize_percentage / 100))

            img.anchor = f'D{ws.max_row}'  # Устанавливаем позицию изображения
            ws.add_image(img)
        else:

            img_path = os.path.join('logos', 'personal.png')  # Укажите путь к вашему изображению
            img = Image(img_path)
            # Указываем процент изменения размера
            resize_percentage = 46  # % от оригинального размера
            # Рассчитываем новый размер
            img.width = int(img.width * (resize_percentage / 100))
            img.height = int(img.height * (resize_percentage / 100))

            img.anchor = f'D{ws.max_row}'  # Устанавливаем позицию изображения
            ws.add_image(img)

    # Устанавливаем выравнивание по центру для нужных колонок
    center_alignment = Alignment(horizontal='center', vertical='center')

    for cell in ws['A'] + ws['B'] + ws['D']:
        cell.alignment = center_alignment

    # Устанавливаем ширину столбцов
    for column in ws.columns:
        column_letter = column[0].column_letter  # Получаем букву столбца
        ws.column_dimensions[column_letter].width = 7.7
    ws.column_dimensions['B'].width = 35.7  # Третий столбец
    ws.column_dimensions['C'].width = 41.7  # Четвертый столбец
    ws.column_dimensions['D'].width = 8.7  # Пятый столбец

    # Скрываем сетку
    ws.sheet_view.showGridLines = False

    # Сохраняем книгу в BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)  # Перемещаем указатель в начало
    return output


async def last_stage():
    gp = await get_actual_gp_async()
    data = await show_result(gp)

    # Создаем новый Excel файл
    wb = Workbook()
    ws = wb.active
    ws.title = "Results"

    # Вставляем 5 пустых строк в начале
    ws.insert_rows(1, amount=5)
    ws.row_dimensions[4].height = 22.5
    # Объединяем ячейки в третьем и четвертом столбцах (C и D)
    ws.merge_cells(start_row=4, start_column=4, end_row=4, end_column=12)
    ws.cell(row=4, column=4).font = Font(name='Formula1 Display Bold', size=18, bold=True, color='000000')
    gp_name = await get_name_gp(gp)
    ws['D4'] = f'FORMULA 1 {gp_name.upper()} GRAND PRIX'
    ws['D4'].alignment = Alignment(horizontal='center', vertical='center')

    img_path = os.path.join('logos', 'Shirokoe_logo_bez_fona_silli.png')  # Укажите путь к вашему изображению
    img = Image(img_path)
    # Указываем процент изменения размера
    resize_percentage = 7  # % от оригинального размера
    # Рассчитываем новый размер
    img.width = int(img.width * (resize_percentage / 100))
    img.height = int(img.height * (resize_percentage / 100))
    img.anchor = f'C1'  # Устанавливаем позицию изображения
    ws.add_image(img)

    # Записываем заголовки
    headers = ['POS', '№', 'DRIVER', 'TEAM', None, 'DR1', 'DR2', 'DR3', 'DR4', 'TM', 'ENG', 'DIFF', 'LAP', 'PEN', 'PTS',
               'CH.PTS']
    ws.append(headers)

    # Устанавливаем шрифт и фон для заголовков
    header_font = Font(name='Formula1 Display Bold', size=11, bold=False, color='FFFFFF')  # Белый цвет
    header_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')  # Красный цвет

    # Создаем черную границу
    thin_border = Border(left=Side(style='thin', color='000000'),
                         right=Side(style='thin', color='000000'),
                         top=Side(style='thin', color='000000'),
                         bottom=Side(style='thin', color='000000'))

    for cell in ws[7]:  # Перебираем ячейки заголовка
        cell.alignment = Alignment(vertical='center')
        cell.font = header_font
        cell.fill = header_fill
        cell.border = thin_border
        # Объединяем ячейки в третьем и четвертом столбцах (C и D)
        ws.merge_cells(start_row=ws.max_row, start_column=4, end_row=ws.max_row, end_column=5)
    teams_fonts: dict = await get_teams_fonts_colors()

    maximus: dict = await get_maximus(gp)

    # Записываем данные
    for index, (user, result, points) in enumerate(data, 1):
        ws.append([
            index,
            user.number,
            user.name,
            await get_user_team(user.id_telegram),
            None,
            result.first_driver,
            result.second_driver,
            result.third_driver,
            result.fourth_driver,
            result.driver_team,
            result.driver_engine,
            result.gap,
            result.lapped,
            result.penalty,
            result.total,
            points.points
        ])
        ws.row_dimensions[ws.max_row].height = 17
        wight_font = Font(name='Formula1 Display Bold', size=11, bold=False, color='FFFFFF')  # Белый цвет
        black_fill = PatternFill(start_color='000001', end_color='000001', fill_type='solid')  # Черный цве
        for cell in ws[ws.max_row]:
            cell.alignment = Alignment(vertical='center')
            if cell.column_letter in ['A', 'B', 'C', 'D', 'E']:
                cell.font = wight_font  # Устанавливаем белый шрифт
            else:
                if (cell.column_letter in ['F', 'G'] and cell.value == maximus['max1']) or (
                        cell.column_letter == 'H' and cell.value == maximus['max2']) or (
                        cell.column_letter == 'I' and cell.value == maximus['max3']) or (
                        cell.column_letter in ['L', 'M'] and cell.value == 10):
                    cell.font = Font(name='Formula1 Display Regular', size=11, bold=False, color='ED7D31')
                else:
                    cell.font = Font(name='Formula1 Display Regular', size=11, bold=False, color='FFFFFF')
            cell.fill = black_fill  # Устанавливаем черный фон

        # Устанавливаем фон для ячейки для команд
        if teams_fonts.get(await get_user_team(user.id_telegram), None):
            team = teams_fonts.get(await get_user_team(user.id_telegram), None)
            # Устанавливаем фон для ячейки, например, в колонке
            font = Font(name='Formula1 Display Bold', size=11, bold=False, color=team['text_color'])
            fill = PatternFill(start_color=team['background_color'], end_color=team['background_color'],
                               fill_type='solid')
            font_number = Font(name=team['number_font'], size=14, bold=True, italic=team['number_italic'],
                               color=team['number_color'])
            ws.cell(row=ws.max_row, column=2).font = font_number
            ws.cell(row=ws.max_row, column=3).font = font
            ws.cell(row=ws.max_row, column=4).font = font
            ws.cell(row=ws.max_row, column=2).fill = fill
            ws.cell(row=ws.max_row, column=3).fill = fill
            ws.cell(row=ws.max_row, column=4).fill = fill
            ws.cell(row=ws.max_row, column=5).fill = fill
            # Вставляем изображение в четвертый столбец (колонка Е)
            if team['logo']:
                img_path = os.path.join('logos', team['logo'])  # Укажите путь к вашему изображению
            else:
                img_path = os.path.join('logos', 'personal.png')  # Укажите путь к вашему изображению
            img = Image(img_path)
            # Указываем процент изменения размера
            resize_percentage = 46  # % от оригинального размера
            # Рассчитываем новый размер
            img.width = int(img.width * (resize_percentage / 100))
            img.height = int(img.height * (resize_percentage / 100))

            img.anchor = f'E{ws.max_row}'  # Устанавливаем позицию изображения
            ws.add_image(img)
        else:

            img_path = os.path.join('logos', 'personal.png')  # Укажите путь к вашему изображению
            img = Image(img_path)
            # Указываем процент изменения размера
            resize_percentage = 46  # % от оригинального размера
            # Рассчитываем новый размер
            img.width = int(img.width * (resize_percentage / 100))
            img.height = int(img.height * (resize_percentage / 100))

            img.anchor = f'E{ws.max_row}'  # Устанавливаем позицию изображения
            ws.add_image(img)

        # Устанавливаем выравнивание по центру для нужных колонок
    center_alignment = Alignment(horizontal='center', vertical='center')

    for cell in ws['A'] + ws['B'] + ws['D']:
        cell.alignment = center_alignment

    # Устанавливаем ширину столбцов
    for column in ws.columns:
        column_letter = column[0].column_letter  # Получаем букву столбца
        ws.column_dimensions[column_letter].width = 7.7
    ws.column_dimensions['C'].width = 35.7  # Третий столбец
    ws.column_dimensions['D'].width = 41.7  # Четвертый столбец
    ws.column_dimensions['E'].width = 8.7  # Пятый столбец
    ws.column_dimensions[ws.cell(row=7, column=ws.max_column).column_letter].width = 10.7  # Последний столбец

    # Цвета 1, 2, 3 места
    ws.cell(row=8, column=1).fill = PatternFill(start_color='bf9000', end_color='bf9000',
                                                fill_type='solid')
    ws.cell(row=9, column=1).fill = PatternFill(start_color='7c7c7c', end_color='7c7c7c',
                                                fill_type='solid')
    ws.cell(row=10, column=1).fill = PatternFill(start_color='c55a11', end_color='c55a11',
                                                 fill_type='solid')

    # Скрываем сетку
    ws.sheet_view.showGridLines = False

    # Сохраняем книгу в BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)  # Перемещаем указатель в начало
    return output

def sort_points(entry):
    points =  [entry[key] if entry[key] else 0 for key in entry if key not in ['User', 'Team', 'Number', 'CH.PTS']]
    total_points = sum(points)
    sorted_point  = sorted(points, reverse=True)
    # Находим максимальное значение
    max_value = max(points) if points else None

    # Находим первый индекс максимального значения
    first_max_index = points.index(max_value) if max_value in points else -1
    return total_points, sorted_point, -first_max_index

async def process_championship_full():
    points_list: List[dict] = await show_points_all(datetime.now().year)


    # Сортируем по общему количеству очков
    points_list.sort(key=sort_points, reverse=True)

    for entry in points_list:
        entry['CH.PTS'] = sum(
            entry[key] for key in entry if key != 'User' and key != 'Team' and key != 'Number' and entry[key])

    # Создаем новый Excel файл
    wb = Workbook()
    ws = wb.active
    ws.title = "Championship Points"

    # Вставляем 5 пустых строк в начале
    ws.insert_rows(1, amount=5)
    ws.row_dimensions[4].height = 22.5

    # Объединяем ячейки в третьем и четвертом столбцах (C и D)
    ws.merge_cells(start_row=4, start_column=4, end_row=4, end_column=12)
    ws.merge_cells(start_row=5, start_column=4, end_row=5, end_column=12)
    ws.cell(row=4, column=4).font = Font(name='Formula1 Display Bold', size=18, bold=True, color='000000')
    ws['D4'] = f'FORMULA 1 FANTASY SERIES BY SILLY FORMULA'
    ws['D4'].alignment = Alignment(horizontal='center', vertical='center')
    ws.cell(row=5, column=4).font = Font(name='Formula1 Display Bold', size=11, bold=True, color='000000')
    ws['D5'] = f"DRIVER'S CHAMPIONSHIP"
    ws['D5'].alignment = Alignment(horizontal='center', vertical='center')

    img_path = os.path.join('logos', 'Shirokoe_logo_bez_fona_silli.png')  # Укажите путь к вашему изображению
    img = Image(img_path)
    # Указываем процент изменения размера
    resize_percentage = 7  # % от оригинального размера
    # Рассчитываем новый размер
    img.width = int(img.width * (resize_percentage / 100))
    img.height = int(img.height * (resize_percentage / 100))
    img.anchor = f'C1'  # Устанавливаем позицию изображения
    ws.add_image(img)

    # Заголовки таблицы
    header = ['POS'] + ['№'] + ['Driver'] + ['Team'] + [''] + [key for key in points_list[0] if
                                                               key not in ['User', 'CH.PTS', 'Number', 'Team',
                                                                           'Image']] + ['CH.PTS']
    ws.append(header)  # Добавляем заголовки в первую строку
    ws.row_dimensions[ws.max_row].height = 17

    # Устанавливаем шрифт и фон для заголовков
    header_font = Font(name='Formula1 Display Bold', size=11, bold=False, color='FFFFFF')  # Белый цвет
    header_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')  # Красный цвет

    # Создаем черную границу
    thin_border = Border(left=Side(style='thin', color='000000'),
                         right=Side(style='thin', color='000000'),
                         top=Side(style='thin', color='000000'),
                         bottom=Side(style='thin', color='000000'))

    for cell in ws[7]:  # Перебираем ячейки заголовка
        cell.font = header_font
        cell.fill = header_fill
        cell.border = thin_border
        # Объединяем ячейки в третьем и четвертом столбцах (C и D)
        ws.merge_cells(start_row=ws.max_row, start_column=4, end_row=ws.max_row, end_column=5)
    teams_fonts: dict = await get_teams_fonts_colors()
    # Добавляем данные в файл
    for num, entry in enumerate(points_list, 1):
        row = [num] + [entry['Number']] + [entry['User']] + [entry['Team']] + [''] + [entry[key] for key in header[5:]]
        ws.append(row)  # Добавляем строку с данными
        ws.row_dimensions[ws.max_row].height = 17
        wight_font = Font(name='Formula1 Display Bold', size=11, bold=False, color='FFFFFF')  # Белый цвет
        black_fill = PatternFill(start_color='000001', end_color='000001', fill_type='solid')  # Черный цве
        for cell in ws[ws.max_row]:
            cell.alignment = Alignment(vertical='center')
            if cell.column_letter in ['A', 'B', 'C', 'D', 'E']:
                cell.font = wight_font  # Устанавливаем белый шрифт
            else:
                cell.font = Font(name='Formula1 Display Regular', size=11, bold=False, color='FFFFFF')
            cell.fill = black_fill  # Устанавливаем черный фон

        # Устанавливаем фон для ячейки для команд
        if teams_fonts.get(entry['Team'], None):
            team = teams_fonts[entry['Team']]
            # Устанавливаем фон для ячейки, например, в колонке
            font = Font(name='Formula1 Display Bold', size=11, bold=False, color=team['text_color'])
            fill = PatternFill(start_color=team['background_color'], end_color=team['background_color'],
                               fill_type='solid')
            font_number = Font(name=team['number_font'], size=14, bold=True, italic=team['number_italic'],
                               color=team['number_color'])
            ws.cell(row=ws.max_row, column=2).font = font_number
            ws.cell(row=ws.max_row, column=3).font = font
            ws.cell(row=ws.max_row, column=4).font = font
            ws.cell(row=ws.max_row, column=2).fill = fill
            ws.cell(row=ws.max_row, column=3).fill = fill
            ws.cell(row=ws.max_row, column=4).fill = fill
            ws.cell(row=ws.max_row, column=5).fill = fill
            # Вставляем изображение в четвертый столбец (колонка Е)
            if team['logo']:
                img_path = os.path.join('logos', team['logo'])  # Укажите путь к вашему изображению
            else:
                img_path = os.path.join('logos', 'personal.png')  # Укажите путь к вашему изображению
            img = Image(img_path)
            # Указываем процент изменения размера
            resize_percentage = 46  # % от оригинального размера
            # Рассчитываем новый размер
            img.width = int(img.width * (resize_percentage / 100))
            img.height = int(img.height * (resize_percentage / 100))

            img.anchor = f'E{ws.max_row}'  # Устанавливаем позицию изображения
            ws.add_image(img)

    # Устанавливаем выравнивание по центру для нужных колонок
    center_alignment = Alignment(horizontal='center', vertical='center')

    for cell in ws['A'] + ws['B'] + ws['D']:
        cell.alignment = center_alignment

    # Устанавливаем ширину столбцов
    for column in ws.columns:
        column_letter = column[0].column_letter  # Получаем букву столбца
        ws.column_dimensions[column_letter].width = 7.7
    ws.column_dimensions['C'].width = 35.7  # Третий столбец
    ws.column_dimensions['D'].width = 41.7  # Четвертый столбец
    ws.column_dimensions['E'].width = 8.7  # Пятый столбец
    ws.column_dimensions[ws.cell(row=7, column=ws.max_column).column_letter].width = 11.3  # Третий столбец

    # Цвета 1, 2, 3 места
    ws.cell(row=8, column=1).fill = PatternFill(start_color='bf9000', end_color='bf9000',
                                                fill_type='solid')
    ws.cell(row=9, column=1).fill = PatternFill(start_color='7c7c7c', end_color='7c7c7c',
                                                fill_type='solid')
    ws.cell(row=10, column=1).fill = PatternFill(start_color='c55a11', end_color='c55a11',
                                                 fill_type='solid')

    # Скрываем сетку
    ws.sheet_view.showGridLines = False

    # Сохраняем книгу в BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)  # Перемещаем указатель в начало
    return output

def sort_points_team(entry):
    total_points = entry['Points']
    sorted_point  = sorted(entry['all_res'], reverse=True)
    # Находим максимальное значение
    max_value = max(sorted_point) if sorted_point else None

    # Находим первый индекс максимального значения
    first_max_index = entry['all_res'].index(max_value) if max_value in entry['all_res'] else -1
    return total_points, sorted_point, -first_max_index


async def championship_team_full():
    points_list: List[dict] = await show_points_team_all(datetime.now().year)

    for entry in points_list:
        entry['Points'] = sum(entry[key] for key in entry if key != 'Team' and key != 'all_res'  and entry[key])

    # Сортируем по общему количеству очков
    #points_list.sort(key=lambda x: x['Points'], reverse=True)
    points_list.sort(key=sort_points_team, reverse=True)

    # Создаем новый Excel файл
    wb = Workbook()
    ws = wb.active
    ws.title = "Championship Teams Points"

    # Вставляем 5 пустых строк в начале
    ws.insert_rows(1, amount=5)
    ws.row_dimensions[4].height = 22.5

    # Объединяем ячейки
    ws.merge_cells(start_row=3, start_column=4, end_row=3, end_column=24)
    ws.merge_cells(start_row=4, start_column=4, end_row=4, end_column=24)
    ws.cell(row=3, column=4).font = Font(name='Formula1 Display Bold', size=18, bold=True, color='000000')
    ws['D3'] = f'FORMULA 1 FANTASY SERIES BY SILLY FORMULA'
    ws['D3'].alignment = Alignment(horizontal='center', vertical='center')
    ws.cell(row=4, column=4).font = Font(name='Formula1 Display Bold', size=11, bold=True, color='000000')
    ws['D4'] = f"TEAM STANDINGS"
    ws['D4'].alignment = Alignment(horizontal='center', vertical='center')

    img_path = os.path.join('logos', 'Shirokoe_logo_bez_fona_silli.png')  # Укажите путь к вашему изображению
    img = Image(img_path)
    # Указываем процент изменения размера
    resize_percentage = 7  # % от оригинального размера
    # Рассчитываем новый размер
    img.width = int(img.width * (resize_percentage / 100))
    img.height = int(img.height * (resize_percentage / 100))
    img.anchor = f'B1'  # Устанавливаем позицию изображения
    ws.add_image(img)

    # Заголовки таблицы
    header = ['POS'] + ['Team'] + [''] + [key for key in points_list[0] if
                                          key != 'Points' and key != 'Team' and key != 'all_res'] + ['Points']
    ws.append(header)  # Добавляем заголовки в первую строку
    ws.row_dimensions[ws.max_row].height = 17

    # Устанавливаем шрифт и фон для заголовков
    header_font = Font(name='Formula1 Display Bold', size=11, bold=False, color='FFFFFF')  # Белый цвет
    header_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')  # Красный цвет

    # Создаем черную границу
    thin_border = Border(left=Side(style='thin', color='000000'),
                         right=Side(style='thin', color='000000'),
                         top=Side(style='thin', color='000000'),
                         bottom=Side(style='thin', color='000000'))

    for cell in ws[7]:  # Перебираем ячейки заголовка
        cell.font = header_font
        cell.fill = header_fill
        cell.border = thin_border
        # Объединяем ячейки в третьем и четвертом столбцах (C и D)
        ws.merge_cells(start_row=ws.max_row, start_column=2, end_row=ws.max_row, end_column=3)
    teams_fonts: dict = await get_teams_fonts_colors()

    # Добавляем данные в файл
    for num, entry in enumerate(points_list, 1):
        row = [num] + [entry['Team']] + [''] + [entry[key] for key in header[1:] if key != '' and key != 'Team' and key != 'all_res']
        ws.append(row)  # Добавляем строку с данными
        ws.row_dimensions[ws.max_row].height = 17
        wight_font = Font(name='Formula1 Display Bold', size=11, bold=False, color='FFFFFF')  # Белый цвет
        black_fill = PatternFill(start_color='000001', end_color='000001', fill_type='solid')  # Черный цве
        for cell in ws[ws.max_row]:
            cell.alignment = Alignment(vertical='center')
            # if cell.column_letter in ['A', 'B', 'C', 'D', 'E']:
            #    cell.font = wight_font  # Устанавливаем белый шрифт

            cell.font = Font(name='Formula1 Display Regular', size=11, bold=False, color='FFFFFF')
            cell.fill = black_fill  # Устанавливаем черный фон

        # Устанавливаем фон для ячейки для команд
        if teams_fonts.get(entry['Team'], None):
            team = teams_fonts[entry['Team']]
            # Устанавливаем фон для ячейки, например, в колонке
            font = Font(name='Formula1 Display Bold', size=11, bold=False, color=team['text_color'])
            fill = PatternFill(start_color=team['background_color'], end_color=team['background_color'],
                               fill_type='solid')
            font_number = Font(name=team['number_font'], size=14, bold=True, italic=team['number_italic'],
                               color=team['number_color'])
            # ws.cell(row=ws.max_row, column=2).font = font_number
            ws.cell(row=ws.max_row, column=2).font = font
            # ws.cell(row=ws.max_row, column=4).font = font
            # ws.cell(row=ws.max_row, column=2).fill = fill
            ws.cell(row=ws.max_row, column=2).fill = fill
            ws.cell(row=ws.max_row, column=3).fill = fill
            # ws.cell(row=ws.max_row, column=5).fill = fill
            # Вставляем изображение в четвертый столбец (колонка Е)
            if team['logo']:
                img_path = os.path.join('logos', team['logo'])  # Укажите путь к вашему изображению
            else:
                img_path = os.path.join('logos', 'personal.png')  # Укажите путь к вашему изображению
            img = Image(img_path)
            # Указываем процент изменения размера
            resize_percentage = 46  # % от оригинального размера
            # Рассчитываем новый размер
            img.width = int(img.width * (resize_percentage / 100))
            img.height = int(img.height * (resize_percentage / 100))

            img.anchor = f'C{ws.max_row}'  # Устанавливаем позицию изображения
            ws.add_image(img)

        # Устанавливаем выравнивание по центру для нужных колонок
    center_alignment = Alignment(horizontal='center', vertical='center')

    for cell in ws['A'] + ws['B'] + ws['C']:
        cell.alignment = center_alignment

    # Устанавливаем ширину столбцов
    for column in ws.columns:
        column_letter = column[0].column_letter  # Получаем букву столбца
        ws.column_dimensions[column_letter].width = 7.7
    # ws.column_dimensions['C'].width = 35.7  # Третий столбец
    ws.column_dimensions['B'].width = 41.7  # Четвертый столбец
    ws.column_dimensions['C'].width = 8.7  # Пятый столбец
    ws.column_dimensions[ws.cell(row=3, column=ws.max_column).column_letter].width = 11.3  # Третий столбец

    # Цвета 1, 2, 3 места
    ws.cell(row=8, column=1).fill = PatternFill(start_color='bf9000', end_color='bf9000',
                                                fill_type='solid')
    ws.cell(row=9, column=1).fill = PatternFill(start_color='7c7c7c', end_color='7c7c7c',
                                                fill_type='solid')
    ws.cell(row=10, column=1).fill = PatternFill(start_color='c55a11', end_color='c55a11',
                                                 fill_type='solid')

    # Скрываем сетку
    ws.sheet_view.showGridLines = False

    # Сохраняем книгу в BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)  # Перемещаем указатель в начало
    return output

async def process_calculation_command(data):
    df = pd.DataFrame(list(data.items()), columns=['Ключ', 'Значение'])
    # Сохраняем книгу в BytesIO
    output = BytesIO()
    # Сохранение DataFrame в Excel-файл
    df.to_excel(output, index=False)
    output.seek(0)  # Перемещаем указатель в начало
    return output

async def process_all_predicts():
    gp = await get_actual_gp_async()
    data =  await get_predictions_by_gp(gp)
    df = pd.DataFrame(data)

    # Заменяем None на пустую строку для корректного сохранения в Excel
    df.fillna('', inplace=True)
    output = BytesIO()
    # Сохраняем DataFrame в Excel
    df.to_excel(output, index=False)
    # Сохраняем книгу в BytesIO

    # Сохранение DataFrame в Excel-файл
    #df.to_excel(output, index=False)
    output.seek(0)  # Перемещаем указатель в начало
    return output
