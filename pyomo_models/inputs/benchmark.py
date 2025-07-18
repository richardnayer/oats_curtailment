import pandas as pd
import numpy as np
import timeit
from typing import Union

# Original function you gave
def _filtered_df_original(case: object, component: str, filter_param: Union[str, float, int], operation: str, filter_value: Union[str, float,int], returned_params: list = None):
    supported_operations = [None, '=', '!=', '>=', '>', '<=', '<']
    df = getattr(case,component)

    if any([filter_param, operation, filter_value]) and not all([filter_param, operation, filter_value]):
        raise ValueError("If any of filter_param, operation, or filter_value is set, all must be provided.")
    if operation not in supported_operations:
        raise ValueError(f"The operator {operation} is not defined for this function. Please use one of {supported_operations}")
    for param in [filter_param] + (returned_params or []):
        if param not in df.columns and param is not None:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data")
    if operation in ['>=', '>', '<=', '<']:
        if not pd.api.types.is_numeric_dtype(df[filter_param]):
            raise TypeError(f"The column '{filter_param}' must be numeric for operation '{operation}'")
        if not isinstance(filter_value, (int, float)):
            raise TypeError(f"The filter_value must be int or float for operation '{operation}'")

    op_map = {
        '=' : lambda df: df[filter_param] == filter_value,
        '!=': lambda df: df[filter_param] != filter_value,
        '>=': lambda df: df[filter_param] >= filter_value,
        '>' : lambda df: df[filter_param] >  filter_value,
        '<=': lambda df: df[filter_param] <  filter_value,
        '<' : lambda df: df[filter_param] <= filter_value,
    }

    if operation is None:
        if returned_params is None:
            return df
        else:
            return df.loc[:, returned_params]
    else:
        return df.loc[op_map[operation](df), returned_params] if returned_params else df.loc[op_map[operation](df)]


# NumPy-enhanced version
def _filtered_df_numpy(case: object, component: str, filter_param: Union[str, float, int], operation: str, filter_value: Union[str, float,int], returned_params: list = None):
    supported_operations = [None, '=', '!=', '>=', '>', '<=', '<']
    df = getattr(case,component)

    if any([filter_param, operation, filter_value]) and not all([filter_param, operation, filter_value]):
        raise ValueError("If any of filter_param, operation, or filter_value is set, all must be provided.")
    if operation not in supported_operations:
        raise ValueError(f"The operator {operation} is not defined for this function. Please use one of {supported_operations}")
    for param in [filter_param] + (returned_params or []):
        if param not in df.columns and param is not None:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data")
    if operation in ['>=', '>', '<=', '<']:
        if not pd.api.types.is_numeric_dtype(df[filter_param]):
            raise TypeError(f"The column '{filter_param}' must be numeric for operation '{operation}'")
        if not isinstance(filter_value, (int, float)):
            raise TypeError(f"The filter_value must be int or float for operation '{operation}'")

    if operation is None:
        return df if returned_params is None else df.loc[:, returned_params]
    else:
        col = df[filter_param].to_numpy()
        if operation == '=':
            mask = col == filter_value
        elif operation == '!=':
            mask = col != filter_value
        elif operation == '>=':
            mask = col >= filter_value
        elif operation == '>':
            mask = col > filter_value
        elif operation == '<=':
            mask = col <= filter_value
        elif operation == '<':
            mask = col < filter_value
        else:
            raise ValueError(f"Unsupported operation '{operation}'")

        idx = np.flatnonzero(mask)
        return df.iloc[idx] if returned_params is None else df.iloc[idx][returned_params]


# Dummy 'case' object with DataFrame attribute for testing
class Case:
    def __init__(self, df):
        self.component = df

# Generate large synthetic dataset
np.random.seed(42)
N = 10_000_000
df = pd.DataFrame({
    'numeric_col': np.random.randn(N),
    'string_col': np.random.choice(['apple', 'banana', 'cherry', 'date'], size=N),
    'other_col': np.random.randint(0, 100, size=N)
})

case = Case(df)

# Benchmarking function
def benchmark():
    tests = [
        # Numeric filter
        ("numeric_col", '>', 0.5, None),
        ("numeric_col", '<=', -1, ['numeric_col', 'other_col']),
        # String filter
        ("string_col", '=', 'banana', None),
        ("string_col", '!=', 'date', ['string_col', 'other_col']),
    ]

    n_runs = 5
    for filter_param, operation, filter_value, returned_params in tests:
        print(f"\nTest: filter_param={filter_param}, operation={operation}, filter_value={filter_value}, returned_params={returned_params}")

        # Original
        t_orig = timeit.timeit(
            lambda: _filtered_df_original(case, 'component', filter_param, operation, filter_value, returned_params),
            number=n_runs)
        print(f"Original function avg time over {n_runs} runs: {t_orig / n_runs:.6f} seconds")

        # NumPy enhanced
        t_np = timeit.timeit(
            lambda: _filtered_df_numpy(case, 'component', filter_param, operation, filter_value, returned_params),
            number=n_runs)
        print(f"NumPy-enhanced function avg time over {n_runs} runs: {t_np / n_runs:.6f} seconds")

benchmark()
