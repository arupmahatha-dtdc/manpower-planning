import math
from typing import Dict, Any, List, Tuple

import pandas as pd
import streamlit as st


@st.cache_data
def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    return df


def roundup(x: float, digits: int = 0) -> float:
    factor = 10 ** digits
    return math.ceil(x * factor) / factor


# Ordered list of derived fields and their formulas (must remain ordered for dependency resolution)
FORMULAS: Dict[str, str] = {
    'in_avg_wt_cn': "row['in_ndx_vol_wt'] / row['in_ndx_out_vol']",
    'out_avg_wt_cn': "row['out_ndx_vol_wt'] / row['out_ndx_out_vol']",
    'packet': "max(row['in_docs'], row['out_docs']) / 15",
    'bag_doc': "(max(row['in_docs'], row['out_docs']) / 15) / 15",
    'vol_bag_non_doc': "max(row['in_ndx_out_vol'], row['out_ndx_out_vol']) / 13",
    'wt_bag_non_doc': "max(row['in_ndx_vol_wt'], row['out_ndx_vol_wt']) / 25",
    'out_per_day_docs': "roundup(row['out_docs'] / 25, 0)",
    'out_per_day_non_docs': "roundup(row['out_non_docs'] / 25, 0)",
    'out_per_day_air': "roundup(row['out_air'] / 25, 0)",
    'out_per_day_surface': "roundup(row['out_surface'] / 25, 0)",
    'out_per_day_ndx_out_vol': "roundup(row['out_ndx_out_vol'] / 25, 0)",
    'out_per_day_ndx_vol_wt': "roundup(row['out_ndx_vol_wt'] / 25, 0)",
    'in_per_day_docs': "roundup(row['in_docs'] / 25, 0)",
    'in_per_day_non_docs': "roundup(row['in_non_docs'] / 25, 0)",
    'in_per_day_air': "roundup(row['in_air'] / 25, 0)",
    'in_per_day_surface': "roundup(row['in_surface'] / 25, 0)",
    'in_per_day_ndx_out_vol': "roundup(row['in_ndx_out_vol'] / 25, 0)",
    'in_per_day_ndx_vol_wt': "roundup(row['in_ndx_vol_wt'] / 25, 0)",
    'per_day_ndx': "max(row['out_per_day_non_docs'], row['in_per_day_non_docs'])",
    'per_day_dox': "max(row['out_per_day_docs'], row['in_per_day_docs'])",
    'per_day_packet': "row['packet'] / 25",
    'per_day_bag_doc': "row['bag_doc'] / 25",
    'per_day_bag_non_doc': "max(row['vol_bag_non_doc'], row['wt_bag_non_doc']) / 25",
    'per_day_air': "row['out_per_day_air'] / 12",
    'cd_unit': "(row['per_day_bag_doc'] + row['per_day_bag_non_doc']) * 35 / 3600",
    'with_sorter_sorter_unit': "20.16 * row['per_day_ndx'] * 0.55 / 3600",
    'with_sorter_non_cony': "(row['with_sorter_sorter_unit'] * 0.3 * 1.5) / 0.55",
    'manual_sorting_units': "row['per_day_ndx'] * 31.1 / 3600",
    # Compute atomic unit workloads before skidder_unit which sums them
    'xray_unit': "row['per_day_air'] * 15 / 3600",
    'air_unit': "row['per_day_air'] * 38 / 3600",
    'surface_unit': "((row['per_day_bag_doc'] + row['per_day_bag_non_doc']) - row['per_day_air']) * 38 / 3600",
    'doc_unit': "(0.6 * row['per_day_dox'] * 10.02222222) / 3600",
    'exception_han_unit': "0.05 * 30 * row['per_day_ndx'] / 3600",
    'skidder_unit': "0.1 * (sum([row['cd_unit'], row['with_sorter_sorter_unit'], row['with_sorter_non_cony'], row['manual_sorting_units'], row['xray_unit'], row['air_unit'], row['surface_unit'], row['doc_unit'], row['exception_han_unit']]))",
    'total': "1.2 * (sum([row['cd_unit'], row['with_sorter_sorter_unit'], row['with_sorter_non_cony'], row['manual_sorting_units'], row['skidder_unit'], row['xray_unit'], row['air_unit'], row['surface_unit'], row['doc_unit'], row['exception_han_unit']]) - row['manual_sorting_units'])",
    'manpower_in_units_cd_unit': "roundup(row['cd_unit'] * 1.25 / row['at'], 0)",
    'manpower_in_units_with_sorter_sorter_unit': "roundup(row['with_sorter_sorter_unit'] * 1.25 / row['at'], 0)",
    'manpower_in_units_with_sorter_non_cony': "roundup(row['with_sorter_non_cony'] * 1.25 / row['at'], 0)",
    'manpower_in_units_with_no_sorter_manual_sorting_units': "roundup(row['manual_sorting_units'] * 1.25 / row['at'], 0)",
    'manpower_in_units_skidder_unit': "roundup(row['skidder_unit'] * 1.25 / row['at'], 0)",
    'manpower_in_units_xray_unit': "roundup(row['xray_unit'] * 1.25 / row['at'], 0)",
    'manpower_in_units_air_unit': "roundup(row['air_unit'] * 1.25 / row['at'], 0)",
    'manpower_in_units_surface_unit': "roundup(row['surface_unit'] * 1.25 / row['at'], 0)",
    'manpower_in_units_doc_unit': "roundup(row['doc_unit'] * 1.25 / row['at'], 0)",
    'manpower_in_units_exception_han_unit': "roundup(row['exception_han_unit'] * 1.25 / row['at'], 0)",
    'manpower_with_sorter': "sum([row['manpower_in_units_cd_unit'], row['manpower_in_units_with_sorter_sorter_unit'], row['manpower_in_units_with_sorter_non_cony'], row['manpower_in_units_with_no_sorter_manual_sorting_units'], row['manpower_in_units_skidder_unit'], row['manpower_in_units_xray_unit'], row['manpower_in_units_air_unit'], row['manpower_in_units_surface_unit'], row['manpower_in_units_doc_unit'], row['manpower_in_units_exception_han_unit']]) - row['manpower_in_units_with_no_sorter_manual_sorting_units']",
    'manpower_without_sorter': "sum([row['manpower_in_units_cd_unit'], row['manpower_in_units_with_sorter_sorter_unit'], row['manpower_in_units_with_sorter_non_cony'], row['manpower_in_units_with_no_sorter_manual_sorting_units'], row['manpower_in_units_skidder_unit'], row['manpower_in_units_xray_unit'], row['manpower_in_units_air_unit'], row['manpower_in_units_surface_unit'], row['manpower_in_units_doc_unit'], row['manpower_in_units_exception_han_unit']]) - row['manpower_in_units_with_sorter_sorter_unit'] - row['manpower_in_units_with_sorter_non_cony']",
}


# Base inputs the user is allowed to change
BASE_INPUT_FIELDS: List[str] = [
    'out_docs', 'out_non_docs', 'out_air', 'out_surface', 'out_ndx_out_vol', 'out_ndx_vol_wt',
    'in_docs', 'in_non_docs', 'in_air', 'in_surface', 'in_ndx_out_vol', 'in_ndx_vol_wt',
    'sorter', 'at'
]


# Correlated base inputs to warn the user about if they try to change together
CORRELATED_SETS: List[Tuple[str, str]] = [
    ('in_ndx_out_vol', 'in_ndx_vol_wt'),
    ('out_ndx_out_vol', 'out_ndx_vol_wt'),
]


def compute_derived(row: Dict[str, Any], locked_keys: List[str] | None = None) -> Dict[str, Any]:
    # Evaluate in declared order; do not overwrite user-overridden (locked) keys
    locked = set(locked_keys or [])
    safe_globals = {'roundup': roundup, 'max': max, 'sum': sum}
    for key, expr in FORMULAS.items():
        if key in locked:
            continue
        try:
            row[key] = eval(expr, safe_globals, {'row': row})
        except Exception:
            row[key] = float('nan')
    return row


def main() -> None:
    st.set_page_config(page_title='Manpower Planning Dashboard', layout='wide')
    st.title('Manpower Planning Dashboard')

    # Lightweight UI polish
    st.markdown(
        """
        <style>
        /* Compact metrics */
        div[data-testid="stMetric"] > label {
            font-size: 0.9rem;
            color: #4a4f5b;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.2rem;
        }
        /* Section spacing */
        .section-spacer { margin: 0.5rem 0 0.25rem 0; }
        /* Card-like container divider effect */
        .shift-card { padding: 0.25rem 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    data_path = '/Users/arup/Documents/manpower-planning/hub_manpower_modelling.csv'
    df = load_data(data_path)

    # Selection: only Hub Code
    hub_code = st.selectbox(
        'Select Hub Code',
        sorted(df['hub_code'].unique()),
        index=None,
        placeholder='Choose Hub Code'
    )

    # Require selection before proceeding
    if hub_code is None:
        st.info('Please select Hub Code to continue.')
        st.stop()

    # Subset data for chosen hub
    hub_df = df.loc[df['hub_code'] == hub_code].copy()
    if hub_df.empty:
        st.error('No data found for selected Hub Code.')
        st.stop()

    st.markdown('---')
    st.subheader('Inputs')
    # Global inputs (user-provided): per_day_ndx and per_day_dox
    # Use hub-wide first row as baseline for sensible defaults
    baseline_row = compute_derived(hub_df.iloc[0].to_dict())
    default_ndx = float(baseline_row.get('per_day_ndx', 0) or 0)
    default_dox = float(baseline_row.get('per_day_dox', 0) or 0)
    cols_in = st.columns(2)
    with cols_in[0]:
        input_per_day_ndx = st.number_input('Per Day NDX', value=default_ndx, format='%f')
    with cols_in[1]:
        input_per_day_dox = st.number_input('Per Day DOX', value=default_dox, format='%f')

    st.markdown('---')
    st.subheader('Shift-wise Outputs')
    # For each shift in the selected hub, compute results using the two user inputs
    shifts = sorted(hub_df['shift_slots'].unique())
    if not shifts:
        st.info('No shifts found for this Hub Code.')
    else:
        for shift in shifts:
            row_series = hub_df.loc[hub_df['shift_slots'] == shift].head(1)
            if row_series.empty:
                continue
            base_row = row_series.iloc[0].to_dict()
            # Apply the two inputs and compute
            working_row = dict(base_row)
            working_row['per_day_ndx'] = float(input_per_day_ndx)
            working_row['per_day_dox'] = float(input_per_day_dox)
            computed_row = compute_derived(working_row, locked_keys=['per_day_ndx', 'per_day_dox'])

            m_with = computed_row.get('manpower_with_sorter', float('nan'))
            m_without = computed_row.get('manpower_without_sorter', float('nan'))

            st.markdown('<div class="shift-card">', unsafe_allow_html=True)
            st.markdown(f"**Shift: {shift}**", help=None)
            cols_out = st.columns(4)
            with cols_out[1]:
                try:
                    st.metric('Manpower With Sorter', f"{float(m_with):.4f}")
                except Exception:
                    st.info('Manpower With Sorter: N/A')
            with cols_out[2]:
                try:
                    st.metric('Manpower Without Sorter', f"{float(m_without):.4f}")
                except Exception:
                    st.info('Manpower Without Sorter: N/A')
            st.markdown('</div>', unsafe_allow_html=True)

    # Detailed per-shift debug view can be added if needed.


if __name__ == '__main__':
    main()


