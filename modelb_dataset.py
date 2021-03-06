# libraries
import pandas as pd
import numpy as np
from keras.utils import np_utils
from sklearn.preprocessing import LabelEncoder
from flask_table import Table, Col
import networkx as nx
import os
PROCESSED_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/processed/'
import matplotlib.pyplot as plt
#Infer Data Types for Individual Columns in DataFrame
import app


def infer_df(df, hard_mode=False, float_to_int=False, mf=None):

    # set multiplication factor
    mf = 1 if hard_mode else 0.5

    # set supported datatype
    integers = ['int8', 'int16', 'int32', 'int64']
    floats = ['float16', 'float32', 'float64']

    # ToDo: Unsigned Integer

    # generate borders for each datatype
    b_integers = [(np.iinfo(i).min, np.iinfo(i).max, i) for i in integers]
    b_floats = [(np.finfo(f).min, np.finfo(f).max, f) for f in floats]

    for c in df.columns:
        _type = df[c].dtype
        # if a column is set to float, but could be int
        if float_to_int and np.issubdtype(_type, np.floating):
            if np.sum(np.remainder(df[c], 1)) == 0:
                df[c] = df[c].astype('int64')
                _type = df[c].dtype

        # convert type of column to smallest possible
        if np.issubdtype(_type, np.integer) or np.issubdtype(_type, np.floating):
            borders = b_integers if np.issubdtype(_type, np.integer) else b_floats

            _min = df[c].min()
            _max = df[c].max()

            for b in borders:
                if b[0] * mf < _min and _max < b[1] * mf:
                    _type = b[2]
                    break

        if _type == 'object' and len(df[c].unique()) / len(df) < 0.1:
            _type = 'category'

        df[c] = df[c].astype(_type)

def encode_category(df, column_name):
    encoder = LabelEncoder()
    encoder.fit(df[column_name])
    encoded_X = encoder.transform(df[column_name])
    df[column_name] = np_utils.to_categorical(encoded_X)

def process_csv(file_path, file_name):
    df = pd.read_csv(file_path, header=0)
    print(df.columns, sep='\n\n')
    infer_df(df)

    # Get a Dictionary containing the pairs of column names & data type objects.
    dataTypeDict = dict(df.dtypes)

    print('Data type of each column of Dataframe :')
    print(dataTypeDict)

    for c in df.select_dtypes(include=['category']):
        encode_category(df,c)

    c = df.corr().abs()
    s = c.unstack()
    s = pd.Series(s).where(lambda x: x < 1).dropna()
    so = s.sort_values(ascending=False)

    list_of_processed = []

    print(df.dtypes, sep='\n\n')

    # Feature Importance - Works

    # apply SelectKBest class to extract top 10 best features
    from sklearn.ensemble import ExtraTreesRegressor
    import matplotlib.pyplot as plt
    model = ExtraTreesRegressor()
    Y = df.iloc[:, -1]
    X = df.drop(df.columns[-1],axis=1)
    model.fit(X,Y)
    for i in model.feature_importances_:
        print(float(i))
    feat_importances = pd.Series(model.feature_importances_, index=X.columns)
    top_10_features = feat_importances.nlargest(10)
    list_of_features = []
    for rownum, (indx, val) in enumerate(top_10_features.iteritems()):
        list_of_features.append(indx)
        print('row number: ', rownum, 'index: ', indx, 'value: ', val)
    # Declare your table
    class ItemTable(Table):
        one = Col('Feature 1')
        two = Col('Feature 2')
        cvalue = Col('Correlation Value')
    # Get some objects
    class Item(object):
        def __init__(self, name_one, name_two, correlation_value):
            self.one = name_one
            self.two = name_two
            self.cvalue = round(correlation_value, 4)

    # Build your graph
    G = nx.Graph()
    G.add_nodes_from(list_of_features)

    # Populate the table
    list_of_entries = []
    for items in so.iteritems():
        if (items[0][0] != items[0][1]):
            if (items[0][0] < items[0][1]):
                x = items[0][0]
                y = items[0][1]
            else:
                x = items[0][1]
                y = items[0][0]
            if (x + "-" + y) not in list_of_processed:
                if x in list_of_features and y in list_of_features:
                    G.add_edge(x, y, weight=round(items[1],4))
                    list_of_entries.append(Item(x, y, items[1]))
                    list_of_processed.append(x + "-" + y)
    table = ItemTable(list_of_entries)

    # Plot it
    nx.draw(G, with_labels=True)
    plt.savefig(PROCESSED_FOLDER + str(file_name).replace(".csv","") + ".png", format="PNG")
    # plt.savefig(app.config['PROCESSED_FOLDER'] + file_name + ".png", format="PNG")
    # Print the html
    return [table.__html__(), plt.figimage]
# process_csv('adult.data')
