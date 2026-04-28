import pandas as pd


def calculate_lookup_results(mat_data: dict, lookup_table: pd.DataFrame, row_values: list, col_values: list):
    """Compute results from processed MAT data and lookup table values.

    Parameters:
        mat_data (dict): Processed MAT data dictionary.
        lookup_table (pd.DataFrame): Lookup table values as a DataFrame.
        row_values (list): Numeric values used for lookup rows.
        col_values (list): Numeric values used for lookup columns.

    Returns:
        dict: A dictionary with calculation results and summaries.
    """
    results = {
        'row_values': row_values,
        'col_values': col_values,
        'lookup_shape': lookup_table.shape,
        'lookup_sum': lookup_table.values.sum(),
        'lookup_mean': float(lookup_table.values.mean()) if lookup_table.size else 0.0,
        'signals': {},
    }

    if mat_data is not None and 'sLap' in mat_data:
        try:
            sLap = mat_data['sLap']
            results['signals']['has_sLap'] = True
            results['signals']['sLap_len'] = len(sLap)
        except Exception:
            results['signals']['has_sLap'] = False
    else:
        results['signals']['has_sLap'] = False

    # Example placeholder logic: add a few derived items
    if lookup_table.size:
        results['lookup_min'] = float(lookup_table.values.min())
        results['lookup_max'] = float(lookup_table.values.max())
    else:
        results['lookup_min'] = None
        results['lookup_max'] = None

    return results
