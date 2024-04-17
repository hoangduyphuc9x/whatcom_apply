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
import concurrent.futures

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
WC_WEEKEND_TEAM_SHEET_ID = "1uEkPu8l7XUlTIM17S_Sdn40YcvbM4xEHWuXpuf7hGNE"
TOOLS_SHEET_NAME = "Tools"
IP_SHEET_NAME = "IP"
PROMPT_TEXT_MAP = {
    "1": "こんにちはと聞くとぺこりとお辞儀をするようになりました",
    "2": "言葉遣いはその言葉を発する人柄を反映します",
    "3": "宝くじに当たるより雷に打たれる確率の方が高いらしい",
    "4": "本当かどうかわざわざ確かめた気得な人がいました",
    "5": "職場の新幹パーティーの企画と実行を任された",
    "6": "その名前はツートン、セトゥンなどと様々な日本語読みがある。",
    "7": "その名前はツートンソトンなどといろいろな日本語読みがある",
    "8": "海でウニや貝などを勝手に取ってはいけません",
    "9": "政治的な後ろ盾のない光源氏は進化の地位に置かれた",
    "10": "ビデオ判定が最も手っ取り早く確実な誤診対策である",
    "11": "サッカーにおいても微量判定の是非が議論されています",
    "12": "大学に限らず、全般的に日本の教育はキロに立たされている",
    "13": "道路は道幅が狭く普通車同士が対抗するのも困難だった",
    "14": "日本では完全禁煙を打たう施設はまだまだ少数派だ",
    "15": "ハリーポッターを言語で読もうと頑張ってみた",
    "16": "ダーウィンの死の起源は一部では依然受け入れられていない",
    "17": "地元でのオリンピック開催という長年の夢が叶う",
    "18": "開催地として立候補するには条件にかなわなければならない",
    "19": "結婚にふさわしい相手を探すために日々婚活に励む",
    "20": "マイクロチップは迷子になったペットを探すのに役立つ",
    "21": "この仕事には的確な判断が求められる",
    "22": "この仕事には的確な人材が求められる",
    "23": "そこは全国有数のニシンの産地として有名だ",
    "24": "そこは全国有数のミシンの生産地として知られる",
    "25": "大河ドラマの影響でちょっとした坂本龍馬ブームだった",
    "26": "病院へはいくつか山を越えていかなければならなかった",
    "27": "その騒音はもはや我慢の限界を超えていた",
    "28": "強風で倒れた大木の一部を植え直し再生を試みた",
    "29": "枕草子は最も親しまれ暗唱されている古典の一つだ",
    "30": "地元の博物館には古い木の橋が展示してある",
    "31": "地元の博物館には古い木の箸が展示してある",
    "32": "人形が倒れて花が取れてしまいました",
    "33": "人形は倒れて鼻が取れてしまいました",
    "34": "転んでぶつかって歯が折れてしまいました",
    "35": "強い風にあおられて葉が折れてしまいました",
    "36": "天気を間違えるとせっかくの眺望が台無しだ",
    "37": "転記を間違えるとせっかくの帳簿が台無しだ",
    "38": "政府は不正再発を防止するための取り組みを強化した",
    "39": "政府は不正な開発を防止するための取り組みを強化した",
    "40": "勝負においては形勢を保つことができるかどうかが大事だ",
    "41": "勝負においては平成を楽すことができるかどうかが大事だ",
    "42": "その点については再度の見直しが必要です",
    "43": "その辺については態度の見直しが必要です",
    "44": "大化の会心は日本初のクーデターと言われている",
    "45": "東京スカイツリーには伝統技術を生かした耐震構造が用いられている",
    "46": "それは家庭では上手に調理するのは難しい",
    "47": "それは家庭では上手に修理するのは難しい",
    "48": "誰もが今よそしと終戦を待ちわびていた",
    "49": "職場で恒例の花見大会の漢字を任されてしまった",
    "50": "職場で恒例の花火大会の漢字を任されてしまった",
    "51": "首相の支持率に関する最近の世論調査の結果が出ました",
    "52": "誰もが今やお祖師と抽選を待ちわびていた",
}
PAGE_LOAD_TIMEOUT = 120
PROFILE_TABLE_HEADERS = [
    {
        "ID": "SELECT",
        "VALUE": "Chọn"
    }, {
        "ID": "STT",
        "VALUE": "Số thứ tự"
    }, {
        "ID": "PROXY",
        "VALUE": "Proxy"
    }, {
        "ID": "IP",
        "VALUE": "IP"
    }, {
        "ID": "PROXY_SITE",
        "VALUE": "Trang Proxy"
    }, {
        "ID": "LOCAL",
        "VALUE": "Local"
    }, {
        "ID": "ACCOUNT_INDEX",
        "VALUE": "Mã số"
    }, {
        "ID": "HOTMAIL_PASS",
        "VALUE": "Hotmail|Password"
    },
    {
        "ID": "MAIL_APPEN",
        "VALUE": "Mail Appen"
    },
    {
        "ID": "PASS_APPEN",
        "VALUE": "Pass Appen"
    },
    {
        "ID": "PROFILE_GOLOGIN",
        "VALUE": "Profile Gologin"
    },
    {
        "ID": "RESULT",
        "VALUE": "Kết quả"
    }, {
        "ID": "START_GOLOGIN",
        "VALUE": "Bắt đầu"
    },
    # {
    #     "ID": "RELOAD_GOLOGIN_PROFILES",
    #     "VALUE": "Reload Gologin Profiles"
    # }

]
SEE_COMPANY_LIST = ["Lionbridge", "Leapforce", "iSoftStone", "Clickworker", "Crowdsource",
                    "Amazon Mechanical Turk (MTurk)", "OneSpace", "Upwork", "Rev", "Spare5",
                    "Scribie", "UTest", "Testbirds", "Test IO", "TranscribeMe", "Crossover",
                    "Fancy Hands", "Fancyhires"]
proxy_detect_patterns = [
    r'(?P<scheme>\w+)://(?:(?P<username>\w+):(?P<password>\w+)@)?(?P<host>[\w\.-]+)(?::(?P<port>\d+))?',
    r'(?:(?P<username>\w+):(?P<password>\w+)@)?(?P<host>[\w\.-]+)(?::(?P<port>\d+))?',
    r'(?P<scheme>\w+)://(?P<host>[\w\.-]+)(?::(?P<port>\d+))?',
    r'(?P<host>[\w\.-]+)(?::(?P<port>\d+))?',
    r'\[(?P<host>[\w:]+)\](?::(?P<port>\d+))?',
]

if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
    TOOLS_SHEET_NAME = f"{TOOLS_SHEET_NAME}_debug"
    IP_SHEET_NAME = f"{IP_SHEET_NAME}_debug"

google_creds = None
if os.path.exists("token.json"):
    google_creds = Credentials.from_authorized_user_file("token.json", SCOPES)
if not google_creds or not google_creds.valid:
    if google_creds and google_creds.expired and google_creds.refresh_token:
        google_creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_config(
            {"installed": {
                "client_id": "369713733636-7flq53e79nlqb27k50pskrq98b0ln8i0.apps.googleusercontent.com",
                "project_id": "weakend-team", "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "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", "redirect_uris": ["http://localhost"]}},
            SCOPES
        )
        google_creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
        token.write(google_creds.to_json())
try:
    service = build('sheets', 'v4', credentials=google_creds)
except Exception as e:
    print(e)
    service = build('sheets', 'v4', credentials=google_creds,
                    discoveryServiceUrl='https://sheets.googleapis.com/$discovery/rest?version=v4')
serviceSpreadSheet = service.spreadsheets()


def extract_proxy_info(proxy_str):
    for pattern in proxy_detect_patterns:
        match = re.match(pattern, proxy_str)
        if match:
            return match.groupdict()
    return None


def create_gologin_profile(gologin_profile_options: dict) -> dict:
    """
    create_gologin_profile Function Documentation
=============================================

This function `create_gologin_profile` is responsible for creating a new GoLogin profile using the provided options. It communicates with the GoLogin API to create the profile.

Parameters
----------
gologin_profile_options : dict
    A dictionary containing options required to create the GoLogin profile. It should contain the following keys:

    - ``"proxy"`` (str): Proxy information in the format "host:port:username:password".
    - ``"goLoginToken"`` (str): The GoLogin token used for authentication.
    - ``"name"`` (str): Name of the GoLogin profile.
    - ``"os"`` (str): Operating system information for the GoLogin profile.

Returns
-------
dict
    A dictionary containing the following keys:

    - ``"error"``: If an error occurs during the profile creation process, it will contain a string describing the error. If no error occurs, this key will be `None`.
    - ``"data"``: If the profile creation is successful, it will contain a dictionary with information about the created GoLogin profile. This includes the `goLoginId`.

Workflow
--------
1. Extract necessary information from ``gologin_profile_options``.
2. Call ``get_gologin_fingerprint`` to retrieve fingerprint data based on the provided GoLogin token and operating system.
3. Prepare the data required for creating the GoLogin profile using the retrieved fingerprint data and the provided options.
4. Send a POST request to the GoLogin API to create the profile.
5. If the request is successful (status code 200 or 201), return the `goLoginId` of the created profile.
6. If an error occurs during the request or processing, return an error message.

Example Usage
-------------
.. code-block:: python

    options = {
        "proxy": "proxy_host:proxy_port:username:password",
        "goLoginToken": "your_gologin_token",
        "name": "Profile Name",
        "os": "Windows 10"
    }

    profile_creation_result = create_gologin_profile(options)
    if profile_creation_result["error"]:
        print("Error:", profile_creation_result["error"])
    else:
        print("GoLogin Profile Created Successfully. Profile ID:", profile_creation_result["data"]["goLoginId"])

Note
----
- This function requires the ``requests`` module to be imported.
- Ensure that the provided GoLogin token is valid and has the necessary permissions to create profiles.
- The proxy information provided should be in the format ``"host:port:username:password"``. If no proxy is required, provide an empty string.
- The function assumes that ``get_gologin_fingerprint`` is defined elsewhere and returns the necessary fingerprint data.

    """
    try:
        gologin_profile_proxy = gologin_profile_options["proxy"]
        go_login_token = gologin_profile_options["goLoginToken"]
        gologin_profile_name = gologin_profile_options["name"]
        gologin_profile_os = gologin_profile_options["os"]

        get_gologin_fingerprint_result = get_gologin_fingerprint(go_login_token, gologin_profile_os)
        get_gologin_fingerprint_result_error = get_gologin_fingerprint_result.get("error")
        if not get_gologin_fingerprint_result_error:
            get_gologin_fingerprint_result_data = get_gologin_fingerprint_result.get("data")
            gologin_profile_proxy_splited = gologin_profile_proxy.split(":")
            proxy_info = {}
            if len(gologin_profile_proxy_splited) == 0:
                proxy_info = {
                    "mode": "none",
                    "host": '',
                    "port": '',
                    "username": '',
                    "password": ''
                }
            elif len(gologin_profile_proxy_splited) == 2:
                proxy_info = {
                    "mode": "http",
                    "host": gologin_profile_proxy_splited[0],
                    "port": int(gologin_profile_proxy_splited[1]),
                    "username": '',
                    "password": ''
                }
            elif len(gologin_profile_proxy_splited) == 4:
                proxy_info = {
                    "mode": "http",
                    "host": gologin_profile_proxy_splited[0],
                    "port": int(gologin_profile_proxy_splited[1]),
                    "username": gologin_profile_proxy_splited[2],
                    "password": gologin_profile_proxy_splited[3]
                }
            data = {
                "name": gologin_profile_name,
                "notes": "",
                "bookmarks": {},
                "isBookmarksSynced": True,
                "autoLang": True,
                "browserType": "chrome",
                "os": gologin_profile_os,
                "devicePixelRatio": 1,
                "startUrl": "",
                "googleServicesEnabled": False,
                "lockEnabled": False,
                "debugMode": False,
                "navigator": get_gologin_fingerprint_result_data.get("navigator"),
                "geoProxyInfo": {},
                "storage": {
                    "local": True,
                    "extensions": True,
                    "bookmarks": True,
                    "history": True,
                    "passwords": True,
                    "session": True,
                    "indexedDb": False,
                },
                "proxyEnabled": True,
                "proxy": proxy_info,
                "dns": "",
                "plugins": {
                    "enableVulnerable": True,
                    "enableFlash": True,
                },
                "timezone": {
                    "enabled": True,
                    "fillBasedOnIp": True,
                    "timezone": "",
                },
                "geolocation": {
                    "mode": "prompt",
                    "enabled": True,
                    "customize": True,
                    "fillBasedOnIp": True,
                },
                "audioContext": {
                    "mode": "noise",
                },
                "canvas": {
                    "mode": "noise",
                },
                "fonts": {
                    "families": get_gologin_fingerprint_result_data.get("fonts"),
                    "enableMasking": True,
                    "enableDomRect": True,
                },
                "mediaDevices": {
                    "videoInputs": 1,
                    "audioInputs": 1,
                    "audioOutputs": 1,
                    "enableMasking": True,
                },
                "webRTC": {
                    "mode": "alerted",
                    "enabled": True,
                    "customize": True,
                    "localIpMasking": True,
                    "fillBasedOnIp": True,
                    "publicIp": "",
                    "localIps": [],
                },
                "webGL": {
                    "mode": "off",
                },
                "clientRects": {
                    "mode": "noise",
                },
                "webGLMetadata": get_gologin_fingerprint_result_data.get("webGlMetadata"),
                "extensions": {
                    "enabled": True,
                    "preloadCustom": True,
                    "names": [],
                },
                "chromeExtensions": [],
                "chromeExtensionsToAllProfiles": [],
                "userChromeExtensions": [],
                "folders": ["Tool Reg"],
                "webglParams": get_gologin_fingerprint_result_data.get("webglParams"),
            }

            try:
                response = requests.post("https://api.gologin.com/browser", json=data, headers={
                    "Authorization": f"Bearer {go_login_token}",
                    "Content-type": "application/json",
                })
                if response.status_code == 200 or response.status_code == 201:
                    return {
                        "error": None,
                        "data": {
                            "goLoginId": response.json().get("id")
                        }
                    }
                else:
                    return {
                        "error": f'requests.post("https://api.gologin.com/browser") returns status code {response.status_code} with reason {response.reason}'
                    }
            except Exception as error:
                return {"error": str(error)}
        else:
            return {"error": str(get_gologin_fingerprint_result_error)}
    except Exception as error:
        return {"error": str(error)}


# GOOGLE SHEET FUNCTIONS
def get_google_sheet_cell_background_color(ranges) -> dict:
    """.. function:: get_google_sheet_cell_background_color(ranges) -> dict

    Retrieve the background color of a Google Sheet cell.

    :param ranges: A string specifying the cell range.
    :type ranges: str
    :return: A dictionary containing the RGB color values of the cell's background.
    :rtype: dict

    This function retrieves the background color of a specified cell or range of cells in a Google Sheet. It uses the Google Sheets API to access the spreadsheet and retrieve the necessary information.

    The background color of the specified cell is obtained by sending a GET request to the Google Sheets API with the specified spreadsheet ID, ranges, and includeGridData parameter set to True. The response from the API call is then parsed to extract the background color value of the cell.

    The extracted background color value is returned as a dictionary containing the RGB color values.

    Example Usage::

        background_color = get_google_sheet_cell_background_color('A1:A1')
        print(background_color)  # Output: {'red': 1.0, 'green': 0.0, 'blue': 0.0}
"""
    response = serviceSpreadSheet.get(
        spreadsheetId=WC_WEEKEND_TEAM_SHEET_ID,
        ranges=ranges,
        includeGridData=True
    ).execute()
    color_background_value = \
        response["sheets"][0]["data"][0]["rowData"][0]["values"][0]["effectiveFormat"][
            "backgroundColorStyle"]["rgbColor"]
    return color_background_value


def get_google_sheet_ranges_values(ranges):
    """.. function:: get_google_sheet_ranges_values(ranges) -> list

    Retrieve the values from specified ranges in a Google Sheet.

    :param ranges: A string specifying the cell range.
    :type ranges: str
    :return: A list containing the values from the specified ranges in the Google Sheet.
    :rtype: list

    This function retrieves the values from the specified ranges in a Google Sheet. It utilizes the Google Sheets API to access the spreadsheet and retrieve the required values.

    The values from the specified ranges are obtained by sending a GET request to the Google Sheets API with the specified spreadsheet ID and range parameter. The response from the API call is then parsed to extract the values from the specified ranges.

    If no values are found in the specified ranges, an empty list is returned.

    Example Usage::

        values = get_google_sheet_ranges_values('Sheet1!A1:B2')
        print(values)  # Output: [['Value A1', 'Value B1'], ['Value A2', 'Value B2']]
"""
    return serviceSpreadSheet.values().get(
        spreadsheetId=WC_WEEKEND_TEAM_SHEET_ID,
        range=ranges
    ).execute().get('values', [])


def update_google_sheet_cell_by_range(cell_range, text_value):
    """.. function:: update_google_sheet_cell_by_range(sheet_range, text_value)

    Update a cell in a Google Sheet with the specified text value.

    :param cell_range: A string specifying the cell range to update.
    :type cell_range: str
    :param text_value: The text value to set in the specified cell.
    :type text_value: str
    :return: None

    This function updates a cell in a Google Sheet with the specified text value. It uses the Google Sheets API to access the spreadsheet and update the cell.

    The cell specified by the `sheet_range` parameter is updated with the provided `text_value`. The update operation is performed by sending a `values().update` request to the Google Sheets API with the specified spreadsheet ID, range, valueInputOption set to 'RAW', and the body containing the new value.

    Example Usage::

        update_google_sheet_cell_by_range('Sheet1!A1', 'New Value')
"""
    serviceSpreadSheet.values().update(
        spreadsheetId=WC_WEEKEND_TEAM_SHEET_ID,
        range=cell_range,
        valueInputOption='RAW',
        body={'values': [[text_value]]}
    ).execute()


def batch_update_google_sheet_range(body):
    """.. function:: batch_update_google_sheet_range(body)

    Batch update multiple ranges in a Google Sheet.

    :param body: A dictionary containing the request body for batch update.
    :type body: dict
    :return: None

    This function performs a batch update on multiple ranges in a Google Sheet. It uses the Google Sheets API to access the spreadsheet and update the specified ranges.

    The `body` parameter contains the request body for the batch update operation. This body should adhere to the structure specified by the Google Sheets API documentation for batch updates.

    The batch update operation is executed by sending a `values().batchUpdate` request to the Google Sheets API with the specified spreadsheet ID and the provided request body.

    Example Usage::

        request_body = {
            "valueInputOption": "RAW",
            "data": [
                {
                    "range": "Sheet1!A1:B2",
                    "values": [
                        ["Value A1", "Value B1"],
                        ["Value A2", "Value B2"]
                    ]
                },
                {
                    "range": "Sheet1!C1:D2",
                    "values": [
                        ["Value C1", "Value D1"],
                        ["Value C2", "Value D2"]
                    ]
                }
            ]
        }

        batch_update_google_sheet_range(request_body)
"""
    serviceSpreadSheet.values().batchUpdate(spreadsheetId=WC_WEEKEND_TEAM_SHEET_ID, body=body).execute()


def check_if_raw_proxy_ip_is_duplicate(ip_sheet_row_index):
    color_background_value_in_e_cell = get_google_sheet_cell_background_color(
        f"{IP_SHEET_NAME}!E{ip_sheet_row_index}")
    return color_background_value_in_e_cell.get("red", 0) != 1 or \
        color_background_value_in_e_cell.get("green", 0) != 1 or \
        color_background_value_in_e_cell.get("blue", 0) != 1


# END GOOGLE SHEET FUNCTIONS

# UTILITY
def get_verification_code(username, password):
    """
    Retrieve verification code from the weightloss123.xyz API using provided username and password.

    :param username: The username for authentication.
    :type username: str
    :param password: The password for authentication.
    :type password: str
    :return: The verification code retrieved from the API, or None if an error occurs.
    :rtype: str or None
    """
    try:
        url = "https://api.weightloss123.xyz/getEmail"
        request_data = json.dumps({
            "username": username,
            "password": password
        })
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=request_data)
        response.raise_for_status()
        response_data = response.json()
        verification_code = response_data.get('code')
        return verification_code
    except requests.exceptions.RequestException as e:
        print("Error making request:", e)
        return None


def generate_random_string(length):
    """
    Generate a random string of specified length using ASCII letters, digits, and punctuation.

    :param length: The length of the random string to generate.
    :type length: int
    :return: The randomly generated string.
    :rtype: str
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


def get_real_proxy_ip(proxy_ip, max_retries=3, retry_delay=1):
    """
    Get the real IP address for a proxy.

    :param proxy_ip: The proxy IP address.
    :type proxy_ip: str
    :param max_retries: Maximum number of retries in case of failure. Default is 3.
    :type max_retries: int
    :param retry_delay: Delay between retries (in seconds). Default is 1.
    :type retry_delay: int

    :return: The real IP address or None if not successful.
    :rtype: str or None
    """
    for _ in range(max_retries):
        try:
            response = requests.get("https://api.ipify.org?format=json", proxies={'http': proxy_ip, 'https': proxy_ip})
            if response.status_code == 200:
                return response.json().get('ip')
        except requests.RequestException as e:
            print(f"Error occurred while fetching real IP for proxy {proxy_ip}: {e}")
        time.sleep(retry_delay)
    return None


def get_ip_of_raw_proxy(raw_proxy):
    """
    Get the real IP address of a proxy from its raw representation.

    :param raw_proxy: Raw proxy string.
    :type raw_proxy: str
    :return: Real IP address of the proxy.
    :rtype: str or None
    """
    real_proxy_ip = None
    proxy_info = raw_proxy.split(':')

    if len(proxy_info) in (2, 4):
        proxy_ip = f'{proxy_info[0]}:{proxy_info[1]}'
        if len(proxy_info) == 4:
            proxy_ip = f'{proxy_info[2]}:{proxy_info[3]}@{proxy_ip}'
        proxy_ip = f'http://{proxy_ip}'
        real_proxy_ip = get_real_proxy_ip(proxy_ip)

    return real_proxy_ip


# END UTILITY

# GOLOGIN FUNCTIONS

def get_gologin_fingerprint(go_login_token: str, gologin_profile_os: str = "win") -> dict:
    """
    Get browser fingerprint data from GoLogin API.

    :param go_login_token: GoLogin API token.
    :type go_login_token: str
    :param gologin_profile_os: Operating system of the GoLogin profile. Default is 'win'.
    :type gologin_profile_os: str

    :return: Dictionary containing browser fingerprint data.
    :rtype: dict
    """
    try:
        url = f"https://api.gologin.com/browser/fingerprint?os={gologin_profile_os}"
        headers = {
            "Authorization": f"Bearer {go_login_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        navigator_data = data.get("navigator", {})
        webgl_metadata = data.get("webGLMetadata", {})

        return {
            "error": None,
            "data": {
                "navigator": {
                    "userAgent": navigator_data.get("userAgent", ""),
                    "resolution": navigator_data.get("resolution", ""),
                    "language": navigator_data.get("language", ""),
                    "platform": navigator_data.get("platform", ""),
                    "hardwareConcurrency": navigator_data.get("hardwareConcurrency", ""),
                    "deviceMemory": navigator_data.get("deviceMemory", ""),
                    "maxTouchPoints": navigator_data.get("maxTouchPoints", ""),
                },
                "webglParams": data.get("webglParams", ""),
                "webGlMetadata": {
                    "vendor": webgl_metadata.get("vendor", ""),
                    "renderer": webgl_metadata.get("renderer", ""),
                },
                "fonts": data.get("fonts", ""),
            }
        }
    except requests.exceptions.RequestException as error:
        return {"error": str(error)}


def get_gologin_profiles(go_login_token: str):
    """
    Get GoLogin profiles using the provided GoLogin API token.

    :param go_login_token: GoLogin API token.
    :type go_login_token: str
    :return: Dictionary containing the list of GoLogin profiles or error message.
    :rtype: dict
    """
    url = "https://api.gologin.com/browser/v2"
    headers = {'Authorization': f'Bearer {go_login_token}', 'Content-Type': 'application/json'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        profiles = data.get("profiles", [])
        return {"error": None, "profiles": profiles}
    except requests.exceptions.RequestException as error:
        return {"error": str(error)}


# END GOLOGIN FUNCTIONS


def reconnect_driver_to_debug_address(driver, debug_address: str):
    pass


def find_element_with_timeout(driver, timeout, by, value, condition):
    """
    Tìm một phần tử trong tối đa 'timeout' giây với điều kiện nhất định.

    Args:
    - driver: WebDriver object của Selenium.
    - timeout: Thời gian chờ tối đa (giây).
    - by: Phương pháp tìm kiếm (ví dụ: By.ID, By.CLASS_NAME, By.XPATH,...).
    - value: Giá trị để tìm kiếm (ví dụ: id, class name, xpath,...).
    - condition: Điều kiện tìm kiếm (ví dụ: ec.presence_of_element_located, ec.visibility_of_element_located,...).

    Returns:
    - WebElement object nếu tìm thấy phần tử, None nếu không tìm thấy.
    """
    element = None
    try:
        element = WebDriverWait(driver, timeout).until(condition((by, value)))
    except TimeoutException:
        pass
    return element


def wait_url_contains_any(driver, target_str_list, timeout=60):
    try:
        WebDriverWait(driver, timeout).until(
            lambda driver: any(target_str in driver.current_url for target_str in target_str_list)
        )
        return True  # Trả về True nếu URL chứa bất kỳ chuỗi nào trong danh sách mục tiêu
    except TimeoutException:
        print(f"Timeout: URL did not contain any of the target strings within {timeout} seconds.")
        return False  # Trả về False nếu timeout xảy ra


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
    options.add_experimental_option("debuggerAddress", debugger_address)
    driver_service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=driver_service, options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver


class IPHandleInGoogleSheetThread(QThread):
    pass


class GoLoginProfileCreateThread(QThread):
    """
    A thread for creating GoLogin profiles.

    Signals:
        gologin_profile_created_signal: Signal emitted when a GoLogin profile is created.
        gologin_profile_created_update_result_signal: Signal emitted to update the result of GoLogin profile creation.
        gologin_profile_driver_created_signal: Signal emitted when the driver for the GoLogin profile is created.
    """

    gologin_profile_created_signal = Signal(dict)
    gologin_profile_created_update_result_signal = Signal(dict)
    gologin_profile_driver_created_signal = Signal(dict)

    def __init__(self, gologin_profile_in_table_data, parent=None):
        """
        Initialize the GoLoginProfileCreateThread.

        :param gologin_profile_in_table_data: Data of the GoLogin profile.
        :type gologin_profile_in_table_data: tuple
        :param parent: Parent widget.
        :type parent: QWidget
        """
        super().__init__(parent)
        self.gologin_profile_in_table_data = gologin_profile_in_table_data

    def run(self):
        """
        Run the thread to create a GoLogin profile and set up the Selenium driver.
        """
        profile_table_row_index, profile_table_gologin_data = self.gologin_profile_in_table_data
        try:
            create_gologin_profile_result = create_gologin_profile({
                'goLoginToken': profile_table_gologin_data.get("goLoginToken"),
                'name': profile_table_gologin_data.get("name"),
                'os': 'mac',
                'proxy': profile_table_gologin_data.get("proxy"),
            })
            create_gologin_profile_result_error = create_gologin_profile_result.get("error")
            if create_gologin_profile_result_error:
                self.gologin_profile_created_signal.emit({
                    "error": create_gologin_profile_result_error,
                    "created_gologin_id": None,
                    "profile_table_row_index": profile_table_row_index
                })
                self.gologin_profile_created_update_result_signal.emit({
                    "error": True,
                    "message": f"An error occurred while creating profile: {create_gologin_profile_result_error}",
                    "profile_table_row_index": profile_table_row_index
                })
            else:
                created_gologin_id = create_gologin_profile_result.get("data").get("goLoginId")
                self.gologin_profile_created_signal.emit({
                    "error": None,
                    "created_gologin_id": created_gologin_id,
                    "profile_table_row_index": profile_table_row_index
                })
                self.gologin_profile_created_update_result_signal.emit({
                    "error": None,
                    "message": f"Successfully created GoLogin Profile with ID {created_gologin_id}",
                    "profile_table_row_index": profile_table_row_index
                })
                gl = GoLogin({
                    "token": profile_table_gologin_data["goLoginToken"],
                    "profile_id": created_gologin_id,
                    "port": random.randint(3500, 7000)
                })
                chrome_driver_path = "./mac_chromedriver/chromedriver" if platform == "darwin" else "./win_chromedriver/chromedriver.exe"
                gologin_profile_debugger_address = gl.start()
                driver = setup_selenium_driver(gologin_profile_debugger_address, chrome_driver_path)
                self.gologin_profile_created_update_result_signal.emit({
                    "error": None,
                    "message": f"Successfully connected to the GoLogin Profile with ID {created_gologin_id}",
                    "profile_table_row_index": profile_table_row_index
                })
                self.gologin_profile_driver_created_signal.emit({
                    "error": None,
                    "data": {
                        "profile_table_row_index": profile_table_row_index,
                        "driver_created": driver
                    }
                })
        except Exception as error:
            self.gologin_profile_created_update_result_signal.emit({
                "error": True,
                "message": f"An error occurred while creating profile: {str(error)}",
                "profile_table_row_index": profile_table_row_index
            })
            self.gologin_profile_created_signal.emit({
                "error": str(error),
                "profile_table_row_index": profile_table_row_index,
                "created_gologin_id": None
            })


class GoLoginDriverHandleThread(QThread):
    go_login_continue_create_profile_update_result_signal = Signal(dict)

    def __init__(self, gologin_continue_create_profile_data, parent=None):
        super().__init__(parent)
        self.profile_table_row_index, self.driver, self.whatcom_info = gologin_continue_create_profile_data

    def update_result_to_profile_table(self, message_data_with_error):
        self.go_login_continue_create_profile_update_result_signal.emit({
            **message_data_with_error,
            "profile_table_row_index": self.profile_table_row_index
        })

    def run(self):
        try:
            # def check_current_driver_state():
            def check_if_current_is_finding_whatcom_job():
                print('check_if_current_is_finding_whatcom_job')
                whatcom_element = find_element_with_timeout(self.driver, 10, By.XPATH, "//h4[text()='Whatcom']",
                                                            ec.presence_of_element_located)
                if whatcom_element:
                    return "FINDING_WHATCOM_JOB"
                return None

            def check_if_current_is_apply_whatcom_job():
                print('check_if_current_is_apply_whatcom_job')
                apply_button = find_element_with_timeout(self.driver, 10, By.XPATH, "//button/div[text()='Apply']",
                                                         ec.presence_of_element_located)
                if apply_button:
                    return "APPLYING_WHATCOM_JOB"
                return None

            def check_if_current_is_intelligent_attributes():
                print('check_if_current_is_intelligent_attributes')
                if wait_url_contains_any(self.driver,
                                         ["https://connect.appen.com/qrp/core/vendors/intelligent_attributes"]):
                    attributes0_element = find_element_with_timeout(self.driver, 10, By.ID, "attributes0",
                                                                    ec.presence_of_element_located)
                    if attributes0_element:
                        return "INTELLIGENT_ATTRIBUTES"
                return None

            def check_if_current_is_exam():
                print('check_if_current_is_exam')
                if wait_url_contains_any(self.driver,
                                         [
                                             "https://connect.appen.com/qrp/core/vendors"
                                             "/language_certification_quiz/view"]):
                    audio_element = find_element_with_timeout(self.driver, 10, By.XPATH,
                                                              "//audio[@controls and source[contains(@src, "
                                                              "'prompt')]]",
                                                              ec.presence_of_element_located)
                    if audio_element:
                        return "EXAM"
                return None

            def check_if_current_is_esign():
                print('check_if_current_is_esign')
                if wait_url_contains_any(self.driver, ["https://connect.appen.com/qrp/core/vendors/esign/view"
                                                       "/microsoft_vendor_code_of_conduct/",
                                                       "https://connect.appen.com/qrp/core/vendors/esign/view"
                                                       "/microsoft_nda/",
                                                       "https://connect.appen.com/qrp/core/vendors/esign/view"
                                                       "/uhrs_judge_data_consent_2023"]):
                    checkbox_agree_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                       "input[id='checkboxAgree'][value='true']",
                                                                       ec.element_to_be_clickable)
                    sign_input_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                   "input[name='sign']",
                                                                   ec.element_to_be_clickable)
                    if checkbox_agree_element is not None and sign_input_element is not None:
                        return "ESIGN"
                return None

            def check_if_current_is_done():
                print("checking_if_current_is_done")
                process_status_header_element = find_element_with_timeout(self.driver, 10, By.XPATH,
                                                                          "//span[text()='Process Status']",
                                                                          ec.presence_of_element_located)
                if process_status_header_element is not None:
                    return "DONE"
                return None

            def do_intelligent_attributes():
                username_hotmail = self.whatcom_info["email|password"].split("|")[0]
                password_hotmail = self.whatcom_info["email|password"].split("|")[1]

                # Lấy element có ID attributes0, nhập giá trị vào
                attributes0_element = find_element_with_timeout(self.driver, 10, By.ID, "attributes0",
                                                                ec.presence_of_element_located)
                if attributes0_element:
                    for character in username_hotmail:
                        attributes0_element.send_keys(character)
                        time.sleep(random.uniform(0, 0.5))
                else:
                    self.update_result_to_profile_table(
                        {"error": True, "message": f"Không tìm thấy attributes0_element"})
                    return

                # Lấy element có ID attributes0_button, click
                attributes0_button_element = find_element_with_timeout(self.driver, 10, By.ID, "attributes0_button",
                                                                       ec.element_to_be_clickable)
                if attributes0_button_element:
                    attributes0_button_element.click()
                else:
                    self.update_result_to_profile_table(
                        {"error": True, "message": f"Không tìm thấy attributes0_button_element"})
                    return

                time.sleep(5)

                ok_button_element = find_element_with_timeout(self.driver, 10, By.XPATH,
                                                              "//div[@aria-describedby='email-verification']//button[text()='OK']",
                                                              ec.element_to_be_clickable)
                if ok_button_element:
                    ok_button_element.click()
                else:
                    self.update_result_to_profile_table({"error": True, "message": f"Không tìm thấy ok_button_element"})
                    return

                code_hotmail = None
                for _ in range(5):
                    temp_code = get_verification_code(username_hotmail, password_hotmail)
                    if temp_code is not None:
                        code_hotmail = temp_code
                        break
                    else:
                        time.sleep(5)

                if code_hotmail is not None:
                    verificationCodes0_element = find_element_with_timeout(self.driver, 10, By.ID, "verificationCodes0",
                                                                           ec.presence_of_element_located)
                    if verificationCodes0_element:
                        for char in str(code_hotmail):
                            verificationCodes0_element.send_keys(char)
                            time.sleep(random.uniform(0, 0.5))
                    else:
                        self.update_result_to_profile_table(
                            {"error": True, "message": f"Không tìm thấy verificationCodes0_element"})
                        return

                    time.sleep(2)

                    attributes1_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                    "input[name='attributes[1].stringValue'][value='true']",
                                                                    ec.element_to_be_clickable)
                    if attributes1_element:
                        attributes1_element.click()
                    else:
                        self.update_result_to_profile_table(
                            {error: True, "message": f"Không tìm thấy attributes1_element"})
                        return

                    time.sleep(2)

                    attributes2_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                    "select[name='attributes[2].stringValue']",
                                                                    ec.presence_of_element_located)
                    if attributes2_element:
                        options2 = attributes2_element.find_elements(By.TAG_NAME, "option")
                        options2[random.choice([1, 2])].click()
                    else:
                        self.update_result_to_profile_table(
                            {error: True, "message": f"Không tìm thấy attributes2_element"})
                        return

                    time.sleep(2)

                    # Tiếp tục các thao tác tiếp theo sau khi B được xử lý
                    # Click vào element có name attributes[1].stringValue, value = true
                    attributes3_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                    "select[name='attributes[3].stringValue']",
                                                                    ec.presence_of_element_located)
                    if attributes3_element:
                        options3 = attributes3_element.find_elements(By.TAG_NAME, "option")
                        for option3 in options3:
                            if option3.text == "iOS":
                                option3.click()
                    else:
                        self.update_result_to_profile_table({"error": True,
                                                             "message": f"Không tìm thấy attributes3_element"})
                        return

                    # Tiếp tục các thao tác tiếp theo sau khi B được xử lý
                    # Trong element select có name attributes[2].stringValue, chọn option random trong 3 option cuối
                    attributes4_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                    "select[name='attributes[4].stringValue']",
                                                                    ec.presence_of_element_located)
                    if attributes4_element:
                        options4 = attributes4_element.find_elements(By.TAG_NAME, "option")
                        random_option_index4 = random.randint(len(options4) - 3, len(options4) - 1)
                        options4[random_option_index4].click()
                    else:
                        self.update_result_to_profile_table({"error": True,
                                                             "message": f"Không tìm thấy attributes4_element"})
                        return

                    time.sleep(2)

                    attributes5_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                    "select[name='attributes[5].stringValue']",
                                                                    ec.presence_of_element_located)
                    if attributes5_element:
                        options5 = attributes5_element.find_elements(By.TAG_NAME, "option")
                        random_option_index5 = random.randint(len(options5) - 6, len(options5) - 1)
                        options5[random_option_index5].click()
                    else:
                        self.update_result_to_profile_table({"error": True,
                                                             "message": f"Không tìm thấy attributes5_element"})
                        return

                    time.sleep(2)

                    attributes6_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                    "input[name='attributes[6].stringValue']["
                                                                    "value='true']",
                                                                    ec.element_to_be_clickable)
                    if attributes6_element:
                        attributes6_element.click()
                    else:
                        self.update_result_to_profile_table({"error": True,
                                                             "message": f"Không tìm thấy attributes6_element"})
                        return

                    time.sleep(2)

                    attributes7_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                    "input[name='attributes[7].stringValue'][value='true']",
                                                                    ec.element_to_be_clickable)
                    if attributes7_element:
                        attributes7_element.click()
                    else:
                        self.update_result_to_profile_table({"error": True,
                                                             "message": f"Không tìm thấy attributes7_element"})
                        return

                    time.sleep(2)

                    attributes8_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                    "input[name='attributes[8].stringValue'][value='true']",
                                                                    ec.element_to_be_clickable)
                    if attributes8_element:
                        attributes8_element.click()
                    else:
                        self.update_result_to_profile_table(
                            {"error": True, "message": f"Không tìm thấy attributes8_element"})
                        return

                    time.sleep(2)

                    attributes9_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                    "input[name='attributes[9].stringValue']",
                                                                    ec.presence_of_element_located)
                    if attributes9_element:
                        random_see_company = random.choice(SEE_COMPANY_LIST)
                        for char in random_see_company:
                            attributes9_element.send_keys(char)
                            time.sleep(random.uniform(0, 0.5))
                    else:
                        self.update_result_to_profile_table({"error": True,
                                                             "message": f"Không tìm thấy attributes9_element"})
                        return

                    time.sleep(2)

                    attributes10_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                     "select[name='attributes[10].stringValue']",
                                                                     ec.presence_of_element_located)
                    if attributes10_element:
                        options10 = attributes10_element.find_elements(By.TAG_NAME, "option")
                        options10[-1].click()
                    else:
                        self.update_result_to_profile_table({"error": True,
                                                             "message": f"Không tìm thấy attributes10_element"})
                        return

                    time.sleep(2)

                    attributes11_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                     "input[name='attributes[11].stringValue'][value='true']",
                                                                     ec.element_to_be_clickable)
                    if attributes11_element:
                        attributes11_element.click()
                    else:
                        self.update_result_to_profile_table({"error": True,
                                                             "message": f"Không tìm thấy attributes11_element"})
                        return

                    time.sleep(2)

                    attributes12_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                     "input[name='attributes[12].stringValue']["
                                                                     "value='true']",
                                                                     ec.element_to_be_clickable)
                    if attributes12_element:
                        attributes12_element.click()
                    else:
                        self.update_result_to_profile_table(
                            {"error": True, "message": f"Không tìm thấy attributes12_element"})
                        return

                    time.sleep(2)

                    save_button = find_element_with_timeout(self.driver, 10, By.ID, "save", ec.element_to_be_clickable)
                    if save_button:
                        save_button.click()
                    else:
                        self.update_result_to_profile_table({"error": True,
                                                             "message": f"Không tìm thấy save_button"})
                        return
                else:
                    self.update_result_to_profile_table({"error": True,
                                                         "message": f"Không nhận được code Hotmail"})
                    return

            def do_exam():
                audio_element = find_element_with_timeout(self.driver, 10, By.XPATH,
                                                          "//audio[@controls and source[contains(@src, 'prompt')]]",
                                                          ec.presence_of_element_located)

                self.driver.execute_script("arguments[0].play();", audio_element)

                src_value = self.driver.execute_script(
                    "return arguments[0].querySelector('source').getAttribute('src');", audio_element)

                prompt_number = src_value.split("prompt")[1].split(".")[0]
                time.sleep(2)

                textarea_element = find_element_with_timeout(self.driver, 10, By.TAG_NAME, "textarea",
                                                             ec.element_to_be_clickable)
                if not textarea_element:
                    self.update_result_to_profile_table({"error": True,
                                                         "message": f"Không tìm thấy textarea_element"})
                    return

                textarea_element.clear()
                for character in PROMPT_TEXT_MAP[prompt_number]:
                    textarea_element.send_keys(character)
                    time.sleep(random.uniform(0, 0.5))

                time.sleep(2)

                # Click vào button submitresponse
                submit_button = find_element_with_timeout(self.driver, 10, By.XPATH, "//input[@name='submitResponse']",
                                                          ec.element_to_be_clickable)
                if not submit_button:
                    self.update_result_to_profile_table({"error": True,
                                                         "message": f"Không tìm thấy submit_button"})
                    return

                submit_button.click()

            def do_esign():
                checkbox_agree_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR,
                                                                   "input[id='checkboxAgree'][value='true']",
                                                                   ec.element_to_be_clickable)
                checkbox_agree_element.click()
                time.sleep(2)

                sign_input_element = find_element_with_timeout(self.driver, 10, By.CSS_SELECTOR, "input[name='sign']",
                                                               ec.element_to_be_clickable)
                sign_input_element.click()
                time.sleep(2)

            def do_find_whatcom_job():
                whatcom_element = find_element_with_timeout(self.driver, 10, By.XPATH, "//h4[text()='Whatcom']"
                                                            , ec.element_to_be_clickable)
                if whatcom_element:
                    whatcom_element.click()

            def do_apply_whatcom_job():
                apply_button = find_element_with_timeout(self.driver, 10, By.XPATH, "//button/div[text()='Apply']"
                                                         , ec.element_to_be_clickable)
                if apply_button:
                    apply_button.click()
                    time.sleep(10)
                    self.driver.get("https://connect.appen.com/qrp/core/vendors/workflows/view")

            def do_done():
                self.update_result_to_profile_table({
                    "error": None,
                    "message": f"Apply thành công"})

            self.update_result_to_profile_table({"error": None,
                                                 "message": "Đang tìm Job Whatcom"})
            # self.driver.get("https://contributor.appen.com/available-projects")
            self.driver.get("file:///Users/hoangduyphuc/Downloads/test_whatcom_project_local_selenium/Contributor"
                            "%20Experience.html")
            # while True:
            self.update_result_to_profile_table({"error": None,
                                                 "message": "Đang tìm trạng thái hiện tại"})

            def check_current_state():
                print('check_current_state')

                # Khởi tạo danh sách các hàm kiểm tra
                check_functions = [
                    check_if_current_is_finding_whatcom_job,
                    check_if_current_is_apply_whatcom_job,
                    check_if_current_is_intelligent_attributes,
                    check_if_current_is_exam,
                    check_if_current_is_esign,
                    check_if_current_is_done
                ]

                # Sử dụng ThreadPoolExecutor để chạy các hàm kiểm tra song song
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    # Bắt đầu các hàm kiểm tra và thu thập kết quả
                    results = executor.map(lambda f: f(), check_functions)

                # Trả về kết quả đầu tiên khác None
                # for future in concurrent.futures.as_completed(results):

                for result in concurrent.futures.as_completed(results):
                    print(f'check_current_state: {result.result()}')
                    if result is not None:
                        print(f'check_current_state: {result}, time: {datetime.datetime.now()}')
                        return result

                return None

            current_state = check_current_state()
            if current_state is not None:
                time.sleep(10)
                check_current_state()
            else:
                print("None detect!")


            # def checking():
            #     print('checking...')
            #     with concurrent.futures.ThreadPoolExecutor() as executor:
            #         tasks = [
            #             executor.submit(check_if_current_is_finding_whatcom_job),
            #             executor.submit(check_if_current_is_apply_whatcom_job),
            #             executor.submit(check_if_current_is_intelligent_attributes),
            #             executor.submit(check_if_current_is_exam),
            #             executor.submit(check_if_current_is_esign),
            #             executor.submit(check_if_current_is_done),
            #         ]
            #         for future in concurrent.futures.as_completed(tasks):
            #             result = future.result()
            #             if result is not None:
            #                 print(f'result = {result}, time: {datetime.datetime.now()}')
            #                 self.update_result_to_profile_table({"error": None, "message": f"Trạng thái hiện tại: {result}"})
            #                 executor.shutdown(wait=False)
            #                 # Gọi lại hàm checking() để tiếp tục kiểm tra
            #                 time.sleep(10)
            #                 return checking()
            #         self.update_result_to_profile_table({"error": None, "message": f"Trạng thái hiện tại: None"})
            #
            # checking()

            # print(f'done with, time: {datetime.datetime.now()}')

            # current_state = check_current_driver_state()
            # if current_state is not None:
            #     self.update_result_to_profile_table({"error": None,
            #                                          "message": f"Trạng thái hiện tại: {current_state}"})
            #     if current_state == "FINDING_WHATCOM_JOB":
            #         do_find_whatcom_job()
            #     elif current_state == "APPLYING_WHATCOM_JOB":
            #         do_apply_whatcom_job()
            #     elif current_state == "INTELLIGENT_ATTRIBUTES":
            #         do_intelligent_attributes()
            #     elif current_state == "EXAM":
            #         do_exam()
            #     elif current_state == "ESIGN":
            #         do_esign()
            #     elif current_state == "DONE":
            #         do_done()
            #         break
            # else:
            #     self.update_result_to_profile_table({"error": None,
            #                                          "message": f"Trạng thái hiện tại: None"})
            #     break

        except Exception as error:
            self.update_result_to_profile_table({"error": True,
                                                 "message": f"Có lỗi xảy ra khi tiếp tục chạy Profile Go Login: {str(error)}"})
        # finally:
        #     # Đóng trình duyệt
        #     driver.quit()


class MainWindow(QMainWindow):
    PROFILE_TABLE_ROW_COUNT = len(PROFILE_TABLE_HEADERS)

    def __init__(self):
        super().__init__()
        # Init column header variable based on PROFILE_TABLE_HEADERS
        self.gologin_profiles = []
        for profile_table_header_index, profile_table_header_value in enumerate(PROFILE_TABLE_HEADERS):
            setattr(self, f"{profile_table_header_value.get('ID')}_COLUMN_HEADER_INDEX", profile_table_header_index)
        self.google_sheet_row_range_input = None
        self.connect_gologin_result_label = None
        self.gologin_api_key_input = None
        self.gologin_profile_create_threads = []
        self.gologin_continue_create_profile_threads = {}
        self.gologin_profile_selenium_drivers = {}
        self.profile_table = QTableWidget()
        self.setWindowTitle('Apply Whatcom')
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.create_api_key_input_layout()
        self.create_profile_table_layout()
        self.create_run_profiles_layout()
        self.fill_profile_table_with_data_from_google_sheet()

    def create_api_key_input_layout(self):
        gologin_api_key_layout = QHBoxLayout()

        self.gologin_api_key_input = QLineEdit()
        self.gologin_api_key_input.setPlaceholderText("API Key")
        self.gologin_api_key_input.setText(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
            ".eyJzdWIiOiI2NjA2YmRiM2QxM2QyZDE5ZGNjNjkwNjgiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2NjA2YmRjYzEwZTU3ZWUwZjZmOTlhNDUifQ"
            ".v-vaL0-O62BmR4LGxHNzn30UncvxzUdRRanM-FpmZiU")

        load_gologin_profiles_button = QPushButton("Load Gologin Profiles")
        load_gologin_profiles_button.clicked.connect(self.load_gologin_profiles)

        self.connect_gologin_result_label = QLabel()
        self.connect_gologin_result_label.setAlignment(Qt.AlignCenter)
        self.set_gologin_result_label("Chưa kết nối GoLogin", QColor("black"))

        self.google_sheet_row_range_input = QLineEdit()
        self.google_sheet_row_range_input.setPlaceholderText("Range Google Sheets Row")
        self.google_sheet_row_range_input.setText("1")

        get_sheet_row_range_input_button = QPushButton("Lấy data từ Sheet")
        get_sheet_row_range_input_button.clicked.connect(self.get_sheet_row_range_input)

        gologin_api_key_layout.addWidget(self.gologin_api_key_input)
        gologin_api_key_layout.addWidget(load_gologin_profiles_button)
        gologin_api_key_layout.addWidget(self.connect_gologin_result_label)
        gologin_api_key_layout.addWidget(self.google_sheet_row_range_input)
        gologin_api_key_layout.addWidget(get_sheet_row_range_input_button)

        self.main_layout.addLayout(gologin_api_key_layout)

    def create_profile_table_layout(self):
        self.profile_table.setColumnCount(self.PROFILE_TABLE_ROW_COUNT)
        self.profile_table.setHorizontalHeaderLabels(
            profile_table_header["VALUE"] for profile_table_header in PROFILE_TABLE_HEADERS)
        self.main_layout.addWidget(self.profile_table)

    def create_run_profiles_layout(self):
        run_profiles_in_profile_table_layout = QHBoxLayout()

        run_profiles_in_profile_table_button = QPushButton("Chạy")
        run_profiles_in_profile_table_button.clicked.connect(self.run_profiles_in_profile_table)

        run_profiles_in_profile_table_layout.addWidget(run_profiles_in_profile_table_button)

        self.main_layout.addLayout(run_profiles_in_profile_table_layout)

    def run_profiles_in_profile_table(self):
        self.gologin_profile_create_threads = []
        for profile_table_row_index in range(self.profile_table.rowCount()):
            select_checkbox = self.profile_table.cellWidget(profile_table_row_index,
                                                            self.SELECT_COLUMN_HEADER_INDEX)
            if select_checkbox.isChecked():
                self.process_profile(profile_table_row_index)

        for gologin_profile_create_thread in self.gologin_profile_create_threads:
            gologin_profile_create_thread.start()

    def process_profile(self, profile_table_row_index):
        raw_proxy = self.profile_table.item(profile_table_row_index, self.PROXY_COLUMN_HEADER_INDEX).text()
        # raw_proxy_after_extract = extract_proxy_info(raw_proxy)
        # if(raw_proxy_after_extract is not None):

        # handle_proxy_thread = IPHandleInGoogleSheetThread((profile_table_row_index, {
        #
        # }))
        # handle_proxy_thread.start()
        # gologin_profile_create_thread = GoLoginProfileCreateThread(
        #     (profile_table_row_index, {
        #         'goLoginToken': self.gologin_api_key_input.text(),
        #         'name': f'Windows {self.profile_table.item(profile_table_row_index, self.ACCOUNT_INDEX_COLUMN_HEADER_INDEX).text()}',
        #         'os': 'win',
        #         'proxy': raw_proxy,
        #         'emailAppen': self.profile_table.item(profile_table_row_index,
        #                                               self.MAIL_APPEN_COLUMN_HEADER_INDEX).text(),
        #         'passwordAppen': self.profile_table.item(profile_table_row_index,
        #                                                  self.PASS_APPEN_COLUMN_HEADER_INDEX).text(),
        #         "email|password": self.profile_table.item(profile_table_row_index,
        #                                                   self.HOTMAIL_PASS_COLUMN_HEADER_INDEX).text()
        #     }))
        # gologin_profile_create_thread.gologin_profile_created_signal.connect(
        #     self.update_profile_table_after_gologin_profile_created)
        # (gologin_profile_create_thread.gologin_profile_created_update_result_signal
        #  .connect(self.update_result_cell_profile_table))
        #
        # gologin_profile_create_thread.gologin_profile_driver_created_signal.connect(
        #     self.update_gologin_profile_drivers)
        # self.gologin_profile_create_threads.append(gologin_profile_create_thread)
        raw_proxy_ip = get_ip_of_raw_proxy(raw_proxy)

        if not raw_proxy_ip:
            self.handle_invalid_raw_proxy(profile_table_row_index)
            return

        self.update_raw_proxy_ip_in_profile_table(profile_table_row_index, raw_proxy_ip)
        japan_column_ip_sheet_values = get_google_sheet_ranges_values(f"{IP_SHEET_NAME}!D3:D")

        if not japan_column_ip_sheet_values:
            self.handle_no_values_in_japan_column_in_ip_sheet_error(profile_table_row_index)
            return

        for japan_column_ip_sheet_value in japan_column_ip_sheet_values:
            if japan_column_ip_sheet_value[0] == self.profile_table.item(profile_table_row_index,
                                                                         self.ACCOUNT_INDEX_COLUMN_HEADER_INDEX).text():
                ip_sheet_row_index = japan_column_ip_sheet_values.index(japan_column_ip_sheet_value) + 3
                self.update_raw_proxy_ip_to_google_sheet(raw_proxy_ip, profile_table_row_index, ip_sheet_row_index)
                raw_proxy_ip_is_duplicate = check_if_raw_proxy_ip_is_duplicate(ip_sheet_row_index)
                if raw_proxy_ip_is_duplicate:
                    self.handle_duplicate_raw_proxy_ip(profile_table_row_index)
                else:
                    self.create_gologin_profile(profile_table_row_index, raw_proxy)
                return

    def handle_duplicate_raw_proxy_ip(self, profile_table_row_index):
        duplicate_ip_message = "IP bị trùng! Bỏ qua."
        self.update_result_cell_profile_table({
            "error": True,
            "message": duplicate_ip_message,
            "profile_table_row_index": profile_table_row_index
        })
        update_google_sheet_cell_by_range(
            f"{TOOLS_SHEET_NAME}!C{self.profile_table.item(profile_table_row_index, self.STT_COLUMN_HEADER_INDEX).text()}",
            duplicate_ip_message)

    def handle_invalid_raw_proxy(self, profile_table_row_index):
        invalid_proxy_message = "Không lấy được địa chỉ IP của Proxy. Bỏ qua."
        self.update_result_cell_profile_table({
            "error": True,
            "message": invalid_proxy_message,
            "profile_table_row_index": profile_table_row_index
        })
        update_google_sheet_cell_by_range(
            f"{TOOLS_SHEET_NAME}!C{self.profile_table.item(profile_table_row_index, self.STT_COLUMN_HEADER_INDEX).text()}",
            invalid_proxy_message)

    def update_raw_proxy_ip_in_profile_table(self, profile_table_row_index, raw_proxy_ip):
        self.profile_table.setItem(profile_table_row_index, self.IP_COLUMN_HEADER_INDEX,
                                   QTableWidgetItem(raw_proxy_ip))

    def handle_no_values_in_japan_column_in_ip_sheet_error(self, profile_table_row_index):
        self.update_result_cell_profile_table({
            "error": True,
            "message": "Không tìm thấy các mã số trong cột B của bảng IP",
            "profile_table_row_index": profile_table_row_index
        })

    def update_raw_proxy_ip_to_google_sheet(self, raw_proxy_ip, profile_table_row_index, ip_sheet_row_index):
        batch_update_google_sheet_range({
            "valueInputOption": "RAW",
            "data": [
                {
                    "range": f"{IP_SHEET_NAME}!E{ip_sheet_row_index}",
                    "values": [[raw_proxy_ip]]
                },
                {
                    "range": f"{TOOLS_SHEET_NAME}!C{self.profile_table.item(profile_table_row_index, self.STT_COLUMN_HEADER_INDEX).text()}",
                    "values": [[raw_proxy_ip]]
                }
            ]
        })

    def create_gologin_profile(self, profile_table_row_index, raw_proxy):
        gologin_profile_create_thread = GoLoginProfileCreateThread(
            (profile_table_row_index, {
                'goLoginToken': self.gologin_api_key_input.text(),
                'name': f'Windows {self.profile_table.item(profile_table_row_index, self.ACCOUNT_INDEX_COLUMN_HEADER_INDEX).text()}',
                'os': 'win',
                'proxy': raw_proxy,
                'emailAppen': self.profile_table.item(profile_table_row_index,
                                                      self.MAIL_APPEN_COLUMN_HEADER_INDEX).text(),
                'passwordAppen': self.profile_table.item(profile_table_row_index,
                                                         self.PASS_APPEN_COLUMN_HEADER_INDEX).text(),
                "email|password": self.profile_table.item(profile_table_row_index,
                                                          self.HOTMAIL_PASS_COLUMN_HEADER_INDEX).text()
            }))
        gologin_profile_create_thread.gologin_profile_created_signal.connect(
            self.update_profile_table_after_gologin_profile_created)
        (gologin_profile_create_thread.gologin_profile_created_update_result_signal
         .connect(self.update_result_cell_profile_table))

        gologin_profile_create_thread.gologin_profile_driver_created_signal.connect(
            self.update_gologin_profile_drivers)
        self.gologin_profile_create_threads.append(gologin_profile_create_thread)

    def update_gologin_profile_drivers(self, driver_gologin_profile_created_data):
        self.gologin_profile_selenium_drivers[
            driver_gologin_profile_created_data.get('data').get('profile_table_row_index')] = \
            driver_gologin_profile_created_data.get('data').get('driver_created')

    # SLOTS
    def update_profile_table_after_gologin_profile_created(self, result_dict: dict):
        result_dict_error = result_dict.get("error")
        result_dict_message = result_dict.get("message")
        result_dict_profile_table_row_index = result_dict.get("profile_table_row_index")

        result_item_in_project_table = QTableWidgetItem(result_dict_message)
        if result_dict_error:
            result_item_in_project_table.setForeground(QColor("red"))
        else:
            result_item_in_project_table.setForeground(QColor("green"))

        self.profile_table.setItem(result_dict_profile_table_row_index, self.RESULT_COLUMN_HEADER_INDEX,
                                   result_item_in_project_table)
        stt_number = self.profile_table.item(result_dict_profile_table_row_index, self.STT_COLUMN_HEADER_INDEX).text()
        try:
            update_google_sheet_cell_by_range(f"{TOOLS_SHEET_NAME}!K{stt_number}", result_dict_message)
        except Exception as error:
            result_item_in_project_table.setText(
                f'Có lỗi xảy ra khi update Google Sheet với nội dung {result_dict_message}, lỗi: {str(error)}')
            result_item_in_project_table.setForeground(QColor("red"))
            self.profile_table.setItem(result_dict_profile_table_row_index, self.RESULT_COLUMN_HEADER_INDEX,
                                       result_item_in_project_table)

    def update_result_cell_profile_table(self, result_dict: dict):
        result_dict_error = result_dict.get("error")
        result_dict_message = result_dict.get("message")
        result_dict_profile_table_row_index = result_dict.get("profile_table_row_index")

        result_item_in_project_table = QTableWidgetItem(result_dict_message)
        if result_dict_error:
            result_item_in_project_table.setForeground(QColor("red"))
        else:
            result_item_in_project_table.setForeground(QColor("green"))

        self.profile_table.setItem(result_dict_profile_table_row_index, self.RESULT_COLUMN_HEADER_INDEX,
                                   result_item_in_project_table)
        stt_number = self.profile_table.item(result_dict_profile_table_row_index, self.STT_COLUMN_HEADER_INDEX).text()
        try:
            update_google_sheet_cell_by_range(f"{TOOLS_SHEET_NAME}!K{stt_number}", result_dict_message)
        except Exception as e:
            result_item_in_project_table.setText(
                f'Có lỗi xảy ra khi update Google Sheet với nội dung {result_dict_message}, lỗi: {str(e)}')
            result_item_in_project_table.setForeground(QColor("red"))
            self.profile_table.setItem(result_dict_profile_table_row_index, self.RESULT_COLUMN_HEADER_INDEX,
                                       result_item_in_project_table)

    # END SLOTS

    def fill_profile_table_with_data_from_google_sheet(self):
        values = get_google_sheet_ranges_values(f"{TOOLS_SHEET_NAME}!A2:I")
        self.fill_data_to_profile_table(values)

    def reset_gologin_profile_combobox(self):
        # self.
        pass

    def reset_profile_table(self):
        self.profile_table.setRowCount(0)

    def fill_data_to_profile_table(self, values):
        self.reset_profile_table()
        for value in values:
            profile_table_row_index = self.profile_table.rowCount()
            self.profile_table.insertRow(profile_table_row_index)
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.profile_table.setCellWidget(profile_table_row_index, self.SELECT_COLUMN_HEADER_INDEX, checkbox)
            for col, val in enumerate(value, start=1):
                item = QTableWidgetItem(val)
                self.profile_table.setItem(profile_table_row_index, col, item)
            gologin_profile_select_checkbox = QComboBox()
            gologin_profile_select_checkbox.addItem("Tạo Profile mới", 0)
            gologin_profile_select_checkbox.setCurrentIndex(0)
            for gologin_profile in self.gologin_profiles:
                gologin_profile_select_checkbox.addItem(gologin_profile.get("name"), gologin_profile.get("id"))
            self.profile_table.setCellWidget(profile_table_row_index, self.PROFILE_GOLOGIN_COLUMN_HEADER_INDEX,
                                             gologin_profile_select_checkbox)
            gologin_continue_after_manual_login_appen_btn = QPushButton("Tiếp tục")
            (gologin_continue_after_manual_login_appen_btn.clicked
             .connect(lambda checked=profile_table_row_index,
                             r=profile_table_row_index: self.continue_gologin_apply_in_driver(checked)))
            self.profile_table.setCellWidget(profile_table_row_index, self.START_GOLOGIN_COLUMN_HEADER_INDEX,
                                             gologin_continue_after_manual_login_appen_btn)
            # reload_gologin_profiles_button = QPushButton("Reload Gologin Profiles")
            # (reload_gologin_profiles_button.clicked
            #  .connect(lambda checked=profile_table_row_index,
            #                  r=profile_table_row_index: self.continue_gologin_apply_in_driver(checked)))
            # self.profile_table.setCellWidget(profile_table_row_index, self.RELOAD_GOLOGIN_PROFILES_COLUMN_HEADER_INDEX,
            #                                  reload_gologin_profiles_button)

    def get_sheet_row_range_input(self):
        input_text = self.google_sheet_row_range_input.text().strip()
        google_sheet_range = None

        if not input_text:
            google_sheet_range = f"{TOOLS_SHEET_NAME}!A2:I"
        else:
            split_range = input_text.split("-")
            if all(part.isdigit() for part in split_range):
                if len(split_range) == 1:
                    google_sheet_range = f"{TOOLS_SHEET_NAME}!A{input_text}:I{input_text}"
                elif len(split_range) == 2:
                    start, end = map(int, split_range)
                    google_sheet_range = f"{TOOLS_SHEET_NAME}!A{start}:I{end}"

        if google_sheet_range:
            values = get_google_sheet_ranges_values(google_sheet_range)
            self.fill_data_to_profile_table(values)

    def continue_gologin_apply_in_driver(self, profile_table_row_index):
        driver = self.gologin_profile_selenium_drivers[profile_table_row_index]
        random_create_profile_id = generate_random_string(5)
        go_login_continue_create_profile_thread = GoLoginDriverHandleThread((profile_table_row_index, driver, {
            "email|password": self.profile_table.item(profile_table_row_index,
                                                      self.HOTMAIL_PASS_COLUMN_HEADER_INDEX).text(),
        }))
        (go_login_continue_create_profile_thread.go_login_continue_create_profile_update_result_signal
         .connect(self.update_result_cell_profile_table))
        self.gologin_continue_create_profile_threads[random_create_profile_id] = go_login_continue_create_profile_thread
        self.gologin_continue_create_profile_threads[random_create_profile_id].start()

    def load_gologin_profiles(self):
        gologin_api_key = self.gologin_api_key_input.text().strip()
        if not gologin_api_key:
            self.set_gologin_result_label("API Key is empty", QColor("red"))
            return
        self.set_gologin_result_label("Đang kết nối Go Login...", QColor("yellow"))
        get_gologin_profiles_result = get_gologin_profiles(gologin_api_key)

        get_gologin_profiles_result_error = get_gologin_profiles_result.get("error")
        get_gologin_profiles_result_profiles = get_gologin_profiles_result.get("profiles")

        if get_gologin_profiles_result_error:
            self.gologin_profiles = []
            self.set_gologin_result_label(f"Kết nối Go Login chưa thành công, lỗi: {get_gologin_profiles_result_error}",
                                          QColor("red"))
        else:
            self.gologin_profiles = get_gologin_profiles_result_profiles
            num_profiles = len(get_gologin_profiles_result_profiles)
            self.set_gologin_result_label(f"Kết nối Go Login thành công ({num_profiles} profile)", QColor("green"))

    def set_gologin_result_label(self, text, color):
        self.connect_gologin_result_label.setText(text)
        self.connect_gologin_result_label.setStyleSheet(f"color: {color.name()};")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec())
