
class ParamPredictor:

    def predict_k(self, df, qi_index):

        eq_count = {}

        # For each record, find all the QI values in the record(as a tuple)
        for record in df.values:
            qi_values = []
            for idx, qi_id in enumerate(qi_index):
                value = record[qi_id]
                qi_values.append(value)
            
            eq = tuple(qi_values)

            # Count the total no.of combination of QI values (EQ Class) found
            if eq not in eq_count.keys():
                eq_count[eq] = 1
            else:
                eq_count[eq] += 1

        pred_k = (max(list(eq_count.values())) + min(list(eq_count.values())) ) / 2
        return pred_k

    def predict_l(self, df, sensitive_column):
        return (len(df[sensitive_column].unique()), 1)

    def predict_t(self, df, sensitive_column):
        # Calculate global frequencies
        global_freqs = {}
        total_count = float(len(df))
        group_counts = df.groupby(sensitive_column)[sensitive_column].agg("count")
        for value, count in group_counts.to_dict().items():
            p = count / total_count
            global_freqs[value] = p
        return max(list(global_freqs.values()))


    def predict(self, df, qi_index, sensitive_column):
        k = self.predict_k(df, qi_index)
        l = self.predict_l(df, sensitive_column)
        t = self.predict_t(df, sensitive_column)
        return {"k": k, "l": l, "t": t}








