

# Mondrian Class
class Mondrian:
    def __init__(self, df, feature_columns, sensitive_column=None):
        self.df = df
        self.feature_columns = feature_columns
        self.sensitive_column = sensitive_column

    # Helper Functions
    def is_valid(self, partition, k=2, l=0, p=0.0):
       
        # k-anonymous
        # len(eq_class) must be >= k 
        if len(partition) < k:
            return False
        
        # l-diverse
        if 0 < l and self.sensitive_column is not None:
            # For each sensitive columns, we make sure that each partition will have >= l unique values.
            unique_values = len(self.df.loc[partition][self.sensitive_column].unique())
            # No.of unique values of sensitive attribute in partition must be >= l
            if unique_values < l:
                return False
        
        # t-close
        if p > 0.0 and self.sensitive_column is not None:
            # Calculate global frequencies
            global_freqs = {}
            total_count = float(len(self.df))
            group_counts = self.df.groupby(self.sensitive_column)[self.sensitive_column].agg("count")
            for value, count in group_counts.to_dict().items():
                p = count / total_count
                global_freqs[value] = p

            # Check if this equivalent class is t-close
            d_max = None #stores the maximum diversity
            total_count = float(len(partition))
            group_counts = self.df.loc[partition].groupby(self.sensitive_column)[self.sensitive_column].agg("count")
            
            for value, count in group_counts.to_dict().items():
                p = count / total_count
                d = abs(p - global_freqs[value])
                if d_max is None or d > d_max:
                    d_max = d
            
            # Maximum diversity value must be equal to or smaller than p
            if d_max > p:
                return False

        return True

    def get_spans(self, partition, scale=None):
        spans = {}
        for column in self.feature_columns:
            if self.df[column].dtype.name == "category":
                span = len(self.df[column][partition].unique())
            else:
                span = (
                    self.df[column][partition].max() - self.df[column][partition].min()
                )
            if scale is not None:
                span = span / scale[column]
            spans[column] = span
        return spans

    def split(self, column, partition):
        dfp = self.df[column][partition]
        if dfp.dtype.name == "category":
            values = dfp.unique()
            lv = set(values[: len(values) // 2])
            rv = set(values[len(values) // 2 :])
            return dfp.index[dfp.isin(lv)], dfp.index[dfp.isin(rv)]
        else:
            median = dfp.median()
            dfl = dfp.index[dfp < median]
            dfr = dfp.index[dfp >= median]
            return (dfl, dfr)

    def partition(self, k=3, l=0, p=0.0):
        scale = self.get_spans(self.df.index)

        print("Partitioning dataset using Mondrian ... ")
        finished_partitions = []
        partitions = [self.df.index]
        while partitions:
            partition = partitions.pop(0)
            spans = self.get_spans(partition, scale)
            for column, span in sorted(spans.items(), key=lambda x: -x[1]):
                lp, rp = self.split(column, partition)
                if not self.is_valid(lp, k, l, p) or not self.is_valid(rp, k, l, p):
                    continue
                partitions.extend((lp, rp))
                break
            else:
                finished_partitions.append(partition)
        
        print("Done!")
        return finished_partitions
