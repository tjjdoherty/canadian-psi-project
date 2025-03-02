import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
# from .constants import PROVINCES, TERRITORIES # relative import - from the same directory, import provinces and territories

# Custom transformer (CT) for dropping unnecessary columns from the dataframe
class DropColumns(BaseEstimator, TransformerMixin):
    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None): # this transformer isn't learning the data, so we just return self
        return self

    def transform(self, X):
        return X.drop(columns=self.columns, errors='ignore') # no inplace=True - not modifying the original dataframe; errors='ignore' to ignore named columns that don't exist in the dataframe
    
# CT for renaming columns
class RenameColumns(BaseEstimator, TransformerMixin):
    def __init__(self, column_names):
        self.column_names = column_names

    def fit(self, X, y=None): # as above, this transformer isn't learning the data, just return self
        return self

    def transform(self, X):
        return X.rename(columns=self.column_names)

# CT to Reformat the 'REF_DATE' (now FY Start) column to only include the year (from 2009-2010 to 2009)
class FormatDate(BaseEstimator, TransformerMixin):
    def __init__(self, column):
        self.column = column

    def fit(self, X, y=None): # as above
        return self

    def transform(self, X):
        X[self.column] = X[self.column].apply(lambda x: int(x[:4]))
        return X
    
# CT to extract institution name and province from 'GEO' (now Province/Territory) column
class AddInstitutionAndProvince(BaseEstimator, TransformerMixin):
    def __init__(self, column, institution_col, province_col, provinces):
        self.column = column
        self.institution_col = institution_col
        self.province_col = province_col
        self.provinces = set(provinces)

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()  # Avoid in-place modification
        # Extract institution name
        X[self.institution_col] = X[self.column].apply(
            lambda x: f"{x} (total)" if x in self.provinces else x.rsplit(',', 1)[0]
        )
        # Extract province
        X[self.province_col] = X[self.column].apply(
            lambda x: x if x in self.provinces else x.rsplit(',', 1)[-1].strip()
        )
        return X
    
# CT to abbreviate institution names
class AbbreviateInstitutionNames(BaseEstimator, TransformerMixin):
    def __init__(self, column, replacements):
        """
        :param column: The column to clean up.
        :param replacements: A dictionary of strings to replace (key: target, value: replacement).
        """
        self.column = column
        self.replacements = replacements

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()  # Avoid in-place modifications
        for target, replacement in self.replacements.items():
            X[self.column] = X[self.column].str.replace(target, replacement, regex=False)
        return X
    
class RemoveTerritories(BaseEstimator, TransformerMixin):
    def __init__(self, column, territories):
        """
        :param column: The column where we look for territory names
        :param territories: A list of territory names (e.g. ["Yukon", "Northwest Territories", "Nunavut"])
        """
        self.column = column
        self.territories = territories # territories imported from constants.py

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """
        Removes rows where the specified column contains any of the territory names.
        """
        X = X.copy()
        # Build a regex pattern that matches any of the territory strings
        pattern = '|'.join(self.territories)

        # Keep rows that do NOT contain any of the territory names (case-insensitive).
        # If the column is sometimes NaN, na=False ensures we don't error out.
        return X[~X[self.column].str.contains(pattern, case=False, na=False)]

# reorder the columns for ease of reading

class ReorderColumns(BaseEstimator, TransformerMixin):
    def __init__(self, desired_order):
        """
        parameter - desired_order: A list specifying the columns in the order desired.
        e.g. ["FY Start", "Province/Territory", "Institution Name", ...]
        """
        self.desired_order = desired_order

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """
        Reorders the columns to the specified order. Any columns not in 'desired_order'
        are appended at the end in their existing order.
        """
        X = X.copy()
        
        # Columns that are explicitly ordered
        ordered_cols = [c for c in self.desired_order if c in X.columns]
        
        # Any remaining columns not in 'desired_order'
        leftover_cols = [c for c in X.columns if c not in ordered_cols]
        
        # Final order is the desired columns first, then leftover
        final_order = ordered_cols + leftover_cols
        
        return X[final_order]

# pivot Canadian status (domestic/international/unreported) into three columns of the same record, all else being equal

class PivotCanadianStatus(BaseEstimator, TransformerMixin):
    def __init__(
        self, 
        index_cols=[
            "FY Start", 
            "Province/Territory", 
            "Institution Name", 
            "Program type", 
            "Credential type", 
            "Field of study"
            ],
        pivot_col="Canadian Status",
        values_col="Enrolment"
    ):
        """
        Parameter - index_cols: The columns to keep for each row/record (index in the pivot).
        Parameter - pivot_col: The column whose unique values become new columns (e.g. 'Canadian Status').
        Parameter - values_col: The numeric column to place in new columns (e.g. 'Enrolment').
        """
        self.index_cols = index_cols
        self.pivot_col = pivot_col
        self.values_col = values_col

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """
        Pivots the dataframe so that 'Canadian Status' becomes columns:
          -> 'Domestic Enrolment'; 'International Enrolment'; 'CA Status Unreported Enrolment'
        If 'Field of study' or 'Unreported status' is missing, they are skipped
        After pivoting, renames columns accordingly and returns the wide table.
        """
        X = X.copy()

        # 1. Build a local list of index columns
        live_index_cols = [col for col in self.index_cols if col in X]

        # 2. Pivot only on the columns that exist
        pivoted = X.pivot_table(
            index=live_index_cols,
            columns=self.pivot_col,
            values=self.values_col,
            aggfunc='sum'  # If duplicates exist, sum them
        ).reset_index()

        # 3. Rename columns from 'Canadian students' -> 'Domestic Enrolment' etc.
        col_rename_map = {
            'Canadian students': 'Domestic Enrolment',
            'International students': 'International Enrolment',
            'Not reported, status of student in Canada': 'CA Status Unreported Enrolment'
        }
        
        # 4. rename and convert columns to integers
        for old_col, new_col in col_rename_map.items():
            if old_col in pivoted.columns: # this if statement will stop a KeyError from being raised if Unreported status is missing from a dataframe e.g. in domestic_intl.ipynb
                # rename the column
                pivoted.rename(columns={old_col: new_col}, inplace=True) # if the column was there (e.g. Canadian Students), it's renamed according to the rename map in 3.
                # fillna & convert to int
                pivoted[new_col] = pivoted[new_col].fillna(0).astype(int)
            # below else statement is if we wanted a dummy column full of zeroes if a column (e.g. Unreported status enrolment) was missing
            # else:
            #     # If it's missing, create it with zeros
            #     if new_col not in pivoted.columns:
            #         pivoted[new_col] = 0
        
        # # 4. convert new Domestic and International Enrolment columns to integers
        # pivoted['Domestic Enrolment'] = pivoted['Domestic Enrolment'].fillna(0).astype(int)
        # pivoted['International Enrolment'] = pivoted['International Enrolment'].fillna(0).astype(int)
        # pivoted['CA Status Unreported Enrolment'] = pivoted['CA Status Unreported Enrolment'].fillna(0).astype(int)

        # 4. Reorder columns (domestic, international, unreported) at the end, if they exist
        final_cols = [c for c in pivoted.columns if c not in col_rename_map.values()]
        final_cols += ['Domestic Enrolment', 'International Enrolment', 'CA Status Unreported Enrolment']
        # keep only what actually exists
        final_cols = [c for c in final_cols if c in pivoted.columns]

        return pivoted[final_cols]