import io
import pandas as pd


def export_excel(sheet_dict):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for sheet_name, df in sheet_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    buffer.seek(0)
    return buffer


def export_excel_grouped(grouped_dict):
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for sheet_name, sections in grouped_dict.items():
            startrow = 0
            for title, df in sections:
                pd.DataFrame([[title]]).to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False, header=False)
                startrow += 1
                df.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False)
                startrow += len(df) + 3

    buffer.seek(0)
    return buffer
