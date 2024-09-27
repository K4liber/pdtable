from dataclasses import dataclass

from pdtable.frame import TableDataFrame
from .proxy import Table


class SpecificationException(Exception):
    pass


@dataclass(frozen=True)
class SpecificColumn:
    """
    Immutable, hashable and reusable specification of a column.
    """
    name: str
    unit: str
    description: str = ''


class SpecificDataTable(Table):

    _NAME: str | None = None
    _DESTINATIONS: set[str] = {'all'}
    _COLUMNS: list[SpecificColumn] | None = None

    def __init__(self, table_data_frame: TableDataFrame, validate_all: bool = True) -> None:
        super().__init__(df=table_data_frame)

        if validate_all:
            self.validate()

    @staticmethod
    def _camel_to_snake(s: str) -> str:
        return ''.join(['_' + c.lower() if c.isupper() else c for c in s]).lstrip('_')

    @classmethod
    def _specified_name(cls) -> str:
        return cls._NAME if cls._NAME else cls._camel_to_snake(cls.__name__)

    @classmethod
    def get_description(cls) -> list[str]:
        description_lines = []
        description_lines.append(f'Table "{cls._specified_name()}"\n')
        destinations_str = str(cls._DESTINATIONS).replace("'", '"')
        description_lines.append(f'Destinations: {destinations_str}\n')

        if cls._COLUMNS is not None:
            description_lines.append(f'Columns:\n')

            for column in cls._COLUMNS:
                description_lines.append(
                    f'    {column.name} [{column.unit}] "{column.description}"\n')

        doc = cls.__doc__

        if doc:
            description_lines.append('Description:\n')

            for description_line in cls.__doc__.split('\n'):
                stripped = description_line.strip()

                if stripped != '':
                    description_lines.append(f'    {stripped}\n')

        return description_lines

    def validate(
            self: 'SpecificDataTable',
            validate_name: bool = True,
            validate_columns: bool = True,
            validate_units: bool = True,
            validate_destinations: bool = True
        ) -> None:
        specified_name = self._specified_name()

        if validate_name:
            if specified_name != self.name:
                raise SpecificationException(
                    f'Name mismatch. Expected = "{specified_name}", got = "{self.name}".')

        if validate_columns:
            if self._COLUMNS is None:
                raise SpecificationException(
                    f'Table "{specified_name}" expected to define a class attribute "_COLUMNS".'
                )

            name_to_column = {column.name: column for column in self._COLUMNS}
            specified_column_names = set(name_to_column.keys())

            if specified_column_names != set(self.df.columns):
                raise SpecificationException(
                    f'Table "{specified_name}" expected to have the following columns: {specified_column_names}.')

            if validate_units:
                for index, col_name in enumerate(self.df.columns):
                    unit = self.units[index]
                    specified_unit = name_to_column[col_name].unit

                    if unit != specified_unit:
                        raise SpecificationException(
                            f'Unit mismatch for column "{col_name}". '
                            f'Expected = [{name_to_column[col_name].unit}], got = [{unit}].')

        if validate_destinations:
            if self._DESTINATIONS != self.destinations:
                raise SpecificationException(
                    f'Destinations mismatch. Expected = {self._DESTINATIONS}, got = {self.destinations}.')
