import PySimpleGUI as sg
import plc

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [[sg.Text('Read a single PLC tag'), sg.B('Read Single Tag')],
          [sg.Text('Write a single PLC tag'), sg.B('Write Single Tag')],
          [sg.Text('Read multiple PLC tags'), sg.B('Read Multiple Tags')],
          [sg.Text('Write multiple PLC tags'), sg.B('Write Multiple Tags')],
          [sg.Text('Trend a PLC tag'), sg.B('Trend Single Tag')],
          [sg.Text('Trend multiple PLC tags'), sg.B('Trend Multiple Tags')],
          [sg.Text('Get PLC tags'), sg.B('Get Tags')],
          [sg.Button('Close')]]

# Create the Window
window = sg.Window('PLC', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    # if user closes window or clicks cancel
    if event == sg.WIN_CLOSED or event == 'Close':
        break

    if event == 'Read Single Tag':
        tag = sg.popup_get_text('Enter tag name to read:')

        print(tag)

    if event == 'Get_Tags':
        tags = plc.get_tags('192.168.1.1')
        sg.popup_scrolled(tags, title='PLC Tags')

window.close()
