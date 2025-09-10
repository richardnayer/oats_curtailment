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
import data_io.helpers as helpers

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



    def _load_excel_case(self, filepath: str, iterative: bool = False) -> None:
        """
        Load system case data from an Excel file.
        Args:
            filepath (str): Path to the Excel file.
            iterative (bool): Whether to load iterative data (not yet implemented).
        """
        filepath = Path(filepath)
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"Excel file not found: {filepath}")

        logger.info(f"Loading Excel file: {filepath}")
        excel_file = pd.ExcelFile(filepath, engine='openpyxl')
        logger.info(f"Excel file loaded: {filepath}")

        self._load_snapshot(excel_file)

        if iterative:
            self._load_iterations(excel_file)

    def _sheet_parser(self, excel_file: pd.ExcelFile, sheet_config: Dict[str, Dict[str, str]]) -> None:
        #Parse all sheets into individual dataframes, according to config settings, add to 'self' object.
        for sheet_name, config in sheet_config.items():
            if sheet_name not in excel_file.sheet_names:
                logger.warning(f"Sheet '{sheet_name}' not found in Excel file.")
                continue

            logger.debug(f"Processing sheet: {sheet_name}")
            df = excel_file.parse(sheet_name)

            if config.get('dropna') != None:
                df = df.dropna(how='all')

            if config.get('filter_active') != None:
                df = self._filter_nonzero_stat(df)

            if config.get('col_types') != None:
                df = self._apply_column_types(df, config['col_types'])

            if config.get('index') != None:
                df = df.set_index(config.get('index'))
            
            #Round values to reduce solver RHS differences
            df = df.round(6)

            self[config['key']] = df
            logger.info(f"Loaded {len(df)} rows into '{config['key']}'")

    def _load_snapshot(self, excel_file: pd.ExcelFile) -> None:
        """
        Load snapshot data from the excel file.
        Args:
            excel_file (object): Pandas Excel File Object
        """

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

        #Parse all sheets into dataframe and add to self
        self._sheet_parser(excel_file, sheet_config)

        #Convert baseMVA into a single value
        self._set_baseMVA()

    def _load_iterations(self, excel_file: pd.ExcelFile) -> None:
        #TODO Add description

        sheet_config: Dict[str, Dict[str, Any]] = {
            'ts_PD': {
                'key': 'ts_PD',
                'index': 'timestep',
                'dropna': True,
                'filter_active': True
            },
            'ts_VOLL': {
                'key': 'ts_VOLL',
                'index': 'timestep',
                'dropna': True,
                'filter_active': True
            },
            'ts_Lmax': {
                'key': 'ts_Lmax',
                'index': 'timestep',
                'dropna': True,
                'filter_active': True
            },
            'ts_TLmax': {
                'key': 'ts_TLmax',
                'index': 'timestep',
                'dropna': True,
                'filter_active': True
            },
            'ts_PGMINGEN': {
                'key': 'ts_PGMINGEN',
                'index': 'timestep',
                'dropna': True,
                'filter_active': True
            },
            'ts_PGLB': {
                'key': 'ts_PGLB',
                'index': 'timestep',
                'dropna': True,
                'filter_active': True
            },
            'ts_PGUB': {
                'key': 'ts_PGUB',
                'index': 'timestep',
                'dropna': True,
                'filter_active': True
            },
            'ts_bid': {
                'key': 'ts_bid',
                'index': 'timestep',
                'dropna': True,
                'filter_active': True
            }
        }

        #Parse all sheets into dataframe and add to self
        self._sheet_parser(excel_file, sheet_config)

        #Take timseries data from index and define as timesteps
        self.iterations = self.ts_PD.index

    def _set_baseMVA(self) -> float:
        if len(self.baseMVA['baseMVA']) > 1:
            raise Exception("More than one base MVA defined")
        
        self.baseMVA = self.baseMVA['baseMVA'][0]
        return None

    def summary(self) -> None:
        print("Case Summary:")
        for key, df in self.data.items():
            print(f" - {key}: {df.shape[0]} rows, {df.shape[1]} columns")


if __name__ == "__main__":
    testcase = Case()
    testcase._load_excel_snapshot_case("end-to-end-testcase.xlsx", timeseries=True)
    testcase.summary()

