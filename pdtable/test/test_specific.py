from pathlib import Path
import pandas as pd
from pytest import fixture
from pdtable.specific import SpecificDataTable, SpecificColumn
from pdtable.proxy import Table

ANIMAL_NAME = SpecificColumn(
    name='name',
    unit='text',
    description='Name of the animal'
)
ANIMAL_WEIGHT = SpecificColumn(
    name='weight',
    unit='kg',
    description='Weight of the animal (as it has on the birth day)'
)
ANIMAL_NUMBER_OF_LEGS = SpecificColumn(
    name='number_of_legs',
    unit='-',
    description='Number of legs of the animal'
)

class Animals(SpecificDataTable):
    """
    Table store the data about all animals in the world.
    The purpose is to select the best animals for Noah's ark.
    """

    _COLUMNS = [
        ANIMAL_NAME,
        ANIMAL_WEIGHT,
        ANIMAL_NUMBER_OF_LEGS
    ]


@fixture
def test_resources() -> Path:
    return Path(__file__).parent / "test_resources"


def test_animals_data_table(test_resources: Path):
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
    actual_description_lines = animals.get_description()

    with open(test_resources / 'animals.txt', 'r') as file:
        expected_description_lines = file.readlines()
        assert expected_description_lines == actual_description_lines
