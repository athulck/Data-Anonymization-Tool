
from algorithms.mondrian import Mondrian
import pandas as pd


# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

class Anonymizer:

	def __init__(self, df, attributes):

		# Get the quasi-identifiers and sensitive attributes
		self.feature_columns = list()
		self.sensitive_column = list()

		for attribute in attributes:
			if attributes[attribute]['attributeType'] == "Quasi-identifier":
				self.feature_columns.append(attribute)
			elif attributes[attribute]['attributeType'] == "Sensitive":
				self.sensitive_column.append(attribute)

		self.feature_columns =  self.feature_columns if (len(self.feature_columns) > 0) else None
		self.sensitive_column = self.sensitive_column[0] if (len(self.sensitive_column) > 0) else None


		# Initialize mondrian algorithm
		self.mondrian = Mondrian(df, self.feature_columns, self.sensitive_column)
	

	def agg_categorical_column(self, series):
		# this is workaround for dtype bug of series
		series.astype("category")

		l = [str(n) for n in set(series)]
		return [",".join(l)]


	def agg_numerical_column(self, series):
		minimum = series.min()
		maximum = series.max()
		if maximum == minimum:
			string = str(maximum)
		else:
			string = f"{minimum}-{maximum}"
		return [string]


	def anonymize(self, k, l=0, t=0):

		# Get partitions
		partitions = self.mondrian.partition(k, l, t)


		# Get aggregations
		aggregations = {}
		for column in self.feature_columns:
			if self.mondrian.df[column].dtype.name == "category":
				aggregations[column] = self.agg_categorical_column
			else:
				aggregations[column] = self.agg_numerical_column


		max_partitions = None
		anonymizedDF = pd.DataFrame(columns=self.mondrian.df.columns)



		# Start anonymization process

		# Initial call to print 0% progress
		printProgressBar(0, len(partitions), prefix = 'Progress:', suffix = 'Complete', length = 50)

		for i, partition in enumerate(partitions):

		    printProgressBar (i+1, len(partitions), prefix = 'Progress:', suffix = 'Complete', length = 50)

		    if max_partitions is not None and i > max_partitions:
		        break
		  
		    # print("Original data partition:")
		    # print(mondrian.df.loc[partition])
		    
		    grouped_columns = self.mondrian.df.loc[partition].agg(aggregations, squeeze=False)
		    # print(grouped_columns) # pandas.core.series.Series
		    
		    # Initializing the k-anonymized partition as the raw partition data
		    k_part = self.mondrian.df.loc[partition]

		    # Replacing the discrete values with generalized value for each quasi-identifier columns.
		    for QI_col in self.feature_columns:
		        k_part[QI_col] = grouped_columns[QI_col][0]
		    
		    # print("K-anonymized data partition:")
		    # print(k_part)
		    
		    if self.sensitive_column:
		        sensitive_counts = (
		            self.mondrian.df.loc[partition].groupby(self.sensitive_column).agg({self.sensitive_column: "count"})
		        )
		        # print(sensitive_counts)
		        # print(type(sensitive_counts))



		    anonymizedDF = pd.concat([anonymizedDF, k_part])
		    # anonymizedDF = anonymizedDF.append(k_part, ignore_index = True)
		    # anonymizedDF.loc[len(anonymizedDF.index)] = ['-' for i in self.mondrian.df.columns]

		return anonymizedDF





