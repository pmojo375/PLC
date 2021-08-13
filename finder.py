import PySimpleGUI as sg
from bs4 import BeautifulSoup
import csv
import re

soup = None
tags = None

sg.theme('DarkAmber')   # Add a touch of color
def make_main_window():

    frame_layout = [[sg.T('You must specify and read the PLC L5X file before you can search. Select file below and press the "Read" button to enable the features below.', size=(63, 2))],
                   [sg.Text('L5X File'), sg.Input(key='-L5X-'), sg.FileBrowse(), sg.B('Read', key='-READFILE-', size=(5,1))],
                   [sg.T('L5X FILE NOT READ', key='-FILEREAD-', justification='center', size=(63,1))]]

    layout = [[sg.Frame('Initial Read', frame_layout)],
             [sg.T('Datatype', size=(14, 1), justification='right'), sg.I('Cylinder', key='-DATATYPE-', disabled=True, size=(41, 1)), sg.B('Find Instances', key='-FIND-', disabled=True, size=(11, 1))],
             [sg.T('Routine To Search', size=(14, 1), justification='right'), sg.I('R05_Faults', key='-ROUTINE-', disabled=True, size=(41, 1)), sg.B('Search', key='-SEARCH-', disabled=True, size=(11, 1))],
             [sg.Button('Close')]]

    return sg.Window('PLC', layout, finalize=True)


def data_entered(data):
    if data == '':
        return False
    else:
        return True


def read_L5X(file_name):
    with open(file_name, encoding='utf-8') as plc:
        soup = BeautifulSoup(plc, 'lxml-xml')

    return soup


def find_all_tags(soup):
    tags = soup.find_all(find_tags)

    return_tags = []

    for tag in tags:
        print(tag['Name'])
        return_tags.append(tag['Name'])

    return return_tags


def find_tags(tag):
    if tag.name == 'Tag' and tag.has_attr('DataType'):
        if tag['DataType'] == f'{datatype}':
            return True
        else:
            return False
    else:
        return False


def search_routines(routine_name, soup, tags):
    # get routines to search

    if routine_name == '':
        routines = soup.find_all('Routine')
    else:
        routines = soup.find_all('Routine', Name=lambda name: routine_name in name)

    rung_text = []

    for routine in routines:
        all_text = routine.find_all('Text')
        for text in all_text:
            rung_text.append(text)

    found_tags = []

    for tag in tags:
        for rung in rung_text:
            logic = rung.get_text()

            if tag in logic:
                found_tags.append(tag)
                break

    missing_tags = []

    for tag in tags:
        if not tag in found_tags:
            print(f'{tag}')
            missing_tags.append(tag)

    return missing_tags


# Create the Window
window = make_main_window()
status = window['-FILEREAD-']

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.Read()

    print(event, values)

    file_name = values['-L5X-']
    routine_name = values['-ROUTINE-']
    datatype = values['-DATATYPE-']

    if event in (sg.WIN_CLOSED, 'Close'):
        break

    if event == '-FIND-':
        tags = find_all_tags(soup)

    if event == '-READFILE-':
        soup = read_L5X(file_name)

    if event == '-SEARCH-':
        missing = search_routines(routine_name, soup, tags)

    if not soup == None:
        status.update(value='L5X READ')

        window['-FIND-'].update(disabled=False)
        window['-DATATYPE-'].update(disabled=False)

    if not tags == None:
        window['-SEARCH-'].update(disabled=False)
        window['-ROUTINE-'].update(disabled=False)

window.Close()


'''
	with open('lts.csv', 'a', newline='') as csv_file:
		csv_writer = csv.writer(csv_file)

		for LT in LTs:
			print(LT['Name'])
			csv_writer.writerow([LT['Name'] + '.PalletExitingFault'])
			csv_writer.writerow([LT['Name'] + '.PalletEnteringFault'])
			csv_writer.writerow([LT['Name'] + '.Faulted'])
'''
