import PySimpleGUI as sg
import plc
from pycomm3 import LogixDriver
import pandas
import threading
import yaml
import socket
from pprint import pformat
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
import csv
import re

scheduler = BackgroundScheduler()
soup = None
l5x_tags = None


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


def valid_ip(address):
    try:
        socket.inet_aton(address)
        return True
    except:
        return False


# reads the config yaml file
def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


debug = False

# initalize a dictionary of dfs
dfs = {}
trendtag_dfOut = pandas.DataFrame()
trendtags_dfOut = pandas.DataFrame()

sg.theme('Dark')   # Add a touch of color

# get config parameters
config = read_yaml('state.yaml')
ip = config['APP']['IP']
readtag = config['APP']['READTAG']
plc_connection = None

def make_main_window():

    frame_layout1 = [[sg.T('You must specify and read the PLC L5X file before you can search. Select file below and press the "Read" button to enable the features below.', size=(63, 2))],
                   [sg.Text('L5X File'), sg.Input(key='-L5X-'), sg.FileBrowse(), sg.B('Read', key='-READFILE-', size=(5,1))], 
                   [sg.T('L5X FILE NOT READ', key='-FILEREAD-', justification='center', size=(63,1))]]

    tab_layout1 = [[sg.Frame('Initial Read', frame_layout1)],
             [sg.T('Datatype', size=(14, 1), justification='right'), sg.I('Cylinder', key='-DATATYPE-', disabled=True, size=(41, 1)), sg.B('Find Instances', key='-FIND-', disabled=True, size=(11, 1))],
             [sg.T('Routine To Search', size=(14, 1), justification='right'), sg.I('R05_Faults', key='-ROUTINE-', disabled=True, size=(41, 1)), sg.B('Search', key='-SEARCH-', disabled=True, size=(11, 1))]]

    frame_layout2 = [[sg.T('IP Address:', size=(15, 1)), sg.In(ip, key='-IP-', size=(27, 1))],
                    [sg.T('Output Filename:', size=(15, 1)), sg.In(
                        key='-OUTFILENAME-', size=(27, 1))],
                    [sg.Checkbox('Output seperate CSV files?', key='-SPLIT-'), sg.Spin([i for i in range(1, 61)], initial_value=1, key='-FREQ-'), sg.Text('Read Frequency')]]

    tab_layout2 = [[sg.Frame('Config', frame_layout2)],
              [sg.Text('Read a single PLC tag:', size=(20, 1)), sg.B(
                  'Read Single Tag', key='-READTAG-', size=(20, 1))],
              [sg.Text('Write a single PLC tag:', size=(20, 1)), sg.B(
                  'Write Single Tag', key='-WRITETAG-', size=(20, 1))],
              [sg.Text('Read multiple PLC tags:', size=(20, 1)), sg.B(
                  'Read Multiple Tags', key='-READTAGS-', size=(20, 1))],
              [sg.Text('Write multiple PLC tags:', size=(20, 1)), sg.B(
                  'Write Multiple Tags', key='-WRITETAGS-', size=(20, 1))],
              [sg.Text('Trend a PLC tag:', size=(20, 1)), sg.B(
                  'Trend Single Tag', key='-TRENDTAG-', size=(20, 1))],
              [sg.Text('Trend multiple PLC tags:', size=(20, 1)), sg.B(
                  'Trend Multiple Tags', key='-TRENDTAGS-', size=(20, 1))],
              [sg.Text('Get PLC tags:', size=(20, 1)), sg.B(
                  'Get Tags', key='-GETTAGS-', size=(20, 1))]]

    layout = [[sg.TabGroup([[sg.Tab('PLC', tab_layout2), sg.Tab('L5X', tab_layout1)]])], [sg.Button('Close')]]

    return sg.Window('PLC', layout, finalize=True)


def make_trend_window():
    trend_layout = [[sg.T('Trending Tag. Press stop below to end the trend')],
                    [sg.B('Stop', key='-STOP-')]]

    return sg.Window('Trending', trend_layout, finalize=True)


def data_entered(data):
    if data == '':
        return False
    else:
        return True


def trend_tag_job():
    global trendtag_dfOut

    trendtag_dfOut = plc.trend_tag(
        ip, tag, output_filename, plc_connection, df=trendtag_dfOut)


def trend_tag():
    global plc_connection
    plc_connection = LogixDriver(ip)
    plc_connection_ok = plc_connection.open()

    scheduler.add_job(trend_tag_job, 'interval',
                      seconds=freq, id='trend_tag_job')
    scheduler.start()


def trend_tags_job():
    global trendtags_dfOut

    trendtags_dfOut = plc.trend_tags(
        ip, trendtags_dfOut, dfs, csv, split, output_filename, plc_connection)


def trend_tags():
    global plc_connection

    plc_connection = LogixDriver(ip)
    plc_connection_ok = plc_connection.open()
    scheduler.add_job(trend_tags_job, 'interval',
                      seconds=freq, id='trend_tags_job')
    scheduler.start()


# Create the Window
main_window, trend_window = make_main_window(), None

status = main_window['-FILEREAD-']
# Event Loop to process "events" and get the "values" of the inputs
while True:
    window, event, values = sg.read_all_windows()

    print(window)
    if window == main_window:
        ip = values['-IP-']
        freq = float(values['-FREQ-'])
        split = values['-SPLIT-']
        output_filename = values['-OUTFILENAME-']
        file_name = values['-L5X-']
        routine_name = values['-ROUTINE-']
        datatype = values['-DATATYPE-']

        if not data_entered(output_filename):
            output_filename = 'out.csv'

    # break loop if window is closed
    if window == main_window and event in (sg.WIN_CLOSED, 'Close'):
        break

    if event == '-READTAG-':
        if data_entered(ip) and valid_ip(ip):
            tag = sg.popup_get_text(
                'Enter tag name to read:', default_text=readtag)

            if tag == '':
                sg.popup('Please enter a tag!')

            else:
                print(f'Reading {tag}')

                results = plc.read_tag(ip, tag)

                if results is None:
                    sg.popup(
                        'Nothing returned. Tag possibly does not exist in PLC.')
                else:
                    sg.popup_scrolled(pformat(results, depth=10, width=100))
        else:
            sg.popup('Enter a valid IP Address')

    if event == '-WRITETAG-':
        if data_entered(ip) and valid_ip(ip):
            tag = sg.popup_get_text('Enter tag name to write to:')
            value = plc.cast(sg.popup_get_text('Enter value to write:'))

            if tag == '' or value == '':
                if tag == '':
                    sg.popup('Tag must be entered!')
                elif value == '':
                    sg.popup('Value must be entered!')
            else:
                print(f'Writing {value} to {tag}')

                plc.write_tag(ip, tag, value)
        else:
            sg.popup('Enter a valid IP Address')

    if event == '-READTAGS-':
        if data_entered(ip) and valid_ip(ip):
            csv = sg.popup_get_file('Locate CSV with tag names:', file_types=(
                ('CSV', '*.csv'),), initial_folder='./')

            if csv == '' or csv is None:
                sg.popup('CSV file required!')
            else:
                print(f'Filename {csv}')
                print(f'Filename {type(csv)}')

                print(f'Reading tags')

                results = plc.read_tags_from_CSV(
                    csv, ip, split, output_filename)

                if results is None:
                    sg.popup('Nothing returned. Tags may not exist in PLC.')
                else:
                    sg.popup_scrolled(pformat(results, depth=10, width=100))
        else:
            sg.popup('Enter a valid IP Address')

    if event == '-WRITETAGS-':
        if data_entered(ip) and valid_ip(ip):
            csv = sg.popup_get_file('Locate CSV with tag names and values to write:', file_types=(
                ('CSV', '*.csv'),), initial_folder='./')

            if csv == '' or csv is None:
                sg.popup('CSV file required!')
            else:
                print(f'Filename {csv}')

                print(f'Writing tags')

                plc.write_tags_from_CSV(csv, ip)
        else:
            sg.popup('Enter a valid IP Address')

    if event == '-TRENDTAG-':
        if data_entered(ip) and valid_ip(ip):
            tag = sg.popup_get_text('Enter tag name to trend:')

            if tag == '':
                sg.popup('Please enter a tag!')
            else:
                print(f'Trending {tag}')

                trend_window = make_trend_window()
                thread = threading.Thread(target=trend_tag, daemon=True)
                thread.start()

        else:
            sg.popup('Enter a valid IP Address')

        print('TrendEnd')

    if event == '-TRENDTAGS-':
        if data_entered(ip) and valid_ip(ip):
            csv = sg.popup_get_file('Locate CSV with tag names to trend:', file_types=(
                ('CSV', '*.csv'),), initial_folder='./')

            if csv == '' or type(csv) is None:
                sg.popup('CSV file required!')
            else:
                # read the csv into a dataframe
                df = pandas.read_csv(csv)

                dfs = {}

                # create empty dfs for each tag
                for tag in df['tag']:
                    dfs[tag] = pandas.DataFrame()

                trend_window = make_trend_window()
                thread = threading.Thread(target=trend_tags, daemon=True)
                thread.start()

        else:
            sg.popup('Enter a valid IP Address')

    if event == '-GETTAGS-':
        if data_entered(ip) and valid_ip(ip):
            tags = plc.get_tags(ip)
            sg.popup_scrolled(tags, title='PLC Tags')
        else:
            sg.popup('Enter a valid IP Address')

    if event == '-FIND-':
        l5x_tags = find_all_tags(soup)

    if event == '-READFILE-':
        soup = read_L5X(file_name)

    if event == '-SEARCH-':
        missing = search_routines(routine_name, soup, l5x_tags)

    if window == main_window and not soup == None:
        status.update(value='L5X READ')

        window['-FIND-'].update(disabled=False)
        window['-DATATYPE-'].update(disabled=False)

    if window == main_window and not l5x_tags == None:
        window['-SEARCH-'].update(disabled=False)
        window['-ROUTINE-'].update(disabled=False)

    # Trend window stuff
    if window == trend_window and event in (sg.WIN_CLOSED, '-STOP-'):
        trend_window.close()
        trend_window = None

        jobs = scheduler.get_jobs()

        for job in jobs:
            scheduler.remove_job(job.name)

        plc_connection.close()

    print('Loop End')

main_window.close()
