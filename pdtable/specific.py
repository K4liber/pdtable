from abc import ABC, abstractstaticmethod
from dataclasses import dataclass
from .proxy import Table


class ValidationException(Exception):
    pass


@dataclass(frozen=True)
class ColumnDetails:
    unit: str
    description: str = ''


class SpecificDataTable(ABC, Table):

    _NAME = ''
    _DESTINATIONS = {'all'}

    @abstractstaticmethod
    def column_name_to_details() -> dict[str, ColumnDetails]:
        ...
    
    @classmethod
    def get_description(cls) -> list[str]:
        description_lines = []
        description_lines.append(f'Table "{cls._NAME}"\n')
        description_lines.append(f'Columns:\n')

        for column_name, column_details in cls.column_name_to_details().items():
            description_lines.append(f'    {column_name} [{column_details.unit}] "{column_details.description}"\n')

        description_lines.append('Description:\n')

        for description_line in cls.__doc__.split('\n'):
            stripped = description_line.strip()

            if stripped != '':
                description_lines.append(f'    {stripped}\n')

        return description_lines

    def validate(self: 'SpecificDataTable') -> None:
        assert self._NAME == self.name
        column_names = set(self.column_name_to_details().keys())

        if column_names != set(self.df.columns):
            raise ValidationException(f'Table "{self._NAME}" should have the following columns: {column_names}.')

        for index, col_name in enumerate(self.df.columns):
            unit = self.units[index]
            assert unit == self.column_name_to_details()[col_name].unit

        assert self._DESTINATIONS == self.destinations
