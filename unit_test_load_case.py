import pytest
import pandas as pd
from load_case import Case  # assuming your main code is in `case_loader.py`
from pathlib import Path

@pytest.fixture
def minimal_excel(tmp_path):
    # Create a minimal Excel file with required sheets
    filepath = tmp_path / "testcase.xlsx"
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        pd.DataFrame({'name': ['B1'], 'zone': ['Z1'], 'stat': [1]}).to_excel(writer, sheet_name='bus', index=False)
        pd.DataFrame({'name': ['D1'], 'busname': ['B1'], 'stat': [1]}).to_excel(writer, sheet_name='demand', index=False)
        pd.DataFrame({'name': ['G1'], 'busname': ['B1'], 'stat': [1]}).to_excel(writer, sheet_name='generator', index=False)
        pd.DataFrame({'base': [100]}).to_excel(writer, sheet_name='baseMVA', index=False)
    return filepath

def test_case_loading(minimal_excel):
    case = Case()
    case.load_excel_snapshot_case(str(minimal_excel))
    
    assert 'busses' in case
    assert 'demands' in case
    assert 'generators' in case
    assert 'baseMVA' in case
    assert isinstance(case.busses, pd.DataFrame)
    assert case.busses.shape[0] == 1

def test_missing_file_raises():
    case = Case()
    with pytest.raises(FileNotFoundError):
        case.load_excel_snapshot_case("nonexistent.xlsx")

def test_attribute_access():
    case = Case()
    case['foo'] = pd.DataFrame({'a': [1]})
    assert case.foo.equals(case['foo'])
