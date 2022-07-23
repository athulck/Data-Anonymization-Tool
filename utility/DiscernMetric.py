

class DM:
    """
    Discernibility Metric implementation based on definition from
    http://www.tdp.cat/issues11/tdp.a169a14.pdf    
    """
    def __init__(self, anon_data, qi_index, k) -> None:
        self.anon_data = anon_data
        self.num_records = len(anon_data)
        self.qi_index = qi_index
        self.k = k
        self.num_qi = len(self.qi_index)

    def compute_eq(self):
        self.eq_count = {}
        for record in self.anon_data.values:
            qi_values = []
            for idx, qi_id in enumerate(self.qi_index):
                value = record[qi_id]
                qi_values.append(value)
            
            # Make set, because set is hashable
            eq = tuple(qi_values)

            # Count set of qi values
            if eq not in self.eq_count.keys():
                self.eq_count[eq] = 1
            else:
                self.eq_count[eq] += 1

    """
    The simplest kind of quality measure is based on the size of the equivalence classes.
    The discernibility metric assigns to each tuple t a penalty, which is determined by the size of the 
    equivalence class containing t.
    """
    def compute_score(self):
        self.compute_eq()
        dm = 0
        for eq in self.eq_count.keys():
            eq_count = self.eq_count[eq]
            if eq_count >= self.k:
                dm += (eq_count * eq_count)
            else:
                dm += (eq_count * self.num_records)

        return dm