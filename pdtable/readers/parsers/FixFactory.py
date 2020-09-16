from typing import List, Any

import numpy as np
import pandas as pd


class FixFactory:
    """ base class for auto-correcting startable.csv input files

        * Possible specialization:

        class fixErrors(FixFactory):
            # augment existing method
            def fix_illegal_cell_value(self, vtype, value):
                db_store(self.TableName,(self.TableColumn,self.TableRow))
                dfval = FixFactory.fix_illegal_cell_value(self, vtype, value)
                return dfval

    """

    # Store legend of what's fixed + API
    def __init__(self):
        self._dbg = False
        self._errors = 0
        self._warnings = 0

        # Context info
        self.origin = None
        self.table_name = None
        self.column_name = None
        self.table_row = None

    @property
    def verbose(self):
        """
        if verbose: print debug info in fix_* methods
        """
        return self._dbg

    @verbose.setter
    def verbose(self, value: bool):
        self._dbg = value

    @property
    def warnings(self):
        """
        Number of simple fixes
        """
        return self._warnings

    @property
    def errors(self):
        """
        Number of error fixes:
            fix_missing_column_name, fix_missing_rows_in_column_data
        """
        return self._errors

    def fix_duplicate_column_name(self, column_name: str, input_columns: List[str]) -> str:
        """
            The column_name already exists in  input_columns
            This method should provide a unique replacement name

        """
        if self.verbose:
            print(
                f"FixFactory: fix duplicate column ({self.column_name}) {column_name} in table: {self.table_name}"
            )

        self._errors += 1
        for sq in range(1000):
            test = f"{column_name}_fixed_{sq:03}"
            if test not in input_columns:
                return test

        return "{column_name}-fixed"

    def fix_missing_column_name(self, input_columns: List[str]) -> str:
        """
            The column_name: self.TableColumn is empty
            This method should provide a unique replacement name
        """
        if self.verbose:
            print(
                f"FixFactory: fix missing column ({self.column_name}) {input_columns} in table: {self.table_name}"
            )
        return self.fix_duplicate_column_name("missing", input_columns)

    def fix_missing_rows_in_column_data(
        self, row: int, row_data: List[str], num_columns: int
    ) -> List[str]:
        """
            The row is expected to have num_columns values
            This method should return the entire row of length num_columns
            by providing the missing default values
        """
        if self.verbose:
            print(f"FixFactory: fix missing data in row ({row}) in table: {self.table_name}")
        row_data.extend(["NaN" for cc in range(num_columns - len(row_data))])
        self._errors += 1
        return row_data

    def fix_illegal_cell_value(self, vtype: str, value: str) -> Any:
        """
            The string value can not be converted to type vtype
            This method should return a suitable default value of type vtype

            Supported vtypes in { "onoff", "datetime", "-", "float" }
        """
        defaults = {"onoff": False, "datetime": pd.NaT, "float": np.NaN, "-": np.NaN}
        if self.verbose:
            print(f'FixFactory: illegal {vtype} value "{value}" in table {self.table_name}')
        default_val = defaults.get(vtype)
        self._warnings += 1
        if default_val is not None:
            return default_val
        else:
            return defaults["-"]
