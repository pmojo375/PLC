from pycomm3 import LogixDriver
from pycomm3.logger import configure_default_logger
import pandas
import yaml
from colorama import init, Fore, Back, Style
import time
from datetime import datetime
from autocast import autocast


# cast to the proper type using an external library
@autocast
def cast(arg):
    return arg


# reads the config yaml file
def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


# recursivly crawls through a tags structure so UDTs can be printed cleanly
def crawl(obj, layer, name):
    # a 'tab' for formating the output
    tab = '    '

    # obj is a dict
    if type(obj) is dict:
        print(f'{layer*tab}{name}:')
        # iterate though the dictionary
        for key, value in obj.items():
            # call function again while incrementing layer
            crawl(value, layer + 1, key)
    # obj is a list
    elif type(obj) is list:
        print(f'{layer*tab}{name}:')
        # iterate through the list
        for value in obj:
            crawl(value, layer + 1, name)
    # obj is an elementary object
    else:
        print(f'{tab*layer}{name} = {obj}')


# same function as 'crawl' but outputs a dictionary so the data can be saved to a CSV file
def crawl_and_format(obj, layer, name, data):
    # a 'tab' for formating the output
    tab = '    '

    # obj is a dict
    if type(obj) is dict:
        print(f'{layer*tab}{name}:')
        # iterate though the dictionary
        for key, value in obj.items():
            # call function again while incrementing layer
            data = crawl_and_format(value, layer + 1, f'{name}.{key}', data)
    # obj is a list
    elif type(obj) is list:
        print(f'{layer*tab}{name}[{len(obj)}]:')
        # iterate through the list
        for i, value in enumerate(obj):
            data = crawl_and_format(value, layer + 1, f'{name}[{i}]', data)
    # obj is an elementary object
    else:
        print(f'{tab*layer}{name} = {obj}')
        data[f'{name}'] = f'{obj}'

    return data


def main():
    # initialize the color text
    init(convert=True)

    # get config parameters
    config = read_yaml('config.yaml')
    debug = config['APP']['DEBUG']
    output_file = config['APP']['OUTPUT']
    out = output_file + '.csv'
    input_file = config['APP']['INPUT']
    use_default = config['APP']['DEFAULT_INPUT']
    input_file = input_file + '.csv'
    streamtime = int(config['APP']['STREAMFREQ'])
    splitout = config['APP']['SPLITOUT']

    # MIT license text
    lic = Style.RESET_ALL + Style.BRIGHT + Fore.BLUE + Back.WHITE + "**************************************************************************************" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   MIT License                                                                      *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*                                                                                    *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   Copyright (c) 2021 Parker Mojsiejenko                                            *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*                                                                                    *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   Permission is hereby granted, free of charge, to any person obtaining a copy     *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   of this software and associated documentation files (the \"Software\"), to deal    *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   in the Software without restriction, including without limitation the rights     *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell        *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   copies of the Software, and to permit persons to whom the Software is            *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   furnished to do so, subject to the following conditions:                         *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*                                                                                    *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   The above copyright notice and this permission notice shall be included in all   *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   copies or substantial portions of the Software.                                  *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*                                                                                    *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR       *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,         *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE      *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER           *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,    *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE    *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "*   SOFTWARE.                                                                        *" + Style.RESET_ALL + "\n" \
        + Style.BRIGHT + Fore.BLUE + Back.WHITE + "**************************************************************************************" + Style.RESET_ALL + "\n" \

    # if running debug mode, inform the user and configure the logger
    if debug:
        configure_default_logger()
        print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}{Back.RED}                                  RUNNING DEBUG MODE                                  {Style.RESET_ALL}\n{Style.BRIGHT}{Fore.YELLOW}{Back.RED}                           No PLC communitcation will happen                          {Style.RESET_ALL}\n{Style.BRIGHT}{Fore.YELLOW}{Back.RED}                  Disable debug mode by editing the config.yaml file                  {Style.RESET_ALL}{Style.BRIGHT}{Fore.WHITE}\n")

    # print the license and disclaimer
    print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.WHITE}{lic}")
    print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}{Back.RED}************************************** WARNING ***************************************{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}{Back.RED}* WHEN USED TO WRITE TO TAGS, THIS SCRIPT WILL OVERWRITE ANY EXISTING DATA WITH      *{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}{Back.RED}* NO WAY TO REVERT BACK TO THE ORIGINAL TAG DATA. PLEASE BACK UP YOUR PLC FILE       *{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}{Back.RED}* OR BE PREPARED TO LOSE ALL DATA!                                                   *{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}{Back.RED}* USE WITH CAUTION AS ALTERING TAG VALUES MAY CAUSE UNEXPECTED MOTION AND POTENTIAL  *{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}{Back.RED}* RISK OF INJURY OR LOSS OF LIFE TO YOURSELF AND/OR OTHERS! BY USING THIS SCRIPT,    *{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}{Back.RED}* YOU ASSUME ALL RISKS OF BOTH PERSONAL INJURY AND EQUIPMENT DAMAGE                  *{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}{Back.RED}**************************************************************************************{Style.RESET_ALL}\n")

    # request the PLC IP address if not configured to be set in the config.yaml file
    if 'IP' not in config['APP']:
        print(
            "Please be sure to enter the correct IP address (followed by an \"/x\" with \"x\"")
        print("being the slot number if using a chassis and not in slot 0) and include the")
        print("\".csv\" extention when entering your file name.\n")
        print(
            f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.GREEN}Enter IP address of your PLC:\n", end='')
        ip = input()
    else:
        ip = config['APP']['IP']
        print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.GREEN}IP address retrieved from config file as: {Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}{ip}")

    # if using default input file (set in config.yaml), inform the user
    if use_default:
        print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.GREEN}Input CSV file name retrieved from config file as: {Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}{input_file}")

    print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.GREEN}Output CSV file name (set in config file): {Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}{out}")

    print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.GREEN}\nWhat would you like to do?")
    print(' 1) Read a single tag\n 2) Write a single tag\n 3) Read multiple tags (tags are written to a CSV file)\n 4) Write multiple tags (tags and their values must be defined in a CSV file)\n 5) Trend a tag (trend stored in CSV)\n 6) Trend multiple tags (trend stored in CSV)\nEnter your choice:\n', end='')
    choice = int(input())

    # read a single tag
    if choice == 1:
        # request tag to read
        print(
            f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.GREEN}Enter tag name to read:\n", end='')
        tag = input()

        read_tag(ip, tag, debug)

    # write a single tag
    elif choice == 2:
        # request user input for the tag and desired value
        print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.GREEN}Enter tag name to write:\n{Style.RESET_ALL}{Style.BRIGHT}{Fore.WHITE}", end='')
        tag = input()
        print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.GREEN}Enter value to write:\n{Style.RESET_ALL}{Style.BRIGHT}{Fore.WHITE}", end='')
        value = input()

        # cast the value to the proper type
        value = cast(value)

        write_tag(ip, tag, value, debug)

    # read multiple tags from a CSV file and write the results to a CSV file
    elif choice == 3:
        # if config is set to use default file names, use them, otherwise request user imput
        if use_default:
            file_name = input_file
        else:
            print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.GREEN}Enter CSV file name with the first (and usually only) column being 'tag' (must be in same directory as the script!):\n", end='')
            file_name = input()
            print()  # print new line

        read_tags_from_CSV(file_name, ip, splitout, out, debug)

    # read multiple tags and their desired values from a CSV file and write to PLC
    elif choice == 4:
        # if using defult file names set in the config file, get the file name, otherwise request user input
        if use_default:
            file_name = input_file
        else:
            print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.GREEN}Enter CSV file name with 'tag' and 'value' columns (must be in same directory as the script!):\n", end='')
            file_name = input()
            # print a new line
            print()

        write_tags_from_CSV(file_name, ip, debug)

    # monitor a single tag at a specified interval
    elif choice == 5:
        # request the tag to monitor
        print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.GREEN}Enter tag name to read:\n{Style.RESET_ALL}{Style.BRIGHT}{Fore.WHITE}", end='')
        tag = input()

        # print info to user
        print(
            f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.WHITE}\nMonitoring tag, press CTRL+C to end stream\n")

        # print the results
        print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}Reading {tag}\n{Style.RESET_ALL}{Style.BRIGHT}{Fore.WHITE}")

        trend_tag(ip, tag, streamtime, out, debug)


    # monitor multiple tags set in a CSV file and write their results to another CSV file
    elif choice == 6:
        # check if using default input csv file or if one needs to be inputted
        if use_default:
            file_name = input_file
        else:
            print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.GREEN}Enter CSV file name with the first (and usually only) column being 'tag' (must be in same directory as the script!):\n{Style.RESET_ALL}{Style.BRIGHT}{Fore.WHITE}", end='')
            file_name = input()

        # make user aware of how to end loop
        print(
            f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.WHITE}Streaming tags, press CTRL+C to end stream\n")
            
        # read the csv into a dataframe
        df = pandas.read_csv(tags)

        # initalize a dictionary of dfs
        dfs = {}

        # create empty dfs for each tag
        for tag in df['tags']:
            dfs[tag] = pandas.DataFrame()

        trend_tags(ip, csv, dfs, splitout, streamtime, out, debug)

    # output a user prompt to inform them the program is over
    print(f'{Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW}')
    input(f"Press any key to close window")


def read_tag(ip, tag, debug):
    if not debug:
        with LogixDriver(ip) as plc:
            tag = plc.read(tag)

            # crawl though result (prints to terminal)
            crawl(tag.value, 0, tag.tag)
    else:
        # print debug text when in debug mode
        print(f'\nDEBUG MODE\n')
        print(f'Reading {tag}')


def write_tag(ip, tag, value, debug):
    if not debug:
        # write the tag values to the PLC
        with LogixDriver(ip) as plc:
            plc.write(tag, value)
    else:
        # print debug output if in debug mode
        print(f'\nDEBUG MODE\n')
        print(f'Writing {tag} with value {value}')


def read_tags_from_CSV(csv, ip, splitout, out, debug):

    # use pandas to read csv file
    df = pandas.read_csv(csv)

    dfOut = pandas.DataFrame()

    if not debug:
        with LogixDriver(ip) as plc:
            # iterate through the tags in the CSV file
            for index, data in df.iterrows():
                # read and store the results
                tagRead = plc.read(data['tag'])
                data = crawl_and_format(tagRead.value, 0, tagRead.tag, {})
                newData = {'tag': tagRead.tag,
                           'value': data[f'{tagRead.tag}']}

                if splitout:
                    # create empty data frame to aid in writing to CSV file
                    dfOut = pandas.DataFrame()

                # write the stored results to the data frame and write to CSV file
                dfOut = dfOut.append(newData, ignore_index=True)

                if splitout:
                    out_name = tagRead.tag.replace(".", "_") + '.csv'
                    dfOut.to_csv(out_name, index=False)
                else:
                    dfOut.to_csv(out, index=False)
    else:
        # print debug text when in debug mode
        print(f'\nDEBUG MODE\n')

        # iterate through the tags in the CSV file
        for index, data in df.iterrows():
            # print debug response if in debug mode
            print(f"Reading value of {data['tag']} and writing output to {out}")
            newData = {'tag': data['tag'], 'value': 'Tag Value'}

            if splitout:
                # create empty data frame to aid in writing to CSV file
                dfOut = pandas.DataFrame()

            # write the stored results to the data frame and write to CSV file
            dfOut = dfOut.append(newData, ignore_index=True)

            if splitout:
                out_name = tagRead.tag.replace(".", "_") + '.csv'
                dfOut.to_csv(out_name, index=False)
            else:
                dfOut.to_csv(out, index=False)


def write_tags_from_CSV(csv, ip, debug):

    # use pandas to read csv file
    df = pandas.read_csv(csv)

    if not debug:
        with LogixDriver(ip) as plc:
            # iterate through the tags read in the CSV file
            for index, data in df.iterrows():
                # write to the PLC
                plc.write(data['tag'], cast(data['value']))
    else:
        # print debug text when in debug mode
        print(f'\nDEBUG MODE\n')

        for index, data in df.iterrows():
            # if in debug mode, print the debug text
            print(f"Writing {data['tag']} with value {data['value']}")


def trend_tag(ip, tag, streamtime, out, debug, **kwargs):

    dfOut = kwargs.get('df', pandas.DataFrame())

    if not debug:
        # current date and time
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y %H:%M:%S")

        # read the tag from the PLC
        with LogixDriver(ip) as plc:
            result = plc.read(tag)

            # crawl through the result and store results
            data = crawl_and_format(
                result.value, 0, result.tag, {})

            # add the timestamp to the results
            data['timestamp'] = date_time

        # append data to the data frame
        dfOut = dfOut.append(data, ignore_index=True)

        if not dfOut.columns.get_loc('timestamp') == 0:
            # shift column 'timestamp' to first position
            first_column = dfOut.pop('timestamp')

            # insert column using insert(position, column_name, first_column) function
            dfOut.insert(0, 'timestamp', first_column)

        # output to CSV file
        dfOut.to_csv(out, index=False)

        # sleep a number of seconds set in the config file
        time.sleep(streamtime)
    else:
        # print debug text when in debug mode
        print(f'\nDEBUG MODE\n')

        # current date and time
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y %H:%M:%S")

        # dummy data to test
        dummy_data = {'Status': 0, 'RejectCode': 0, 'Model': {'Name': '', 'ModelNum': '', 'TallPart': False, 'ShortPart': False, 'UEF_Galv': False, 'UEF_Coated': False}, 'Barcode': '', 'Sta3000_HipotTestStatus': 0, 'Sta5000_LeakTestStatus': 0, 'Sta5000_EnclosureScrew1': {'Torque': 0.0, 'Angle': 0.0}, 'Sta5000_EnclosureScrew2': {'Torque': 0.0, 'Angle': 0.0}, 'Sta5000_EnclosureScrew3': {'Torque': 0.0, 'Angle': 0.0}, 'Sta5000_EnclosureScrew4': {'Torque': 0.0, 'Angle': 0.0}, 'Sta6000_HighVoltageTest': {'Status': 0, 'ContinuityTest': {'Status': '', 'Resistance': 0.0}, 'ACWTest': {'Status': '', 'Volts': 0.0, 'TotalAmps': 0.0, 'RealAmps': 0.0}, 'RunTest': {'Status': '', 'Volts': 0.0, 'Amps': 0.0, 'Watts': 0.0, 'RawVolts': 0.0, 'RawAmps': 0.0, 'RawWatts': 0.0, 'TestTime': 0.0, 'PowerFactor': 0.0}, 'PassedContinuity': False, 'PassedHiPot': False, 'PassedRun': False, 'VoltageInRange': False, 'CurrentInRange': False, 'PowerInRange': False}, 'Sta6000_LowVoltageTest': {'Status': 0, 'ContinuityTest': {'Status': '', 'Resistance': 0.0}, 'ACWTest': {'Status': '', 'Volts': 0.0, 'TotalAmps': 0.0, 'RealAmps': 0.0}, 'RunTest': {'Status': '', 'Volts': 0.0, 'Amps': 0.0, 'Watts': 0.0, 'RawVolts': 0.0, 'RawAmps': 0.0, 'RawWatts': 0.0, 'TestTime': 0.0, 'PowerFactor': 0.0}, 'PassedContinuity': False, 'PassedHiPot': False, 'PassedRun': False, 'VoltageInRange': False,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           'CurrentInRange': False, 'PowerInRange': False}, 'Sta6000_LeakTestStatus': 0, 'Sta7000_TerminalPlateScrew': {'Torque': 0.0, 'Angle': 0.0}, 'Sta3000_Rework_Count': 0, 'Sta4000_UEFPlace_Status': 0, 'Sta5000_Rework_Status': 0, 'Sta6000_Lane_Status': 0, 'Sta2000_LoopNum': 0, 'Sta1000_ReleaseTime': {'Year': 0, 'Month': 0, 'Day': 0, 'Hour': 0, 'Minute': 0, 'Second': 0, 'Microsecond': 0}, 'Sta2000_ReleaseTime': {'Year': 0, 'Month': 0, 'Day': 0, 'Hour': 0, 'Minute': 0, 'Second': 0, 'Microsecond': 0}, 'Sta7000_UnloadTime': {'Year': 0, 'Month': 0, 'Day': 0, 'Hour': 0, 'Minute': 0, 'Second': 0, 'Microsecond': 0}, 'PalletNum': 0, 'TestRecord': {'Base': '', 'Matrix': '', 'DateTime': '', 'TestResults': [{'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}, {'Status': 0, 'Value': 0.0}], 'TestLane': 0, 'MasterFail': 0, 'FailTest': 0, 'ProdLine': 74}, 'Tracking': 0}
        data = crawl_and_format(dummy_data, 0, 'PalletRecords[1]', {})

        # add the timestamp to the results
        data['timestamp'] = date_time

        # append data to the data frame
        dfOut = dfOut.append(data, ignore_index=True)

        print(f"Timestamp column location: {dfOut.columns.get_loc('timestamp')}")

        if not dfOut.columns.get_loc('timestamp') == 0:
            # shift column 'timestamp' to first position
            first_column = dfOut.pop('timestamp')

            # insert column using insert(position, column_name, first_column) function
            dfOut.insert(0, 'timestamp', first_column)

        # output to CSV file
        dfOut.to_csv(out, index=False)

        # sleep a number of seconds set in the config file
        time.sleep(streamtime)

    return dfOut

def trend_tags(ip, df, dfs, csv, splitout, streamtime, out, debug, **kwargs):

    input_csv_data = pandas.read_csv(csv)

    if not splitout:
        # get the df with the trend data or create an empty one
        dfOut = df
    else:
        # if splitting out, copy the dfs to the dfOut variable
        dfOut = dfs

    # inform the user tags are being read
    print(f"Reading tags\n")

    # create empty array to store the data
    tags = []

    # create the header and an array of the tags
    for index, data in input_csv_data.iterrows():
        tags.append(data['tag'])

    # print the results
    print('Reading the following tags:')
    print(f"{tags}\n")

    if not debug:
        # create the initial data dict
        data = {}

        # open the PLC connection
        with LogixDriver(ip) as plc:
            # outputs a list of results
            tagsRead = plc.read(*tags)

        # loop through the results and crawl through them to store
        for result in tagsRead:

            # if splitting out the results overwrite the original data dint
            if splitout:
                data = {}

            # format the data
            data = crawl_and_format(
                result.value, 0, result.tag, data)

            # add the timestamp to the results
            data['timestamp'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

            # if splitting out, process the df and write to the csv output
            if splitout:
                # append the results to an empty data frame
                dfOut[result.tag] = dfOut[result.tag].append(
                    data, ignore_index=True)

                # avoid the processing if the timestamp is moved already
                if not dfOut[result.tag].columns.get_loc('timestamp') == 0:

                    # shift column 'timestamp' to first position
                    first_column = dfOut[result.tag].pop('timestamp')

                    # insert column using insert(position, column_name, first_column) function
                    dfOut[result.tag].insert(
                        0, 'timestamp', first_column)

                # create the output file name from the tag name
                out_name = result.tag.replace(".", "_") + '.csv'

                # write to the csv file
                dfOut[result.tag].to_csv(out_name, index=False)

        # if not splitting out, write all data to the output df
        if not splitout:
            # add the timestamp to the results
            data['timestamp'] = date_time

            # append the results to an empty data frame
            dfOut = dfOut.append(data, ignore_index=True)

            # avoid the processing if the timestamp is moved already
            if not dfOut.columns.get_loc('timestamp') == 0:

                # shift column 'timestamp' to first position
                first_column = dfOut.pop('timestamp')

                # insert column using insert(position, column_name, first_column) function
                dfOut.insert(0, 'timestamp', first_column)

            # output data to CSV file
            dfOut.to_csv(out, index=False)

        # wait a number of seconds set in the config file
        time.sleep(streamtime)
    else:
        # print debug text when in debug mode
        print(f'\nDEBUG MODE\n')
        
        data = {}

        # loop throught the tags read from the CSV file
        for result in tags:

            # if splitting out the results overwrite the original data dint
            if splitout:
                data = {}

            # add the time stamp to the results
            data['timestamp'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

            # store dummy result 'value'
            data[result] = 'value'

            if splitout:

                # append the results to an empty data frame
                dfOut[result] = dfOut[result].append(
                    data, ignore_index=True)

                # avoid the processing if the timestamp is moved already
                if not dfOut[result].columns.get_loc('timestamp') == 0:

                    # shift column 'timestamp' to first position
                    first_column = dfOut[result].pop('timestamp')

                    # insert column using insert(position, column_name, first_column) function
                    dfOut[result].insert(0, 'timestamp', first_column)

                # create the output file name from the tag name
                out_name = result.replace(".", "_") + '.csv'

                # write to the csv file
                dfOut[result].to_csv(out_name, index=False)

                # print the results
                print(f"{data}")

        if not splitout:

            # print the results
            print(f'{data}')

            # append the results to an empty data frame
            dfOut = dfOut.append(data, ignore_index=True)

            # avoid the processing if the timestamp is moved already
            if not dfOut.columns.get_loc('timestamp') == 0:

                # shift column 'timestamp' to first position
                first_column = dfOut.pop('timestamp')

                # insert column using insert(position, column_name, first_column) function
                dfOut.insert(0, 'timestamp', first_column)

            # output data to CSV file
            dfOut.to_csv(out, index=False)

        # wait a number of seconds set in the config file
        time.sleep(streamtime)

    return dfOut

def get_tags(ip):
    with LogixDriver(ip) as plc:
        return plc.get_tag_list()


if __name__ == "__main__":
    main()
