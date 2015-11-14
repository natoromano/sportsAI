import pandas as pd
import pickle
class Dataset():
    def __init__(self):
        self.df = pd.DataFrame()

    def __str__(self):
        return str(self.df)

    def fromDataframe(self, df):
        self.df = df

    def fromCSV(self, path):
        self.df = pd.DataFrame.from_csv(path)

    def toCSV(self, path):
        self.df.to_csv(path)

    def saveColumns(self, path):
        columns = self.df.columns
        f = open(path,'w')
        pickle.dump(columns, f)
        f.close()

    def getX(self, excludedColumns=['label']):
        trainingColumns = self.df.columns[~self.df.columns.isin(excludedColumns)]
        return self.df[trainingColumns]

    def getY(self, labelColumn='label'):
        return self.df[labelColumn]

    def fromHeader(self, path):
        f = open(path,'r')
        columns = pickle.load(f)
        f.close()

        d = Dataset()
        d.fromDataframe(pd.DataFrame(columns=columns))
        return d

    def append(self, rows, fill=False):
        self.df = self.df.append(rows)
        if fill:
            self.df.fillna(0, inplace=True)

