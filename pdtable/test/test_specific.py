from pathlib import Path
import pandas as pd
from pytest import fixture
import pytest
from pdtable.frame import ImmutabilityError
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


@fixture
def animals_data_table() -> Animals:
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
        immutable=True
    )
    return Animals(table_data_frame=table.df)


def test_animals_data_table(
        test_resources: Path,
        animals_data_table: Animals
    ) -> None:

    actual_description_lines = animals_data_table.get_description()

    with open(test_resources / 'animals.txt', 'r') as file:
        expected_description_lines = file.readlines()
        assert expected_description_lines == actual_description_lines


def test_immutable(animals_data_table: Animals) -> None:
    # The following mutation methods are not allowed for the immutable table
    with pytest.raises(ImmutabilityError):
        animals_data_table.df.at[0, ANIMAL_NAME.name] = 'Onid'
    
    with pytest.raises(ImmutabilityError):
        animals_data_table.df.replace("Dino", "Odin", inplace=True)

    # The following methods (read-only or not in-place) 
    # are allowed for the immutable table
    animals_data_table.df.reindex(animals_data_table.df.index)
    pd.concat([animals_data_table.df, animals_data_table.df])
    animals_data_table.df.merge(pd.DataFrame(columns=animals_data_table.df.columns))
    animals_data_table.df[ANIMAL_WEIGHT.name]
    animals_data_table.df.iloc[0]
    [row for _, row in animals_data_table.df.iterrows()]
    animals_data_table.df.take([0, 1])
    animals_data_table.df[[ANIMAL_WEIGHT.name, ANIMAL_NAME.name]]
    animals_data_table.df.copy()
    animals_data_table.df.copy(deep=False)
    animals_data_table.df.groupby([ANIMAL_NAME.name]).mean()
    animals_data_table.df.data_not_changed()
