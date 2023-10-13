"""
The purpose of Class Generator is to create a class based on the loaded startable.
The class need to implement validation of columns (existence) and values (types/units).
[To consider] The class can have methods to easily access columns.
The class should have a method for generating the table description (maybe just a copy of the class description?).
The idea is to have a workspace (bundle of csv/excel files with startables) and generate the classes + description.

The purposes of such class is to:
1) validate the input
2) access for each column (using class methods)
3) keeping the history of changes for startables bundle in version control system
"""


from .frame import TableDataFrame
from .proxy import Table


class Animals(Table):
    """
    Generated at 13.10.2023 21:37 CEST

    Description:
      Table store the data about all animals in the world.
      The purpose is to select the best animals for Noah's ark.
    
    Destinations:
      - all

    Columns:
      - name [text]
        Name of the animal.
      - weight [kg]
        Weight of the animal (as it has on the birth day).
      - number_of_legs [-]
        
    """
    def __init__(self, table_data_frame: TableDataFrame) -> None:
        super().__init__(df=table_data_frame)
    
    def validate(self):
        pass  # TODO

    def description(self) -> str:
        pass  # TODO
