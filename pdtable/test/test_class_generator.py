import pandas as pd
from pdtable.class_generator import Animals
from pdtable.proxy import Table


def test_class_generator():
    table = Table(
        pd.DataFrame(
            {
                "name": ["Dino", "Rex", "Pysio"],
                "weight": [1, 6, 42],
                "number_of_legs": [2, 2, 1]
            }
        ),
        name="animals",
        units=["text", "kg", "-"],
    )
    animals = Animals(table_data_frame=table.df)
    animals.validate()
