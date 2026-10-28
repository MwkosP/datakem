import sys
from pathlib import Path

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from datakem.data import fetchAssetData
from datakem.data.__helper__ import preprocessAssetData
from datakem.ui.__helper__ import writeAssetsToSheet


class AssetDataWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Asset Data Fetcher")
        self.setMinimumWidth(520)
        self.buildUi()

    def buildUi(self) -> None:
        self.tickerInput = QLineEdit()
        self.tickerInput.setPlaceholderText("Example: BTC-USD")
        addAssetButton = QPushButton("Add asset")
        addAssetButton.clicked.connect(self.addAsset)
        self.tickerInput.returnPressed.connect(self.addAsset)

        tickerLayout = QHBoxLayout()
        tickerLayout.addWidget(self.tickerInput)
        tickerLayout.addWidget(addAssetButton)

        self.assetList = QListWidget()
        self.assetList.addItem("BTC-USD")
        self.assetList.setMaximumHeight(100)
        removeAssetButton = QPushButton("Remove selected")
        removeAssetButton.clicked.connect(self.removeSelectedAssets)

        self.intervalInput = QComboBox()
        self.intervalInput.addItems(
            ["1m", "5m", "15m", "30m", "1h", "1d", "5d", "1wk", "1mo"]
        )
        self.intervalInput.setCurrentText("1d")

        self.missingDataInput = QComboBox()
        self.missingDataInput.addItem("No preprocessing", "keep")
        self.missingDataInput.addItem("Delete rows with null values", "drop")
        self.missingDataInput.addItem("Fill null values with SMA (5)", "sma")
        self.missingDataInput.addItem("Fill null values with EMA (5)", "ema")

        self.startInput = QDateEdit(QDate.currentDate().addYears(-1))
        self.startInput.setCalendarPopup(True)
        self.startInput.setDisplayFormat("yyyy-MM-dd")

        self.endInput = QDateEdit(QDate.currentDate())
        self.endInput.setCalendarPopup(True)
        self.endInput.setDisplayFormat("yyyy-MM-dd")

        self.saveInput = QLineEdit(str(Path.cwd() / "asset_data.xlsx"))
        browseButton = QPushButton("Browse...")
        browseButton.clicked.connect(self.selectSaveFile)

        saveLayout = QHBoxLayout()
        saveLayout.addWidget(self.saveInput)
        saveLayout.addWidget(browseButton)

        formLayout = QFormLayout()
        formLayout.addRow("Ticker:", tickerLayout)
        formLayout.addRow("Assets:", self.assetList)
        formLayout.addRow("", removeAssetButton)
        formLayout.addRow("Interval:", self.intervalInput)
        formLayout.addRow("Preprocessing method:", self.missingDataInput)
        formLayout.addRow("Start:", self.startInput)
        formLayout.addRow("End:", self.endInput)
        formLayout.addRow("Save as:", saveLayout)

        fetchButton = QPushButton("Fetch and Save")
        fetchButton.clicked.connect(self.fetchAndSave)

        self.statusLabel = QLabel("Ready")

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(formLayout)
        mainLayout.addWidget(fetchButton)
        mainLayout.addWidget(self.statusLabel)

        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def addAsset(self) -> None:
        ticker = self.tickerInput.text().strip().upper()
        currentTickers = {
            self.assetList.item(index).text()
            for index in range(self.assetList.count())
        }

        if ticker and ticker not in currentTickers:
            self.assetList.addItem(ticker)
        self.tickerInput.clear()

    def removeSelectedAssets(self) -> None:
        for item in self.assetList.selectedItems():
            self.assetList.takeItem(self.assetList.row(item))

    def selectSaveFile(self) -> None:
        filePath, _ = QFileDialog.getSaveFileName(
            self,
            "Save asset data",
            self.saveInput.text(),
            "Excel workbook (*.xlsx)",
        )
        if filePath:
            self.saveInput.setText(filePath)

    def fetchAndSave(self) -> None:
        tickers = [
            self.assetList.item(index).text()
            for index in range(self.assetList.count())
        ]
        interval = self.intervalInput.currentText()
        missingDataMethod = self.missingDataInput.currentData()
        saveText = self.saveInput.text().strip()

        if not tickers or not saveText:
            QMessageBox.warning(
                self,
                "Missing input",
                "Add at least one asset and choose a save path.",
            )
            return

        if self.startInput.date() > self.endInput.date():
            QMessageBox.warning(
                self,
                "Invalid dates",
                "The start date must be before the end date.",
            )
            return
        start = self.startInput.date().toString("yyyy-MM-dd")
        end = self.endInput.date().toString("yyyy-MM-dd")

        savePath = Path(saveText)
        if savePath.suffix.lower() != ".xlsx":
            savePath = savePath.with_suffix(".xlsx")
            self.saveInput.setText(str(savePath))

        try:
            dataByTicker = {}
            for ticker in tickers:
                self.statusLabel.setText(f"Fetching {ticker}...")
                QApplication.processEvents()
                data = fetchAssetData(
                    ticker=ticker,
                    start=start,
                    end=end,
                    interval=interval,
                )
                dataByTicker[ticker] = preprocessAssetData(
                    data,
                    missingDataMethod,
                )

            writeAssetsToSheet(savePath, dataByTicker)
        except Exception as error:
            self.statusLabel.setText("Failed")
            QMessageBox.critical(self, "Fetch failed", str(error))
            return

        totalRows = sum(len(data) for data in dataByTicker.values())
        self.statusLabel.setText(
            f"Saved {totalRows} rows for {len(tickers)} assets to {savePath}"
        )
        QMessageBox.information(self, "Complete", f"Saved data to:\n{savePath}")


def runUi() -> None:
    app = QApplication(sys.argv)
    window = AssetDataWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    runUi()
