import pandas as pd
from excel_util import ws_set_header_style, ws_set_columns_width, ws_set_number_format


def is_no_residue(value):
    try:
        return float(value).is_integer()
    except (TypeError, ValueError):
        pass


def df_to_numeric(df: pd.DataFrame):
    for col in df.columns:
        if all([is_no_residue(v) for v in df[col]]):
            df[col] = df[col].astype(int, errors='ignore')
        else:
            df[col] = df[col].astype(float, errors='ignore')

    return df


def df_to_excel(df: pd.DataFrame, path, float_round_len=3):
    writer = pd.ExcelWriter(path, engine='openpyxl')

    df = df_to_numeric(df)
    df.to_excel(writer, sheet_name='Sheet1', startrow=1, header=False, index=False)

    worksheet = writer.sheets['Sheet1']

    ws_set_header_style(worksheet, df)
    ws_set_number_format(worksheet, float_round_len=float_round_len)
    ws_set_columns_width(worksheet, float_round_len=float_round_len)

    writer.save()
