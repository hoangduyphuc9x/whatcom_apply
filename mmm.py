import asyncio
import os.path
import sys
import time
import datetime

import requests
import json
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QCheckBox, QComboBox, QLabel
)
from sys import platform
from gologin import GoLogin
import random
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import string
import re


def setup_selenium_driver(debugger_address: str, chrome_driver_path: str) -> webdriver.Chrome:
    """
    Set up a Selenium WebDriver with specific configurations.

    :param debugger_address: Address of the debugger for Chrome DevTools Protocol.
    :type debugger_address: str
    :param chrome_driver_path: Path to the Chrome WebDriver executable.
    :type chrome_driver_path: str
    :return: Configured Selenium WebDriver instance.
    :rtype: selenium.webdriver.Chrome
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-notifications')
    # print(debugger_address)
    options.add_experimental_option("debuggerAddress", debugger_address)
    driver_service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=driver_service, options=options)
    driver.set_page_load_timeout(60)
    return driver

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Table with Buttons")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Column 1", "Column 2", "button"])

        self.layout.addWidget(self.table)

        # Add some dummy data to the table
        self.add_data_to_table()

    def add_data_to_table(self):
        data = [
            ("Row 1", "Value 1"),
            ("Row 2", "Value 2"),
            ("Row 3", "Value 3"),
            ("Row 4", "Value 4"),
            ("Row 5", "Value 5"),
        ]

        self.table.setRowCount(len(data))

        for row, (col1, col2) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(col1))
            self.table.setItem(row, 1, QTableWidgetItem(col2))

            button = QPushButton("Print")
            # button.clicked.connect(lambda _, r=row: self.print_row_value(r))
            button.clicked.connect(lambda checked=row,
                             r=row: self.print_row_value(checked))
            # button.clicked.connect(partial(self.print_row_value, row))

            self.table.setCellWidget(row, 2, button)

    def print_row_value(self, row):
        # gl = GoLogin({
        #     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NjE5YzM5M2FjNTQ4MDcyODZmZTUyMGUiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2NjE5YzNhNWNlYmQwODIxZDY2ZGJlZWYifQ.UrBemMOjHHOA6j_8uwFKB2J9avzpKZ5Xt0UH_DVPnoA",
        #     "profile_id": "661cff5cddb6bf61c864dd24",
        #     "port": 3543
        #     # "port": random.randint(3500, 7000)
        # })
        chrome_driver_path = "./mac_chromedriver/chromedriver" if platform == "darwin" else "./win_chromedriver/chromedriver.exe"
        # # gl.start()
        # gologin_profile_debugger_address = gl.start()
        gologin_profile_debugger_address = "127.0.0.1:3543"

        driver = setup_selenium_driver(gologin_profile_debugger_address, chrome_driver_path)
        item = self.table.item(row, 0)
        if item is not None:
            print("Value of the first column in row", row, ":", item.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
