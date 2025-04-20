import os
import sys
import pandas as pd
import psycopg2
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog,
                             QMessageBox)


class ExcelToPostgresApp(QWidget):
    def init(self):
        super().init()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Excel to PostgreSQL Loader")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.db_host = QLineEdit("localhost")
        self.db_port = QLineEdit("5432")
        self.db_name = QLineEdit("test1")
        self.db_user = QLineEdit("myuser")
        self.db_pass = QLineEdit("mypassword")
        self.folder_path = QLineEdit()

        layout.addWidget(QLabel("Host:"))
        layout.addWidget(self.db_host)
        layout.addWidget(QLabel("Port:"))
        layout.addWidget(self.db_port)
        layout.addWidget(QLabel("Database:"))
        layout.addWidget(self.db_name)
        layout.addWidget(QLabel("User:"))
        layout.addWidget(self.db_user)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.db_pass)

        btn_select_folder = QPushButton("Select Excel Folder")
        btn_select_folder.clicked.connect(self.select_folder)
        layout.addWidget(btn_select_folder)
        layout.addWidget(self.folder_path)

        btn_upload = QPushButton("Upload to PostgreSQL")
        btn_upload.clicked.connect(self.upload_to_postgres)
        layout.addWidget(btn_upload)

        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_path.setText(folder)

    def upload_to_postgres(self):
        db_params = {
            "host": self.db_host.text(),
            "port": self.db_port.text(),
            "dbname": self.db_name.text(),
            "user": self.db_user.text(),
            "password": self.db_pass.text()
        }
        folder = self.folder_path.text()

        if not folder:
            QMessageBox.warning(self, "Error", "Please select a folder")
            return

        try:
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()

            for file in os.listdir(folder):
                if file.endswith(".xlsx"):
                    file_path = os.path.join(folder, file)
                    xls = pd.ExcelFile(file_path)
                    for sheet_name in xls.sheet_names:
                        df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")
                        table_name = f"{os.path.splitext(file)[0]}_{sheet_name}".replace(" ", "_").lower()
                        self.create_table_from_excel(cursor, table_name, df)

            conn.commit()
            cursor.close()
            conn.close()
            QMessageBox.information(self, "Success", "Data uploaded successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def create_table_from_excel(self, cursor, table_name, df):
        columns = ", ".join([f'"{col}" TEXT' for col in df.columns])
        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
        cursor.execute(f'CREATE TABLE "{table_name}" ({columns})')

        for _, row in df.iterrows():
            values = "', '".join([str(val).replace("'", "''") for val in row])
            cursor.execute(f'INSERT INTO "{table_name}" VALUES (\'{values}\')')


if name == "main":
    app = QApplication(sys.argv)
    window = ExcelToPostgresApp()
    window.show()
    sys.exit(app.exec())