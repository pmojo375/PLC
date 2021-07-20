import PySimpleGUI as sg
import plc

ip = '192.168.1.1'

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [[sg.Text('Read a single PLC tag'), sg.B('Read Single Tag', key='Read Tag')],
          [sg.Text('Write a single PLC tag'), sg.B('Write Single Tag', key='Write Tag')],
          [sg.Text('Read multiple PLC tags'), sg.B('Read Multiple Tags', key='Read Tags')],
          [sg.Text('Write multiple PLC tags'), sg.B('Write Multiple Tags', key='Write Tags')],
          [sg.Text('Trend a PLC tag'), sg.B('Trend Single Tag', key='Trend Tag')],
          [sg.Text('Trend multiple PLC tags'), sg.B('Trend Multiple Tags', key='Trend Tags')],
          [sg.Text('Get PLC tags'), sg.B('Get Tags', key='Get Tags')],
          [sg.Button('Close')]]

# Create the Window
window = sg.Window('PLC', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    # if user closes window or clicks cancel
    if event == sg.WIN_CLOSED or event == 'Close':
        break

    if event == 'Read Tag':
        tag = sg.popup_get_text('Enter tag name to read:')

        print(f'Reading {tag}')

        plc.read_tag(ip, tag)

    if event == 'Write Tag':
        tag = sg.popup_get_text('Enter tag name to write to:')
        value = plc.cast(sg.popup_get_text('Enter value to write:'))

        print(f'Writing {value} to {tag}')

        plc.write_tag(ip, tag, value)

    if event == 'Read Tags':
        tags = sg.popup_get_file('Locate CSV with tag names:', file_types = (('CSV','*.csv'),), initial_folder='./')

        print(f'Filename {tags}')

        print(f'Reading tags')

        plc.read_tags_from_CSV(tags, ip, False)

    if event == 'Write Tags':
        tags = sg.popup_get_file('Locate CSV with tag names and values to write:', file_types = (('CSV','*.csv'),), initial_folder='./')

        print(f'Filename {tags}')

        print(f'Writing tags')

        plc.write_tags_from_CSV(tags, ip)

    if event == 'Trend Tag':
        tag = sg.popup_get_text('Enter tag name to trend:')

        print(f'Trending {tag}')

        plc.trend_tag(ip, tag, False)

    if event == 'Trend Tags':
        tags = sg.popup_get_file('Locate CSV with tag names to trend:', file_types = (('CSV','*.csv'),), initial_folder='./')

        print(f'Filename {tags}')

        print(f'Trending tags')

        plc.trend_tags(ip, tags, False, 1)

    if event == 'Get Tags':
        tags = plc.get_tags(ip)
        sg.popup_scrolled(tags, title='PLC Tags')

window.close()
