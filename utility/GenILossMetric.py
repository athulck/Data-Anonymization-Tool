class GenILoss:

    def __init__(self, OrigDF, feature_columns):
        self.OrigDF = OrigDF
        self.feature_columns = feature_columns
        self.qi_index = list()
        self.UniqueVals = dict()

        # Create QI_Index
        for i in self.OrigDF.columns:
            if i in self.feature_columns:
                self.qi_index.append(list(self.OrigDF.columns).index(i))

        # Create UniqueVals
        for column in feature_columns:
            if self.OrigDF[column].dtype.name == "category":
                # If it is a categorical attribute, then max generalizaion will be 1, and min generalization wll be the number of unique values.
                self.UniqueVals[column] = len(self.OrigDF[column].unique()) - 1
            else:
                # If it is a continuous attribute, then upper bound - lower bound will be the max range.
                self.UniqueVals[column] = self.OrigDF[column].max() - self.OrigDF[column].min()

    def calculate(self, df):
        genILoss, sum = 0, 0
        for record in df.values:      #[15060 times]
            for qi in self.qi_index:    #[4 times]
                temp_sum = sum
                if self.OrigDF[self.OrigDF.columns[qi]].dtype.name == "category":
                    sum += (len(str(record[qi]).split(',')) - 1) / self.UniqueVals[self.OrigDF.columns[qi]]
                else:
                    if '-' in list(str(record[qi])):
                        hi = int(str(record[qi]).split('-')[1]) 
                        lo = int(str(record[qi]).split('-')[0])
                        sum += ((hi - lo) / self.UniqueVals[self.OrigDF.columns[qi]])

            if sum - temp_sum > 0.5:
                print(self.OrigDF.columns[qi], ":", record[qi])

        genILoss =   (1 / (len(df) * len(self.feature_columns))) * sum
        # print("Max sum:", (len(df) * len(self.feature_columns)))
        # print("Current sum:", sum)
        return genILoss