import PySimpleGUI as sg
import plc
import pandas
import threading
import queue

ip = '192.168.1.1'
debug = True
# initalize a dictionary of dfs
dfs = {}
stop_trend = False
print('Creating DFs')
trendtag_dfOut = pandas.DataFrame()
trendtags_dfOut = pandas.DataFrame()

sg.theme('DarkAmber')   # Add a touch of color
def make_main_window():
    frame_layout = [[sg.T('IP Address:', size=(15,1)), sg.In(key='-IP-', size=(27,1))],
                   [sg.T('Output Filename:', size=(15,1)), sg.In(key='-OUTFILENAME-', size=(27,1))],
                   [sg.Checkbox('Output seperate CSV files?', key='-SPLIT-'),sg.Spin([i for i in range(1,61)], initial_value=1, key='-FREQ-'), sg.Text('Read Frequency')]]

    layout = [[sg.Frame('Config', frame_layout)],
             [sg.Text('Read a single PLC tag:', size=(20,1)), sg.B('Read Single Tag', key='-READTAG-', size=(20,1))],
             [sg.Text('Write a single PLC tag:', size=(20,1)), sg.B('Write Single Tag', key='-WRITETAG-', size=(20,1))],
             [sg.Text('Read multiple PLC tags:', size=(20,1)), sg.B('Read Multiple Tags', key='-READTAGS-', size=(20,1))],
             [sg.Text('Write multiple PLC tags:', size=(20,1)), sg.B('Write Multiple Tags', key='-WRITETAGS-', size=(20,1))],
             [sg.Text('Trend a PLC tag:', size=(20,1)), sg.B('Trend Single Tag', key='-TRENDTAG-', size=(20,1))],
             [sg.Text('Trend multiple PLC tags:', size=(20,1)), sg.B('Trend Multiple Tags', key='-TRENDTAGS-', size=(20,1))],
             [sg.Text('Get PLC tags:', size=(20,1)), sg.B('Get Tags', key='-GETTAGS-', size=(20,1))],
             [sg.Button('Close')]]

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

def trend_tag(ip, tag, freq, output_filename, debug, main_window):
    global trendtag_dfOut
    trendtag_dfOut = plc.trend_tag(ip, tag, freq, output_filename, debug, df=trendtag_dfOut)

    main_window.write_event_value('-TRENDINGTAG-', '** DONE **')

    print('Thread Done')

def trend_tags(ip, csv, split, freq, output_filename, debug, main_window):
    global trendtags_dfOut
    global dfs
    trendtags_dfOut = plc.trend_tags(ip, trendtags_dfOut, dfs, csv, split, freq, output_filename, debug)

    main_window.write_event_value('-TRENDINGTAGS-', '** DONE **')

    print('Thread Done')

# Create the Window
main_window, trend_window = make_main_window(), None

# Event Loop to process "events" and get the "values" of the inputs
while True:
    window, event, values = sg.read_all_windows()
    print(window, event, values)     
    if window == main_window:
        ip = values['-IP-']
        freq = int(values['-FREQ-'])
        split = values['-SPLIT-']
        output_filename = values['-OUTFILENAME-']

        if not data_entered(output_filename):
            output_filename = 'out.csv'

    if window == main_window and event in (sg.WIN_CLOSED, 'Close'):
        break


    if event == '-READTAG-':
        if data_entered(ip):
            tag = sg.popup_get_text('Enter tag name to read:')

            if tag == '':
                sg.popup('Please enter a tag!')
            else:
                print(f'Reading {tag}')

                plc.read_tag(ip, tag, debug)
        else:
            sg.popup('No IP Address Entered!')


    if event == '-WRITETAG-':
        if data_entered(ip):
            tag = sg.popup_get_text('Enter tag name to write to:')
            value = plc.cast(sg.popup_get_text('Enter value to write:'))

            if tag == '' or value == '':
                if tag == '':
                    sg.popup('Tag must be entered!')
                elif tag == '':
                    sg.popup('Value must be entered!')
            else:
                print(f'Writing {value} to {tag}')

                plc.write_tag(ip, tag, value, debug)
        else:
            sg.popup('No IP Address Entered!')


    if event == '-READTAGS-':
        if data_entered(ip):
            csv = sg.popup_get_file('Locate CSV with tag names:', file_types = (('CSV','*.csv'),), initial_folder='./')

            if csv == '':
                sg.popup('CSV file required!')
            else:
                print(f'Filename {csv}')

                print(f'Reading tags')

                plc.read_tags_from_CSV(csv, ip, split, output_filename, debug)
        else:
            sg.popup('No IP Address Entered!')


    if event == '-WRITETAGS-':
        if data_entered(ip):
            csv = sg.popup_get_file('Locate CSV with tag names and values to write:', file_types = (('CSV','*.csv'),), initial_folder='./')

            if csv == '':
                sg.popup('CSV file required!')
            else:
                print(f'Filename {csv}')

                print(f'Writing tags')

                plc.write_tags_from_CSV(csv, ip, debug)
        else:
            sg.popup('No IP Address Entered!')


    if event == '-TRENDTAG-':
        if data_entered(ip):
            tag = sg.popup_get_text('Enter tag name to trend:')

            if tag == '':
                sg.popup('Please enter a tag!')
            else:
                print(f'Trending {tag}')

                trend_window = make_trend_window()
                thread = threading.Thread(target=trend_tag, args=(ip, tag, freq, output_filename, debug, main_window), daemon=True)
                thread.start()

        else:
            sg.popup('No IP Address Entered!')


    if event == '-TRENDTAGS-':
        if data_entered(ip):
            csv = sg.popup_get_file('Locate CSV with tag names to trend:', file_types = (('CSV','*.csv'),), initial_folder='./')

            if csv == '' or type(csv) == None:
                sg.popup('CSV file required!')
            else:

                # read the csv into a dataframe
                df = pandas.read_csv(csv)

                # create empty dfs for each tag
                for tag in df['tag']:
                    dfs[tag] = pandas.DataFrame()

                trend_window = make_trend_window()
                thread = threading.Thread(target=trend_tags, args=(ip, csv, split, freq, output_filename, debug, main_window), daemon=True)
                thread.start()

        else:
            sg.popup('No IP Address Entered!')


    if event == '-GETTAGS-':
        if data_entered(ip):
            tags = plc.get_tags(ip)
            sg.popup_scrolled(tags, title='PLC Tags')
        else:
            sg.popup('No IP Address Entered!')

    # Trend window stuff
    if window == trend_window and event in(sg.WIN_CLOSED, '-STOP-'):
            trend_window.close()
            trend_window = None

            stop_trend = True


    if event == '-TRENDINGTAG-':
        if not stop_trend:
            print('Recalling Thread')
            thread = threading.Thread(target=trend_tag, args=(ip, tag, freq, output_filename, debug, main_window), daemon=True)
            thread.start()
        else:
            print('Trend Stopped')

    if event == '-TRENDINGTAGS-':
        if not stop_trend:
            print('Recalling Thread')
            thread = threading.Thread(target=trend_tags, args=(ip, csv, split, freq, output_filename, debug, main_window), daemon=True)
            thread.start()
        else:
            print('Trend Stopped')

    print('Loop End')
main_window.close()
