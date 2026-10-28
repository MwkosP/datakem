from pathlib import Path

import pandas as pd


def writeAssetsToSheet(
    savePath: Path,
    dataByTicker: dict[str, pd.DataFrame],
) -> None:
    """Write asset tables side by side with two blank columns between them."""
    startColumn = 0

    with pd.ExcelWriter(savePath, engine="openpyxl", mode="w") as writer:
        for ticker, data in dataByTicker.items():
            data.to_excel(
                writer,
                sheet_name="Data",
                startrow=1,
                startcol=startColumn,
            )

            worksheet = writer.sheets["Data"]
            worksheet.cell(row=1, column=startColumn + 1, value=ticker)

            tableWidth = len(data.columns) + 1
            startColumn += tableWidth + 2
