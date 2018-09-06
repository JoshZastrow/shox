import pandas as pd
import numpy as np
import os
import json
from pandas import ExcelWriter
from utils import query_yes_no
import argparse
import ast

def unpack_data_column(data):
    """
    Processing script that takes a "Data" column, where
    the values are in the form of a dictionary, and unpacks
    them so the result is a standard dataframe with all fields
    in their own column.
    """
    d = []
    for col, row in data.iterrows():
        fields = ast.literal_eval(row['Data'])
        fields['ImageURL'] = row['imageURL']
        fields['Retailer'] = row['Retailer']
        fields['Data'] = row['Data']
        d.append(fields)
    
    data = pd.DataFrame(d)
    
    return data


def get_tags():
    """
    pulls list of tags from tag.csv file
    """
    curr_dir = os.getcwd().split('\\')[-1]
    if curr_dir == 'data':
        file = 'meta/tags.csv'
    else:
        file = 'data/meta/tags.csv'

    assert os.path.isfile(file), 'Cannot find tag file. Tag file should be in ~/data/meta/tags.csv'
    return set(pd.read_csv(file ,header=None, names=['tag'])['tag'].str.lower())


def get_mvpTags():
    """
    mvp tag file, loads into python as a dictionary: key <tag> : value <mvp tag>
    """
    curr_dir = os.getcwd().split('\\')[-1]
    if curr_dir == 'data':
        file = 'meta/mvp.json'
    else:
        file = 'data/meta/mvp.json'

    with open(file, 'r') as fp:
        mvp = json.load(fp)

    return mvp

def label(x, tags):
    """
    Labeling function. Takes in a string and searches for a match against a set of
    pre-defined tag words.
    inputs:
        x <str>: string of words
        tags <set>: unordered set of words

    outputs:
        word <str>: the matching word. If no match, returns NaN
    """
    x = x.replace('-', ' ')  # text processing for split operation
    description = x.split()
    for word in description:
        if word.lower() in tags:
            return word.lower()
    else:
        return np.nan


def add_tags(data):
    '''
    Dataframe modifying function. Adds two columns for tags and MVP tags,
    then outputs the resulting dataframe. Tags are retrieved from a csv list of tags,
    mvp tags are from a dictionary mapping tags to MVP tags.
    input:
        Pandas DataFrame
    output:
        Pandas DataFrame
    '''

    tags = get_tags()
    mvp = get_mvpTags()

    assert 'Product Name' in data.columns, 'Column: Product Name not found in csv'
    data['tag'] = data.apply(lambda x: label(x['Product Name'], tags), axis=1)
    data['mvp'] = data.apply(lambda x: mvp.get(x['tag'], np.nan), axis=1)
    data['image'] = data.ImageURL.apply(lambda x: '=IMAGE("{}")'.format(x))
    data['timestamp'] = pd.datetime.now()

    return data


def write_data(data, filename):
    """
    Writes a pandas dataframe to a designated CSV file in a 'processed' folder.
    If the file already exists, the data is added to the file.
    """
    
    data_COM = data.loc[:, ['ImageURL', 'Data', 'tag']]
    data_HUM = data.drop(['Data'], axis=1)

    fpath_COM = 'C019_processed'
    fpath_HUM = 'C019_to_review'
     
    for data, fpath in zip([data_COM, data_HUM], [fpath_COM, fpath_HUM]):
        print('\nWriting processed data to {}...\n'.format(fpath))
        
        if not os.path.isdir(fpath):
           os.makedirs(fpath)

        fpath = '{}/{}'.format(fpath, filename)

        if not os.path.isfile(fpath):
            data.to_csv(fpath, index=False)

        else:
            overwrite = query_yes_no('Data already processed. Overwrite existing file?')

            if overwrite:
                print('overwriting file {}'.format(fpath))
                data.to_csv(fpath, index=False)

            else:
                append = query_yes_no('Add data to existing processed file?')
                if append:
                    # Check for matching columns
                    curr_cols = pd.read_csv(fpath, nrows=1).columns
                    same_length = len(data.columns) == len(curr_cols)
                    assert (same_length), 'Number of columns of processed data do not match database'

                    same_column = (data.columns == curr_cols).all()
                    assert same_column, 'Column names of processed data do not match database'

                    print('Adding data to file {}'.format(fpath))
                    data.to_csv(fpath, mode='a', index_label='Index')
                else:
                    print('Please modify name of existing processed file {} and re-run the program.'.format(fpath.split('/')[-1]))


def check_data(filename, reference_file=None):

    data = pd.read_csv('data/2-1_processed/{}'.format(filename))

    total_rows = data.shape[0]
    not_tagged = data[data.tag.isnull()].shape[0]

    # Create metrics
    new_row = {
        'Filename': filename,
        'rowCount': total_rows,
        'Labeled': total_rows - not_tagged,
        'Missed': not_tagged
        }

    # if there are already metrics, retrieve them then add
    if os.path.isfile('data/3_monitor/data.xlsx'):

        # Get data, add row, write back to sheet
        next_row.to_excel()

    else:
        report = pd.DataFrame(new_row)

    if reference_sheet:
        pass

    # write to data sheet
    if not os.path.isdir('monitor'): os.makedirs('monitor')
    writer = ExcelWriter('monitor/data.xlsx', 'data')
    report.to_excel(writer,'data')
    writer.save()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process Scraping date: Adding timestamp and product tags.')
    parser.add_argument('filename', metavar='file', type=str,
                        help='The file name of the scraper file (i.e 2018-08-24_zalora.csv)')

    args = parser.parse_args()
    
    file = args.filename
    
    assert os.path.isfile(file), 'Error: cannot find file. Make sure file is spelled correctly and is located in current directory'

    # Processing Steps. Scraper file has no headers FYI
    column_names = ['imageURL', 'Data', 'Retailer']
    data = pd.read_csv(file, encoding='latin1', header=None, names=column_names)
    data = unpack_data_column(data)
    data = add_tags(data)

    print('Checking for a data folder, files will be stored there..')

    # Are we in the data folder? Create one if it doesn't exist
    curr_dir = os.getcwd().split('\\')[-1]
    if curr_dir != 'data':
        if not os.path.isdir('data'):
            os.path.makedirs('data')
        os.chdir('data')

    write_data(data, file)