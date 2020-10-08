import sys
import os
import json
import pytest
from pathlib import Path
import pandas as pd

from pdtable import ParseFixer, BlockType
from pdtable import read_csv
from pdtable.io.parsers import parse_blocks
from pdtable.io.parsers.blocks import make_table
from pdtable.io import table_to_json_data


_test_fixer = ParseFixer()
_test_fixer.stop_on_errors = False
_test_fixer._called_from_test = True


def input_dir() -> Path:
    return Path(__file__).parent / "input/with_errors"


def test_columns_duplicate():
    """
       Verify that default ParseFixer corrects duplicate column names

    """
    tab = None
    with open(input_dir() / "cols1.csv", "r") as fh:
        g = read_csv(fh, fixer=_test_fixer)
        for tp, tt in g:
            if True:
                if tp == BlockType.TABLE:
                    tab = tt
                    break
    assert tab is not None
    assert tab.df["flt_fixed_001"] is not None
    assert tab.df["flt_fixed_001"][6] == 7.6
    assert tab.df["flt"][0] == 3.0


def test_columns_missing():
    """
       Verify that default ParseFixer corrects missing column name

    """
    tab = None
    with open(input_dir() / "cols2.csv", "r") as fh:
        g = read_csv(fh, fixer=_test_fixer)
        for tp, tt in g:
            if True:
                if tp == BlockType.TABLE:
                    tab = tt
                    break
    assert tab is not None
    assert tab.df["missing_fixed_000"] is not None
    assert tab.df["flt"][6] == 7.11


def test_custom_fixer():
    """ Test custom ParseFixer
        Verify that read_csv uses custom ParseFixer
    """

    class fix_pi(ParseFixer):
        def __init__(self):
            super().__init__()

        # augment existing method, simple fix float
        def fix_illegal_cell_value(self, vtype, value):
            if vtype == "float":
                return 22.0 / 7.0
            else:
                fix_value = ParseFixer.fix_illegal_cell_value(self, vtype, value)
                return fix_value

    fix = fix_pi()
    fix.stop_on_errors = False
    fix._called_from_test = True

    with open(input_dir() / "types3.csv", "r") as fh:
        g = read_csv(fh, to="jsondata", fixer=fix)
        for tp, tt in g:
            if tp == BlockType.TABLE:
                assert tt["columns"]["num"]["values"][2] == 22.0 / 7.0
                assert tt["columns"]["flt"]["values"][0] == 22.0 / 7.0
                assert tt["columns"]["flt"]["values"][0] == 22.0 / 7.0
                assert tt["columns"]["flt2"]["values"][2] == 22.0 / 7.0

    with pytest.raises(ValueError):
        # test read_csv w. class (not instance) of fixer
        # class has default stop_on_errors = True
        with open(input_dir() / "types3.csv", "r") as fh:
            g = read_csv(fh, to="jsondata", fixer=fix_pi)
            for tp, tt in g:
                pass


def test_FAT():
    """ Factory Acceptance Test

        Verify that we are able to read all files in ./input
        Using default ParseFixer
    """
    all_files = 0
    ignore_files = ["auto_fixed.py", "__init__.py", "all.json"]
    for fn in os.listdir(input_dir()):
        path = input_dir() / fn
        if not os.path.isfile(path):
            continue
        if fn in ignore_files:
            continue
        all_files += 1

    # load targets
    with open(input_dir() / "all.json") as f:
        all_json = json.load(f)

    for fn in os.listdir(input_dir()):
        path = input_dir() / fn
        if not os.path.isfile(path):
            continue
        if fn in ignore_files:
            continue

        with open(input_dir() / fn, "r") as fh:
            g = read_csv(fh, origin=f'"{fn}"', to="jsondata", fixer=_test_fixer)
            count = 0
            for tp, tt in g:
                if tp == BlockType.TABLE:
                    count += 1
                    if fn != "all.csv":
                        assert tt == all_json[fn]

            if fn == "all.csv":
                assert count == all_files - 1
            else:
                assert count == 1


def test_stop_on_errors():
    """ Unit test cusrom ParseFixer.stop_on_errors
    """
    # fmt: off
    table_lines = [
        ["**tab_ok"],
        ["dst1"],
        [ "a1"  , "a2"  , "a3"  , "a4"  ],
        [ "-"   , "-"   , "-"   , "-"   ],
        [ 1     , 2     , 3     , 3.14  ],
        [],
        ["**tab_errors"],
        ["dst1"],
        [ "a1"  , "a2"  , "a3"  , "a4"  ],
        [ "-"   , "-"   , "-"   , "-"   ],
        [ "NaN" , "nan" , "Nine", "Ten" ],
        [ 1     , 2     , 3     , 4     ],
    ]
    # fmt: on

    fix = ParseFixer()
    fix.stop_on_errors = True
    fix._dbg = False  #  ignore during test
    pi = 0
    with pytest.raises(ValueError):
        for typ, tab in parse_blocks(table_lines, fixer=fix, to="pdtable"):
            if typ != BlockType.TABLE:
                continue
            assert tab.df["a4"][0] == 3.14
            pi += 1

    with pytest.raises(ValueError):
        for typ, tab in parse_blocks(table_lines, fixer=fix, to="jsondata"):
            if typ != BlockType.TABLE:
                continue
            assert tab["columns"]["a4"]["values"][0] == 3.14
            pi += 1

    # cellgrid does not parse values, i.e. no ValueError
    for typ, tab in parse_blocks(table_lines, fixer=fix, to="cellgrid"):
        if typ != BlockType.TABLE:
            continue
        if tab[0][0] == "**tab_ok":
            assert tab[4][3] == 3.14
            pi += 1
        if tab[0][0] == "**tab_errors":
            assert tab[4][3] == "Ten"

    assert pi == 3  # 😉


def test_stop_on_errors_default_fixer():
    """ Unit test ParseFixer: raise ValueError on empty float and empty onoff
    """
    # fmt: off
    table_lines_flt = [
        ["**tab_ok"],
        ["dst1"],
        [ "a1"  , "a2"  , "a3"  , "a4"  ],
        [ "-"   , "-"   , "-"   , "-"   ],
        [ 1     , 2     , 3     , 3.14  ],
        [],
        ["**tab_errors"],
        ["dst1"],
        [ "a1"  , "a2"  , "a3"  , "a4"  ],
        [ "-"   , "-"   , "-"   , "-"   ],
        [ 1     , 2     , 3     , ""    ],
    ]
    # fmt: on

    g = parse_blocks(table_lines_flt, filter=lambda ty, tn: ty == BlockType.TABLE)
    typ, tab = next(g)
    assert tab.name == "tab_ok"
    assert tab.df["a4"][0] == 3.14

    with pytest.raises(ValueError):
        typ, tab = next(g)
        print(f"-oOo-: {typ} {tab}")

    # fmt: off
    table_lines_onoff = [
        ["**tab_ok"],
        ["dst1"],
        [ "a1"  , "a2"],
        [ "-"   , "onoff"],
        [ 3.14  , 1      ],
        [],
        ["**tab_errors"],
        ["dst1"],
        [ "a1"  , "a2" ],
        [ "-"   , "onoff" ],
        [ 1     ,  None   ],
    ]
    # fmt: on
    g = parse_blocks(table_lines_onoff, filter=lambda ty, tn: ty == BlockType.TABLE)
    typ, tab = next(g)
    assert tab.name == "tab_ok"
    assert tab.df["a1"][0] == 3.14

    with pytest.raises(ValueError):
        typ, tab = next(g)
        print(f"-oOo-: {typ} {tab}")

    # fmt: off
    table_lines_datetime = [
        ["**tab_ok"],
        ["dst1"],
        [ "a1"  , "a2"],
        [ "-"   , "datetime"   ],
        [ 14    , pd.to_datetime("2020-08-11")],
        [ 3.14  , "2020-08-12" ],
        [],
        ["**tab_errors"],
        ["dst1"],
        [ "a1"  , "a2" ],
        [ "-"   , "datetime" ],
        [ 14    , pd.to_datetime("2020-08-13")],
        [ 1     ,  None   ],
    ]
    # fmt: on
    g = parse_blocks(table_lines_datetime, filter=lambda ty, tn: ty == BlockType.TABLE)
    typ, tab = next(g)
    assert tab.name == "tab_ok"
    assert tab.df["a1"][1] == 3.14
    assert tab.df["a2"][1] == pd.to_datetime("2020-08-12")

    with pytest.raises(ValueError):
        typ, tab = next(g)
        print(f"-oOo-: {typ} {tab}")


def test_converter():
    """ Unit test
        Verify that misc. float input are handled consistently
    """
    # fmt: off
    table_lines = [
        ["**flt_errors"],
        ["dst1"],
        [ "a1"  , "a2"  , "a3"  , "a4"  ],
        [ "-"   , "-"   , "-"   , "-"   ],
        [ "NaN" , "nan" , "Nine", "Ten" ],
        [ 1     , 2     , 3     , 3.14  ],
    ]
    # fmt: on
    pandas_pdtab = make_table(table_lines, fixer=_test_fixer)
    js_obj = table_to_json_data(pandas_pdtab)
    assert js_obj["columns"]["a3"]["values"][0] is None
    assert js_obj["columns"]["a4"]["values"][1] == 3.14

    assert _test_fixer.fixes == 2  # Nine and Ten
