from pycomm3 import LogixDriver
import pandas
import yaml
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
def crawl(obj, layer, name, string):
    # a 'tab' for formating the output
    tab = '    '

    # obj is a dict
    if type(obj) is dict:
        print(f'{layer*tab}{name}:')
        string.append(f'{layer*tab}{name}:')
        # iterate though the dictionary
        for key, value in obj.items():
            # call function again while incrementing layer
            string.append(crawl(value, layer + 1, key, string))
    # obj is a list
    elif type(obj) is list:
        print(f'{layer*tab}{name}:')
        string.append(f'{layer*tab}{name}:')
        # iterate through the list
        for value in obj:
            string.append(crawl(value, layer + 1, name, string))
    # obj is an elementary object
    else:
        print(f'{tab*layer}{name} = {obj}')
        string.append(f'{tab*layer}{name} = {obj}')

    return string

# same function as 'crawl' but outputs a dictionary so the data can be saved to a CSV file


def crawl_and_format(obj, layer, name, data):
    # a 'tab' for formating the output
    tab = '    '

    # obj is a dict
    if type(obj) is dict:
        # iterate though the dictionary
        for key, value in obj.items():
            # call function again while incrementing layer
            data = crawl_and_format(value, layer + 1, f'{name}.{key}', data)
    # obj is a list
    elif type(obj) is list:
        # iterate through the list
        for i, value in enumerate(obj):
            data = crawl_and_format(value, layer + 1, f'{name}[{i}]', data)
    # obj is an elementary object
    else:
        data[f'{name}'] = f'{obj}'

    return data


def read_tag(ip, tag):
    with LogixDriver(ip) as plc:
        tag = plc.read(tag)

    return tag.value


def write_tag(ip, tag, value):
    # write the tag values to the PLC
    with LogixDriver(ip) as plc:
        plc.write(tag, value)


def read_tags_from_CSV(csv, ip, splitout, out):

    # use pandas to read csv file
    df = pandas.read_csv(csv)

    dfOut = pandas.DataFrame()

    ret_data = {}
    temp_data = {}

    with LogixDriver(ip) as plc:
        # iterate through the tags in the CSV file
        for index, data in df.iterrows():
            # read and store the results
            tagRead = plc.read(data['tag'])

            if splitout:
                # create empty data frame to aid in writing to CSV file
                dfOut = pandas.DataFrame()

            temp_data = crawl_and_format(tagRead.value, 0, tagRead.tag, {})

            # write the stored results to the data frame and write to CSV file
            dfOut = dfOut.append(temp_data, ignore_index=True)

            if splitout:
                out_name = tagRead.tag.replace(".", "_") + '.csv'
                dfOut.to_csv(out_name, index=False)
            else:
                dfOut.to_csv(out, index=False)

            ret_data = {**ret_data, **{tagRead.tag: tagRead.value}}

    return ret_data

def write_tags_from_CSV(csv, ip):

    # use pandas to read csv file
    df = pandas.read_csv(csv)

    with LogixDriver(ip) as plc:
        # iterate through the tags read in the CSV file
        for index, data in df.iterrows():
            # write to the PLC
            plc.write(data['tag'], cast(data['value']))


def trend_tag(ip, tag, out, plc, **kwargs):

    # get the currently used df to append to or create new
    dfOut = kwargs.get('df', pandas.DataFrame())

    # current date and time
    date_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    # read the tag from the PLC
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

        # insert column using insert function
        dfOut.insert(0, 'timestamp', first_column)

    # output to CSV file
    dfOut.to_csv(out, index=False)

    return dfOut

def trend_tags(ip, df, dfs, csv, splitout, out, plc):

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

    # create the initial data dict
    data = {}

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
        data['timestamp'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

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

    return dfOut


def get_tags(ip):
    with LogixDriver(ip) as plc:
        tags = plc.get_tag_list()

        tags = [d['tag_name'] for d in tags if 'tag_name' in d]

        return tags
