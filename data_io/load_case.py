"""
__authors__ = "Richard Nayer"
__credits__ = "University of Strathclyde"
__version__ = "0.0.1"
__status__ = "Prototype"
__description__ = "Load and process case data from a specified directory. Code creation supported by chatGPT"
"""

import logging
from collections import UserDict
from pathlib import Path
from typing import Dict, Any
import pandas as pd

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Change to DEBUG for more details
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Case(UserDict):
    """
    A container for electrical system case data loaded from Excel.
    Allows dictionary-style and attribute-style access to components.
    """

    def __getattr__(self, item: str) -> pd.DataFrame:
        try:
            return self[item]
        except KeyError as e:
            raise AttributeError(f"'Case' object has no attribute '{item}'") from e

    def _filter_nonzero_stat(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df['stat'] != 0] if 'stat' in df.columns else df

    def _apply_column_types(self, df: pd.DataFrame, col_types: Dict[str, type]) -> pd.DataFrame:
        for col, dtype in col_types.items():
            if col in df.columns:
                try:
                    df[col] = df[col].astype(dtype)
                except Exception as e:
                    raise ValueError(f"Error converting column '{col}' to {dtype}: {e}")
        return df

    def _load_excel_snapshot_case(self, filepath: str, timeseries: bool = False) -> None:
        """
        Load system case data from an Excel file.
        Args:
            filepath (str): Path to the Excel file.
            timeseries (bool): Whether to load timeseries data (not yet implemented).
        """
        filepath = Path(filepath)
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"Excel file not found: {filepath}")

        logger.info(f"Loading Excel file: {filepath}")
        excel_file = pd.ExcelFile(filepath, engine='openpyxl')
        logger.info(f"Excel file loaded: {filepath}")

        sheet_config: Dict[str, Dict[str, Any]] = {
            'bus': {
                'key': 'busses',
                'col_types': {'name': pd.StringDtype(),
                              'baseKV': float,
                              'type': int,
                               'zone': pd.StringDtype(),
                },
                'dropna': True,
                'filter_active': True
            },
            'demand': {
                'key': 'demands',
                'col_types': {'name': pd.StringDtype(),
                               'busname': pd.StringDtype(),
                               'real': float,
                               'stat': int,
                               'VOLL': int
                },
                'dropna': True,
                'filter_active': True
            },
            'branch': {
                'key': 'branches',
                'col_types': {'name': pd.StringDtype(),
                              'from_busname': pd.StringDtype(),
                              'to_busname': pd.StringDtype(),
                              'stat': int,
                              'r': float,
                              'x': float,
                              'b': float,
                              'ShortTermRating': int,
                              'ContinousRating': int 
                },
                'dropna': True,
                'filter_active': True
            },
            'transformer': {
                'key': 'transformers',
                'col_types': {'name': pd.StringDtype(),
                              'from_busname': pd.StringDtype(),
                              'to_busname': pd.StringDtype(),
                              'type': pd.StringDtype(),
                              'stat': int,
                              'r': float,
                              'x': float,
                              'b': float,
                              'ShortTermRating': int,
                              'ContinousRating': int
                },
                'dropna': True,
                'filter_active': True
            },
            'generator': {
                'key': 'generators',
                'col_types': {'busname': pd.StringDtype(),
                              'name': pd.StringDtype(),
                              'export_policy': pd.StringDtype(),
                              'lifo_group': pd.StringDtype(),
                              'lifo_position': pd.StringDtype(),
                              'prorata_groups': pd.StringDtype(),
                              'stat': int,
                              'type': pd.StringDtype(),
                              'PGMINGEN': float,
                              'PGLB': float,
                              'PGUB': float,
                              'FuelType': pd.StringDtype(),
                              'synchronous': pd.StringDtype(),
                              'costc1': float,
                              'costc0': float,
                              'bid': float,
                              'offer': float
                },
                'dropna': True,
                'filter_active': True
            },
            'baseMVA': {
                'key': 'baseMVA',
                'col_types': {'baseMVA': float},
                'dropna': True,
                'filter_active': False
            }
        }

        #Parse all sheets into individual dataframes, according to config settings 
        for sheet_name, config in sheet_config.items():
            if sheet_name not in excel_file.sheet_names:
                logger.warning(f"Sheet '{sheet_name}' not found in Excel file.")
                continue

            logger.debug(f"Processing sheet: {sheet_name}")
            df = excel_file.parse(sheet_name)

            if config.get('dropna', True):
                df = df.dropna(how='all')

            if config.get('filter_active', True):
                df = self._filter_nonzero_stat(df)

            df = self._apply_column_types(df, config['col_types'])
            self[config['key']] = df
            logger.info(f"Loaded {len(df)} rows into '{config['key']}'")

        #Convert baseMVA into a single value
        self._set_baseMVA()

        if timeseries:
            self._load_timeseries(excel_file)
            #TODO Implement Load_Timeseries

    def _load_timeseries(self, excel_file: pd.ExcelFile) -> None:
       #TODO Implement Load_Timeseries
        """
        Placeholder for timeseries data handling.
        Currently not implemented.
        """
        logger.info("Timeseries support is not yet implemented.")

    def _set_baseMVA(self) -> float:
        if len(self.baseMVA['baseMVA']) > 1:
            raise Exception("More than one base MVA defined")
        
        self.baseMVA = self.baseMVA['baseMVA'][0]
        return None

    def summary(self) -> None:
        print("Case Summary:")
        for key, df in self.data.items():
            print(f" - {key}: {df.shape[0]} rows")



if __name__ == "__main__":
    testcase = Case()
    testcase._load_excel_snapshot_case("end-to-end-testcase.xlsx", timeseries=True)
    testcase.summary()

