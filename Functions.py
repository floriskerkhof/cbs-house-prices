import pandas as pd
import requests
import cbsodata 
import numpy as np
import matplotlib as mpl
import datetime

import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

#  verwerk dit in een functie
# data_vacatures = pd.DataFrame(cbsodata.get_data('80474ned'))
# dict_kwartaal={' 1e kwartaal':'KW01',' 2e kwartaal':'KW02',' 3e kwartaal':'KW03'," 4e kwartaal":'KW04'}
# # Zorg dat deze in andere functie opgeneomen wordt

# for pat, repl in dict_kwartaal.items():
#     data_vacatures['Perioden'] = data_vacatures['Perioden'].str.replace(pat, repl)
# data_vacatures = cbs_add_date_column(data_vacatures)


def loadin_cbsdata(apicode):
    data = pd.DataFrame(cbsodata.get_data(apicode))
    dict_kwartaal={' 1e kwartaal':'KW01',' 2e kwartaal':'KW02',' 3e kwartaal':'KW03'," 4e kwartaal":'KW04'}
    # Zorg dat deze in andere functie opgeneomen wordt
#      potentieel nog een if of er kwartaal inzit

    for pat, repl in dict_kwartaal.items():
        data['Perioden'] = data['Perioden'].str.replace(pat, repl)
    if 4!= data['Perioden'].apply(len).mean():
        data = cbs_add_date_column(data)
    return data
def setup_load_db(df,name):

    conn = sqlite3.connect('TestDB.db')
    c = conn.cursor()
    df.to_sql(name, conn, if_exists='append', index = False)

def make_graph(df,x,d,v,name):
    """This function creates separate lines in a graph for every category
    the input are: |
    df:the input dataframe |
    x: The column with the different categories |
    d: the date value |
    v: the value to be reported, |
    name=the title of the graph |

    """
    years = df[x].unique()

    # Prep Colors
    np.random.seed(100)
    mycolors = np.random.choice(list(mpl.colors.XKCD_COLORS.keys()), len(years), replace=False)

    # Draw Plot
    plt.figure(figsize=(10,12), dpi= 80)
    for i, y in enumerate(years):
        if i > 0:        
            plt.plot(d, v, data=df.loc[df[x]==y, :], color=mycolors[i], label=y)
    #         plt.text(df.loc[df.Title==y, :].shape[0]-.9, df.loc[df.Title==y, 'value'][-1:].values[0], y, fontsize=12, color=mycolors[i])



    # Decoration
    # plt.gca().set(xlim=(-0.3, 11), ylim=(2, 30), ylabel='$Vacatures$', xlabel='$Month$')
    plt.yticks(fontsize=12, alpha=.7)
    plt.title(name, fontsize=20)
    from matplotlib.font_manager import FontProperties
    fontP = FontProperties()
    fontP.set_size('small')

    plt.legend(loc="upper left", prop=fontP,bbox_to_anchor=(-.2, 1.008))
    plt.show()
    
    
def cbs_add_date_column(data, period_name = "Perioden",col=0):
    if not period_name in list(data):
        print("No time dimension found called " + period_name)
        return data
    


#  check if there is no kwartaal column, otherwise use groupby on that first
    if not data[period_name].str.contains('kwartaal').any():

        dict_maanden={' januari':'KW01',' februari':'KW01',' maart':'KW01',' april':'KW02',' mei':'KW02',' juni':'KW02',' juli':'KW03',' augustus':'KW03',' september':'KW03',' oktober':'KW04',' november':'KW04',' december':'KW04'}
        #       replace the months with values from dict
        #         data = data.replace({period_name: dict_maanden})
        for pat, repl in dict_maanden.items():
            data['Perioden'] = data['Perioden'].str.replace(pat, repl)
        #       Find all numeric columns and make a dict
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        List_numeric=list(data.iloc[:,1:].select_dtypes(include=numerics).columns)
        # List_numeric.append('Perioden')

        d = {}
        for i in List_numeric:
          d[i]='sum'
        d

        # list of all objects
        List_object=list(data.iloc[:,:].select_dtypes(include=object).columns)


        #       Groupby all numeric columns and merge it back in one dataframe
        data = data.groupby(List_object, as_index=False).agg(d)
        
    dict_kwartaal={' 1e kwartaal':'KW01',' 2e kwartaal':'KW02',' 3e kwartaal':'KW03'," 4e kwartaal":'KW04'}
    for pat, repl in dict_kwartaal.items():
        data[period_name] = data[period_name].str.replace(pat, repl)
#   Find 1992KW01 and make separate columns
    regex = r'(\d{4})([A-Z]{2})(\d{2})'
    data[['year','frequency','count']] = data[period_name].str.extract(regex)

    freq_dict = {'JJ': 'Y', 'KW': 'Q', 'MM': 'M'}
    
    data = data.replace({'frequency': freq_dict})
    
     # Converteert van het CBS-formaat voor perioden naar een datetime.
    def convert_cbs_period(row):
        if(row['frequency'] == 'Y'):
            return datetime.datetime(int(row['year']),1,1)
        elif(row['frequency'] == 'M'):
            return datetime.datetime(int(row['year']),int(row['count']),1)
        elif(row['frequency'] == 'Q'):
            return datetime.datetime(int(row['year']),int(row['count'])*3-2,1)
        else:
            return None
        
    data['date'] = data.apply(convert_cbs_period, axis = 1)
    return data

def three_y_graph(df,x_axis,y1,y2,y3,label_x,label1,label2,label3):
    """This function creates a graph with 3 y axis
    the input are: |
    df:the input dataframe |
    x_axis: usually date|
    y1= first y-axis
    y2=second y-axis
    y3= third y-axis
    label_x=label x axis
    label1-3= label other y axis

    """
    import matplotlib.pyplot as plt 

    fig = plt.figure()
    host = fig.add_subplot(111)

    par1 = host.twinx()
    par2 = host.twinx()

    # host.set_xlim(0, 2)
    # host.set_ylim(0, 2)
    # par1.set_ylim(0, 4)
    # par2.set_ylim(1, 65)


    host.set_xlabel(label_x)
    host.set_ylabel(label1)
    par1.set_ylabel(label2)
    par2.set_ylabel(label3)


    p1, = host.plot(df[x_axis], df[y1], '-y', label = label1)
    p2, = par1.plot(df[x_axis], df[y2], '-', label = label2)

    p3, = par2.plot(df[x_axis], df[y3], '-r', label = label3)


    lns = [p1, p2, p3]
    host.legend(handles=lns, loc='best')

    par2.spines['right'].set_position(('outward', 60))              
    # par2.xaxis.set_ticks([])
    return 
def plot_df(df, x, y, title="", xlabel='Date', ylabel='Value',rotation='no', dpi=100):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(16,5), dpi=dpi)
    plt.plot(x, y, color='tab:red')
    plt.gca().set(title=title, xlabel=xlabel, ylabel=ylabel)
#     plt.xlabel("x1000")
    if rotation=='yes':
        plt.xticks(rotation=90)
    plt.show()
    
    
def filter_df(df, filter_values):

    """Filter df by matching targets for multiple columns.

 

    Args:

        df (pd.DataFrame): dataframe

        filter_values (None or dict): Dictionary of the form:

                `{<field>: <target_values_list>}`

            used to filter columns data.

    """

    import numpy as np

    if filter_values is None or not filter_values:

        return df

    return df[

        np.logical_and.reduce([

            df[column].isin(target_values) 

            for column, target_values in filter_values.items()

        ])

    ]