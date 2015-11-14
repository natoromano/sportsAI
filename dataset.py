# -*- coding: utf-8 -*-
"""
Classes to handle datasets. Could be merged with the "buildingDataset" files.

@author: Nathanael Romano and Daniel Levy
"""

import pandas as pd
import pickle

class Dataset(object):
    '''Base class for a dataset.'''
    
    def __init__(self, df=None):
        if df is not None:
            self.df = df
        else:
            self.df = pd.DataFrame()
            
    @classmethod
    def fromDataframe(cls, df):
        '''Instantiation from a data frame.'''
        return cls(df)
        
    @classmethod
    def fromCSV(cls, path):
        '''Instantiation from a file path.'''
        return cls(pd.DataFrame.from_csv(path))
        
    @classmethod
    def fromHeader(cls, path):
        '''Instantiation from a header.'''
        f = open(path,'r')
        columns = pickle.load(f)
        f.close()
        return cls(pd.DataFrame(columns=columns))

    def toCSV(self, path):
        '''Dump the data frame to path.'''
        self.df.to_csv(path)

    def saveColumns(self, path):
        '''Dumps the columns to path.'''
        columns = self.df.columns
        f = open(path,'w')
        pickle.dump(columns, f)
        f.close()

    def getX(self, excludedColumns=['label']):
        '''Gets the X matrix.'''
        trainCol = self.df.columns[~self.df.columns.isin(excludedColumns)]
        return self.df[trainCol]

    def getY(self, labelColumn='label'):
        '''Gets the Y matrix.'''
        return self.df[labelColumn]

    def append(self, rows, fill=False):
        '''Appends rows the self.'''
        self.df = self.df.append(rows)
        if fill:
            self.df.fillna(0, inplace=True)

    def __str__(self):
        '''Custom representation method.'''
        return str(self.df)
