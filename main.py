import os.path
import sys
import time

import requests
import json
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

prompt_text_map = {
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


def create_gologin_profile(gologin_profile_options: dict) -> dict:
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
                        "error": f'requests.post("https://api.gologin.com/browser") returns status code {response.status_code}'
                    }
            except Exception as error:
                return {"error": str(error)}
        else:
            return {"error": str(get_gologin_fingerprint_result_error)}
    except Exception as error:
        return {"error": str(error)}


def get_code_from_weightloss(username, password):
    try:
        url = "https://api.weightloss123.xyz/getEmail"

        payload = json.dumps({
            "username": username,
            "password": password
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
        code = data.get('code')
        if code is not None:
            return code
    except requests.exceptions.RequestException as e:
        print("Error making request:", e)
    return None


def get_gologin_fingerprint(go_login_token: str, gologin_profile_os="win") -> dict:
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
        user_agent = navigator_data.get("userAgent", "")
        return {
            "error": None,
            "data": {
                "navigator": {
                    "userAgent": user_agent,
                    "resolution": navigator_data.get("resolution", ""),
                    "language": navigator_data.get("language", ""),
                    "platform": navigator_data.get("platform", ""),
                    "hardwareConcurrency": navigator_data.get("hardwareConcurrency", ""),
                    "deviceMemory": navigator_data.get("deviceMemory", ""),
                    "maxTouchPoints": navigator_data.get("maxTouchPoints", ""),
                },
                "webglParams": data.get("webglParams", ""),
                "webGlMetadata": {
                    "vendor": data.get("webGLMetadata", {}).get("vendor", ""),
                    "renderer": data.get("webGLMetadata", {}).get("renderer", ""),
                },
                "fonts": data.get("fonts", ""),
            }
        }
    except Exception as error:
        return {"error": str(error)}


def setup_selenium_driver(debugger_address, chrome_driver_path):
    # try:
    page_load_timeout = 120
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-notifications')
    options.add_experimental_option("debuggerAddress", debugger_address)
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(page_load_timeout)
    return driver


class IPHandleInGoogleSheetThread(QThread):
    pass


class GoLoginProfileCreateThread(QThread):
    gologin_profile_created_signal = Signal(dict)
    gologin_profile_created_update_result_signal = Signal(dict)
    gologin_profile_driver_created_signal = Signal(dict)

    def __init__(self, gologin_profile_in_table_data, parent=None):
        super().__init__(parent)
        self.gologin_profile_in_table_data = gologin_profile_in_table_data

    def run(self):
        profile_table_row_index, profile_table_gologin_data = self.gologin_profile_in_table_data
        try:
            create_gologin_profile_result = create_gologin_profile(
                {
                    'goLoginToken': profile_table_gologin_data.get("goLoginToken"),
                    'name': profile_table_gologin_data.get("name"),
                    'os': 'mac',
                    'proxy': profile_table_gologin_data.get("proxy"),
                }
            )
            create_gologin_profile_result_error = create_gologin_profile_result.get("error")
            if create_gologin_profile_result_error:
                self.gologin_profile_created_signal.emit(
                    {
                        "error": create_gologin_profile_result_error,
                        "data": {
                            "profile_table_row_index": profile_table_row_index
                        }
                    }
                )
                self.gologin_profile_created_update_result_signal.emit({
                    "error": True,
                    "message": f"Xảy ra lỗi khi tạo profile: {create_gologin_profile_result_error}",
                    "profile_table_row_index": profile_table_row_index
                })
            else:
                created_gologin_id = create_gologin_profile_result.get("data").get("goLoginId")
                self.gologin_profile_created_update_result_signal.emit({
                    "error": None,
                    "message": f"Tạo thành công Profile GoLogin với ID {created_gologin_id}",
                    "profile_table_row_index": profile_table_row_index
                })
                self.gologin_profile_created_signal.emit(
                    {
                        "error": None,
                        "data": {
                            "profile_table_row_index": profile_table_row_index,
                            "goLoginId": created_gologin_id
                        }
                    }
                )
                gl = GoLogin({
                    "token": profile_table_gologin_data["goLoginToken"],
                    "profile_id": created_gologin_id,
                    "port": random.randint(3500, 7000)
                })
                chrome_driver_path = None
                if platform == "darwin":
                    chrome_driver_path = "./mac_chromedriver/chromedriver"
                elif platform == "win32":
                    chrome_driver_path = "./win_chromedriver/chromedriver.exe"
                gologin_profile_debugger_address = gl.start()
                driver = setup_selenium_driver(gologin_profile_debugger_address, chrome_driver_path)
                self.gologin_profile_created_update_result_signal.emit({
                    "error": None,
                    "message": f"Kết nối thành công hệ thống tự động với Profile GoLogin có ID {created_gologin_id}",
                    "profile_table_row_index": profile_table_row_index
                })
                self.gologin_profile_driver_created_signal.emit(
                    {
                        "error": None,
                        "data": {
                            "profile_table_row_index": profile_table_row_index,
                            "driver_created": driver
                        }
                    }
                )
        except Exception as error:
            self.gologin_profile_created_update_result_signal.emit({
                "error": True,
                "message": f"Xảy ra lỗi khi tạo profile: {str(error)}",
                "profile_table_row_index": profile_table_row_index
            })
            self.gologin_profile_created_signal.emit(
                {
                    "error": str(error),
                    "data": {
                        "profile_table_row_index": profile_table_row_index,
                    }
                }
            )


class GoLoginContinueCreateProfileThread(QThread):
    go_login_continue_create_profile_update_result_signal = Signal(dict)

    def __init__(self, gologin_continue_create_profile_data, parent=None):
        super().__init__(parent)
        self.gologin_continue_create_profile_data = gologin_continue_create_profile_data

    def run(self):
        profile_table_row_index, driver, whatcom_info = self.gologin_continue_create_profile_data
        try:
            self.go_login_continue_create_profile_update_result_signal.emit({
                "error": None,
                "message": "Đang tìm Job Whatcom",
                "profile_table_row_index": profile_table_row_index
            })
            driver.get("https://contributor.appen.com/available-projects")

            try:
                # Tìm element có xpath //h4[text()='Whatcom'] và click
                whatcom_element = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//h4[text()='Whatcom']"))
                )
                whatcom_element.click()

                time.sleep(5)

                # Tìm element có dạng button>div[text()='Apply'] và click
                apply_element = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//button/div[text()='Apply']"))
                )
                apply_element.click()

                time.sleep(15)

            except TimeoutException as timeout:
                self.go_login_continue_create_profile_update_result_signal.emit({
                    "error": True,
                    "message": f"Không tìm thấy nút Apply Whatcom, chuyển hướng sang trang Academy",
                    "profile_table_row_index": profile_table_row_index
                })

            driver.get("https://connect.appen.com/qrp/core/vendors/workflows/view")
            try:
                WebDriverWait(driver, 30).until(EC.url_contains("https://connect.appen.com/qrp/core/vendors"
                                                                "/intelligent_attributes"))
                username_hotmail = whatcom_info["email|password"].split("|")[0]
                password_hotmail = whatcom_info["email|password"].split("|")[1]
                # Lấy element có ID attributes0, nhập giá trị vào
                attributes0_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "attributes0"))
                )
                for character in username_hotmail:
                    attributes0_element.send_keys(character)
                    time.sleep(random.uniform(0, 0.5))

                # Lấy element có ID attributes0_button, click
                attributes0_button_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "attributes0_button"))
                )
                attributes0_button_element.click()

                time.sleep(5)

                ok_button_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//div[@aria-describedby='email-verification']//button[text()='OK']"))
                )
                ok_button_element.click()

                time.sleep(5)

                code_hotmail = None
                for _ in range(5):
                    temp_code = get_code_from_weightloss(username_hotmail, password_hotmail)
                    if temp_code is not None:
                        code_hotmail = temp_code
                        break
                    else:
                        time.sleep(5)

                if code_hotmail is not None:
                    verificationCodes0_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "verificationCodes0"))
                    )
                    for char in str(code_hotmail):
                        verificationCodes0_element.send_keys(char)
                        time.sleep(random.uniform(0, 0.5))

                    time.sleep(2)

                    # Tiếp tục các thao tác tiếp theo sau khi B được xử lý
                    # Click vào element có name attributes[1].stringValue, value = true
                    attributes1_element = driver.find_element(
                        By.CSS_SELECTOR, "input[name='attributes[1].stringValue'][value='true']")
                    attributes1_element.click()
                    time.sleep(2)

                    attributes2_element = driver.find_element(
                        By.CSS_SELECTOR, "select[name='attributes[2].stringValue']"
                    )
                    options2 = attributes2_element.find_elements(By.TAG_NAME, "option")
                    options2[random.choice([1, 2])].click()

                    time.sleep(2)

                    attributes3_element = driver.find_element(
                        By.CSS_SELECTOR, "select[name='attributes[3].stringValue']"
                    )
                    options3 = attributes3_element.find_elements(By.TAG_NAME, "option")
                    for option3 in options3:
                        if option3.text == "iOS":
                            option3.click()

                    # Trong element select có name attributes[2].stringValue, chọn option random trong 3 option cuối
                    attributes4_element = driver.find_element(By.CSS_SELECTOR,
                                                              "select[name='attributes[4].stringValue']")
                    options4 = attributes4_element.find_elements(By.TAG_NAME, "option")
                    random_option_index4 = random.randint(len(options4) - 3, len(options4) - 1)
                    options4[random_option_index4].click()

                    time.sleep(2)

                    # Trong element select có name attributes[3].stringValue, chọn option random trong 6 option cuối
                    attributes5_element = driver.find_element(By.CSS_SELECTOR,
                                                              "select[name='attributes[5].stringValue']")
                    options5 = attributes5_element.find_elements(By.TAG_NAME, "option")
                    random_option_index5 = random.randint(len(options5) - 6, len(options5) - 1)
                    options5[random_option_index5].click()

                    time.sleep(2)

                    # Click vào element có name attributes[4].stringValue, value = true
                    attributes6_element = driver.find_element(
                        By.CSS_SELECTOR, "input[name='attributes[6].stringValue'][value='true']")
                    attributes6_element.click()

                    time.sleep(2)

                    # Click vào element có name attributes[5].stringValue, value = true
                    attributes7_element = driver.find_element(
                        By.CSS_SELECTOR, "input[name='attributes[7].stringValue'][value='true']")
                    attributes7_element.click()

                    time.sleep(2)

                    # Click vào element có name attributes[6].stringValue, value = true
                    attributes8_element = driver.find_element(
                        By.CSS_SELECTOR, "input[name='attributes[8].stringValue'][value='true']")
                    attributes8_element.click()
                    time.sleep(2)

                    # Nhập vào element có name attributes[7].stringValue random 1 trong các giá trị được cung cấp
                    values_list = [
                        "Lionbridge", "Leapforce", "iSoftStone", "Clickworker", "Crowdsource",
                        "Amazon Mechanical Turk (MTurk)", "OneSpace", "Upwork", "Rev", "Spare5",
                        "Scribie", "UTest", "Testbirds", "Test IO", "TranscribeMe", "Crossover",
                        "Fancy Hands", "Fancyhires"
                    ]
                    random_value = random.choice(values_list)
                    attributes9_element = driver.find_element(By.CSS_SELECTOR,
                                                              "input[name='attributes[9].stringValue']")
                    for char in random_value:
                        attributes9_element.send_keys(char)
                        time.sleep(random.uniform(0, 0.5))
                    time.sleep(2)

                    # Trong element select có name attributes[8].stringValue, chọn option 5+
                    attributes10_element = driver.find_element(By.CSS_SELECTOR,
                                                               "select[name='attributes[10].stringValue']")
                    options10 = attributes10_element.find_elements(By.TAG_NAME, "option")
                    options10[-1].click()
                    time.sleep(2)

                    # Click vào element có name attributes[9].stringValue, value = true
                    attributes11_element = driver.find_element(
                        By.CSS_SELECTOR, "input[name='attributes[11].stringValue'][value='true']")
                    attributes11_element.click()
                    time.sleep(2)

                    # Click vào element có name attributes[10].stringValue, value = true
                    attributes12_element = driver.find_element(
                        By.CSS_SELECTOR, "input[name='attributes[12].stringValue'][value='true']")
                    attributes12_element.click()
                    time.sleep(2)

                    # Click vào input có id = "save"
                    save_button = driver.find_element(By.ID, "save")
                    save_button.click()
                    time.sleep(2)

                    # esign
                    WebDriverWait(driver, 30).until(EC.url_contains("https://connect.appen.com/qrp/core/vendors/esign"
                                                                    "/view/microsoft_vendor_code_of_conduct/"))

                    # Tìm và click vào element có id = checkboxAgree và value = true
                    checkbox_agree_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[id='checkboxAgree'][value='true']"))
                    )
                    checkbox_agree_element.click()
                    time.sleep(2)

                    # Tìm và click vào element input có name = sign
                    sign_input_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='sign']"))
                    )
                    sign_input_element.click()
                    time.sleep(2)

                    # Đợi trang web load và redirect xong
                    WebDriverWait(driver, 30).until(
                        EC.url_contains("https://connect.appen.com/qrp/core/vendors/esign/view/microsoft_nda/"))

                    # Tìm và click vào element có id = checkboxAgree và value = true
                    checkbox_agree_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[id='checkboxAgree'][value='true']"))
                    )
                    checkbox_agree_element.click()
                    time.sleep(2)

                    # Tìm và click vào element input có name = sign
                    sign_input_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='sign']"))
                    )
                    sign_input_element.click()
                    time.sleep(2)

                    # Đợi trang web load và redirect xong
                    WebDriverWait(driver, 30).until(
                        EC.url_contains("https://connect.appen.com/qrp/core/vendors/esign/view"
                                        "/uhrs_judge_data_consent_2023"))

                    # Tìm và click vào element có id = checkboxAgree và value = true
                    checkbox_agree_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[id='checkboxAgree'][value='true']"))
                    )
                    checkbox_agree_element.click()
                    time.sleep(2)

                    # Tìm và click vào element input có name = sign
                    sign_input_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='sign']"))
                    )
                    sign_input_element.click()
                    time.sleep(2)

                    # vào bài thi
                    WebDriverWait(driver, 30).until(
                        EC.url_contains(
                            "https://connect.appen.com/qrp/core/vendors/language_certification_quiz/view"))

                    while True:
                        try:
                            # Lấy giá trị của number
                            audio_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//audio[@controls and source[contains(@src, 'prompt')]]"))
                            )
                            driver.execute_script("arguments[0].play();", audio_element)

                            # Execute JavaScript to get the src attribute value of the source element
                            src_value = driver.execute_script(
                                "return arguments[0].querySelector('source').getAttribute('src');", audio_element)

                            # src_attribute = audio_element.get_attribute("src")
                            prompt_number = src_value.split("prompt")[1].split(".")[0]
                            time.sleep(2)

                            # Điền giá trị của number vào textarea
                            textarea_element = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.TAG_NAME, "textarea"))
                            )
                            textarea_element.clear()
                            for character in prompt_text_map[prompt_number]:
                                textarea_element.send_keys(character)
                                time.sleep(random.uniform(0, 0.5))

                            time.sleep(2)

                            # Click vào button submitresponse
                            submit_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//input[@name='submitResponse']"))
                            )
                            submit_button.click()
                            time.sleep(8)

                        except Exception as e:
                            # TODO
                            """
                            Nếu check thay nut OK, Apply xong, 
                            danh dau la Done va update Apply thanh cong tren Google Sheet
                            """
                            process_status_header_element = driver.find_element(By.XPATH, "//span[text()='Process "
                                                                                          "Status']")
                            if process_status_header_element is not None:
                                self.go_login_continue_create_profile_update_result_signal.emit({
                                    "error": None,
                                    "message": f"Apply thành công",
                                    "profile_table_row_index": profile_table_row_index
                                })
                                # self.serviceSpreadSheet.values().update(
                                #     spreadsheetId="1uEkPu8l7XUlTIM17S_Sdn40YcvbM4xEHWuXpuf7hGNE",
                                #     range=f"Tools!K{self.profile_table.item(profile_table_row_index, 1).text()}",
                                #     valueInputOption='RAW',
                                #     body={'values': [["Apply thành công!"]]}
                                # ).execute()

                            break
                else:
                    self.go_login_continue_create_profile_update_result_signal.emit({
                        "error": True,
                        "message": f"Không nhận được code Hotmail",
                        "profile_table_row_index": profile_table_row_index
                    })
            except TimeoutException as timeout:
                self.go_login_continue_create_profile_update_result_signal.emit({
                    "error": True,
                    "message": f"Load trang Academy không thành công",
                    "profile_table_row_index": profile_table_row_index
                })
        except Exception as e:
            self.go_login_continue_create_profile_update_result_signal.emit({
                "error": True,
                "message": f"Co lỗi xảy ra khi tiếp tục chạy Profile Go Login: {str(e)}",
                "profile_table_row_index": profile_table_row_index
            })
        # finally:
        #     # Đóng trình duyệt
        #     driver.quit()


def generate_random_string(length):
    letters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(letters) for _ in range(length))


def get_real_proxy_ip(proxy_ip, max_retries=3, retry_delay=1):
    """
    Get the real IP address for a proxy.

    Args:
        proxy_ip (str): The proxy IP address.
        max_retries (int): Maximum number of retries in case of failure.
        retry_delay (int): Delay between retries (in seconds).

    Returns:
        str or None: The real IP address or None if not successful.
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.google_sheet_row_range_input = None
        self.connect_gologin_result_label = None
        self.gologin_api_key_input = None
        self.gologin_profile_create_threads = []
        self.gologin_continue_create_profile_threads = {}
        self.gologin_profile_selenium_drivers = {}
        self.serviceSpreadSheet = None
        self.profile_table = QTableWidget()
        self.google_creds = None
        self.setWindowTitle('Apply Whatcom')
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.create_api_key_input_layout()
        self.create_account_table()
        self.create_run_profiles_layout()
        self.create_creds_google()
        self.get_sheet_data_from_row()

    def create_account_table(self):
        self.profile_table.setColumnCount(13)
        self.profile_table.setHorizontalHeaderLabels(["Select", "STT", "PROXY", "IP", "PROXY SITE", "LOCAL", "MÃ SỐ",
                                                      "HOTMAIL|PASS", "MAIL APPEN", "PASS APPEN", "ACC GOLOGIN",
                                                      "Kết quả", "Bắt đầu"])
        self.main_layout.addWidget(self.profile_table)

    def create_run_profiles_layout(self):
        run_profiles_in_profile_table_layout = QHBoxLayout()

        run_profiles_in_profile_table_button = QPushButton("Chạy")
        run_profiles_in_profile_table_button.clicked.connect(self.run_profiles_in_profile_table)

        run_profiles_in_profile_table_layout.addWidget(run_profiles_in_profile_table_button)

        self.main_layout.addLayout(run_profiles_in_profile_table_layout)

    def run_profiles_in_profile_table(self):
        self.gologin_profile_create_threads = []  # List to keep track of all created threads
        self.gologin_profile_selenium_drivers = {}
        for profile_table_row_index in range(self.profile_table.rowCount()):
            select_checkbox_in_box = self.profile_table.cellWidget(profile_table_row_index, 0)
            if select_checkbox_in_box.isChecked():
                # Check Proxy before create Go Login Profile
                raw_proxy = self.profile_table.item(profile_table_row_index, 2).text()
                real_proxy_ip = None
                raw_proxy_splited = raw_proxy.split(':')

                # TODO
                # Update result in profile table: Checking IP
                if len(raw_proxy_splited) == 2:
                    proxy_ip = f'http://{raw_proxy_splited[0]}:{raw_proxy_splited[1]}'
                    real_proxy_ip = get_real_proxy_ip(proxy_ip)

                elif len(raw_proxy_splited) == 4:
                    proxy_ip = f'http://{raw_proxy_splited[2]}:{raw_proxy_splited[3]}@{raw_proxy_splited[0]}:{raw_proxy_splited[1]}'
                    real_proxy_ip = get_real_proxy_ip(proxy_ip)

                if real_proxy_ip:
                    # real_proxy_ip = "real_ip_test"
                    self.profile_table.setItem(profile_table_row_index, 3, QTableWidgetItem(real_proxy_ip))
                    result = self.serviceSpreadSheet.values().get(
                        spreadsheetId="1uEkPu8l7XUlTIM17S_Sdn40YcvbM4xEHWuXpuf7hGNE",
                        range="IP!D3:D"
                    ).execute()

                    b_column_ip_sheet_values = result.get('values', [])
                    if not b_column_ip_sheet_values:
                        self.update_result_cell_profile_table({
                            "error": True,
                            "message": "Không tìm thấy giá tri mã số trong cột B của bảng IP",
                            "profile_table_row_index": profile_table_row_index
                        })
                    else:
                        for b_column_ip_sheet_value in b_column_ip_sheet_values:
                            if b_column_ip_sheet_value[0] == self.profile_table.item(profile_table_row_index, 6).text():
                                # Get A1 notation of the cell
                                cell_row_index = b_column_ip_sheet_values.index(b_column_ip_sheet_value) + 3
                                self.serviceSpreadSheet.values().batchUpdate(
                                    spreadsheetId="1uEkPu8l7XUlTIM17S_Sdn40YcvbM4xEHWuXpuf7hGNE",
                                    body={
                                        "valueInputOption": "RAW",
                                        "data": [
                                            {
                                                "range": f"IP!E{cell_row_index}",
                                                "values": [[real_proxy_ip]]
                                            },
                                            {
                                                "range": f"Tools!C{self.profile_table.item(profile_table_row_index, 1).text()}",
                                                "values": [[real_proxy_ip]]
                                            }
                                        ]
                                    }
                                ).execute()
                                request = self.serviceSpreadSheet.get(
                                    spreadsheetId="1uEkPu8l7XUlTIM17S_Sdn40YcvbM4xEHWuXpuf7hGNE",
                                    ranges=f"IP!E{cell_row_index}",
                                    includeGridData=True
                                )
                                response = request.execute()
                                color_background_value = \
                                    response["sheets"][0]["data"][0]["rowData"][0]["values"][0]["effectiveFormat"][
                                        "backgroundColorStyle"]["rgbColor"]
                                if color_background_value.get("red") != 1 or color_background_value.get(
                                        "green") != 1 or color_background_value.get("blue") != 1:
                                    self.update_result_cell_profile_table({
                                        "error": True,
                                        "message": "IP bị trùng! Bỏ qua.",
                                        "profile_table_row_index": profile_table_row_index
                                    })
                                    self.serviceSpreadSheet.values().update(
                                        spreadsheetId="1uEkPu8l7XUlTIM17S_Sdn40YcvbM4xEHWuXpuf7hGNE",
                                        range=f"Tools!C{self.profile_table.item(profile_table_row_index, 1).text()}",
                                        valueInputOption='RAW',
                                        body={'values': [["IP bị trùng! Bỏ qua."]]}
                                    ).execute()
                                else:
                                    gologin_profile_create_thread = GoLoginProfileCreateThread(
                                        (profile_table_row_index, {
                                            'goLoginToken': self.gologin_api_key_input.text(),
                                            'name': f'Windows {self.profile_table.item(profile_table_row_index, 6).text()}',
                                            'os': 'win',
                                            'proxy': raw_proxy,
                                            'emailAppen': self.profile_table.item(profile_table_row_index, 8).text(),
                                            'passwordAppen': self.profile_table.item(profile_table_row_index, 9).text(),
                                            "email|password": self.profile_table.item(profile_table_row_index, 7).text()
                                        }))
                                    gologin_profile_create_thread.gologin_profile_created_signal.connect(
                                        self.update_profile_table)
                                    (gologin_profile_create_thread.gologin_profile_created_update_result_signal
                                     .connect(self.update_result_cell_profile_table))

                                    gologin_profile_create_thread.gologin_profile_driver_created_signal.connect(
                                        self.update_gologin_profile_drivers)
                                    self.gologin_profile_create_threads.append(gologin_profile_create_thread)
                else:
                    self.update_result_cell_profile_table({
                        "error": True,
                        "message": "Không lấy được địa chỉ IP của Proxy. Bỏ qua.",
                        "profile_table_row_index": profile_table_row_index
                    })
                    self.serviceSpreadSheet.values().update(
                        spreadsheetId="1uEkPu8l7XUlTIM17S_Sdn40YcvbM4xEHWuXpuf7hGNE",
                        range=f"Tools!C{self.profile_table.item(profile_table_row_index, 1).text()}",
                        valueInputOption='RAW',
                        body={'values': [["Không lấy được địa chỉ IP của Proxy. Bỏ qua."]]}
                    ).execute()
        for gologin_profile_create_thread in self.gologin_profile_create_threads:
            gologin_profile_create_thread.start()

    def update_gologin_profile_drivers(self, driver_gologin_profile_created_data):
        self.gologin_profile_selenium_drivers[
            driver_gologin_profile_created_data.get('data').get('profile_table_row_index')] = \
            driver_gologin_profile_created_data.get('data').get('driver_created')

    def update_profile_table(self, update_profile_table_data):
        update_profile_table_data_error = update_profile_table_data.get("error")
        if not update_profile_table_data_error:
            result_item_in_project_table = QTableWidgetItem(update_profile_table_data_error)
            result_item_in_project_table.setForeground(QColor("green"))
            self.profile_table.setItem(update_profile_table_data.get("data").get('profile_table_row_index'),
                                       11,
                                       result_item_in_project_table)
        else:
            result_item_in_project_table = QTableWidgetItem(update_profile_table_data_error)
            result_item_in_project_table.setForeground(QColor("red"))
            self.profile_table.setItem(update_profile_table_data.get("data").get('profile_table_row_index'),
                                       11,
                                       result_item_in_project_table)

    def update_result_cell_profile_table(self, result_dict):
        result_dict_error = result_dict.get("error")
        result_dict_message = result_dict.get("message")
        result_dict_profile_table_row_index = result_dict.get("profile_table_row_index")

        result_item_in_project_table = QTableWidgetItem(result_dict_message)
        if result_dict_error:
            result_item_in_project_table.setForeground(QColor("red"))
        else:
            result_item_in_project_table.setForeground(QColor("green"))

        self.profile_table.setItem(result_dict_profile_table_row_index, 11, result_item_in_project_table)
        stt_number = self.profile_table.item(result_dict_profile_table_row_index, 1).text()
        try:
            self.serviceSpreadSheet.values().update(
                spreadsheetId="1uEkPu8l7XUlTIM17S_Sdn40YcvbM4xEHWuXpuf7hGNE",
                range=f"Tools!K{stt_number}",
                valueInputOption='RAW',
                body={'values': [[result_dict_message]]}
            ).execute()
        except Exception as e:
            result_item_in_project_table.setText(
                f'Có lỗi xảy ra khi update Google Sheet với nội dung {result_dict_message}, lỗi: {str(e)}')
            result_item_in_project_table.setForeground(QColor("red"))
            self.profile_table.setItem(result_dict_profile_table_row_index, 11, result_item_in_project_table)

    def create_creds_google(self):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            self.google_creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.google_creds or not self.google_creds.valid:
            if self.google_creds and self.google_creds.expired and self.google_creds.refresh_token:
                self.google_creds.refresh(Request())
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
                self.google_creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self.google_creds.to_json())

    def create_api_key_input_layout(self):
        gologin_api_key_layout = QHBoxLayout()

        self.gologin_api_key_input = QLineEdit()
        self.gologin_api_key_input.setPlaceholderText("API Key")
        self.gologin_api_key_input.setText(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
            ".eyJzdWIiOiI2NjA2YmRiM2QxM2QyZDE5ZGNjNjkwNjgiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2NjA2YmRjYzEwZTU3ZWUwZjZmOTlhNDUifQ"
            ".v-vaL0-O62BmR4LGxHNzn30UncvxzUdRRanM-FpmZiU")

        connect_gologin_button = QPushButton("Kết nối Go Login")
        connect_gologin_button.clicked.connect(self.connect_gologin)

        self.connect_gologin_result_label = QLabel()
        self.connect_gologin_result_label.setAlignment(Qt.AlignCenter)
        self.set_gologin_result_label("Chưa kết nối GoLogin", QColor("black"))

        self.google_sheet_row_range_input = QLineEdit()
        self.google_sheet_row_range_input.setPlaceholderText("Range Google Sheets Row")
        self.google_sheet_row_range_input.setText("1")

        get_sheet_row_range_input_button = QPushButton("Lấy data từ Sheet")
        get_sheet_row_range_input_button.clicked.connect(self.get_sheet_row_range_input)

        gologin_api_key_layout.addWidget(self.gologin_api_key_input)
        gologin_api_key_layout.addWidget(connect_gologin_button)
        gologin_api_key_layout.addWidget(self.connect_gologin_result_label)
        gologin_api_key_layout.addWidget(self.google_sheet_row_range_input)
        gologin_api_key_layout.addWidget(get_sheet_row_range_input_button)

        self.main_layout.addLayout(gologin_api_key_layout)

    def get_sheet_data_from_row(self):
        try:
            service = build('sheets', 'v4', credentials=self.google_creds)
        except Exception as e:
            print(e)
            service = build('sheets', 'v4', credentials=self.google_creds,
                            discoveryServiceUrl='https://sheets.googleapis.com/$discovery/rest?version=v4')
        # Call the Sheets API
        self.serviceSpreadSheet = service.spreadsheets()
        result = (
            self.serviceSpreadSheet.values()
            .get(spreadsheetId="1uEkPu8l7XUlTIM17S_Sdn40YcvbM4xEHWuXpuf7hGNE", range="Tools!A2:I")
            .execute()
        )
        values = result.get("values", [])
        self.fill_data_to_profile_table(values)

    def fill_data_to_profile_table(self, values):
        self.profile_table.setRowCount(0)
        for value in values:
            row_position = self.profile_table.rowCount()
            self.profile_table.insertRow(row_position)
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.profile_table.setCellWidget(row_position, 0, checkbox)
            for col, val in enumerate(value, start=1):
                item = QTableWidgetItem(val)
                self.profile_table.setItem(row_position, col, item)
            gologin_profile_select_checkbox = QComboBox()
            gologin_profile_select_checkbox.addItem("Tạo Profile mới", 0)
            gologin_profile_select_checkbox.setCurrentIndex(0)
            self.profile_table.setCellWidget(row_position, 10, gologin_profile_select_checkbox)
            gologin_continue_after_manual_login_appen_btn = QPushButton("Tiếp tục")
            (gologin_continue_after_manual_login_appen_btn.clicked
             .connect(lambda checked=row_position, r=row_position: self.continue_gologin_apply_in_driver(checked)))
            self.profile_table.setCellWidget(row_position, 12, gologin_continue_after_manual_login_appen_btn)

    def get_sheet_row_range_input(self):
        input_text = self.google_sheet_row_range_input.text().strip()
        google_sheet_range = None

        if not input_text:
            google_sheet_range = "Tools!A2:I"
        else:
            split_range = input_text.split("-")
            if all(part.isdigit() for part in split_range):
                if len(split_range) == 1:
                    google_sheet_range = f"Tools!A{input_text}:I{input_text}"
                elif len(split_range) == 2:
                    start, end = map(int, split_range)
                    google_sheet_range = f"Tools!A{start}:I{end}"

        if google_sheet_range:
            result = (
                self.serviceSpreadSheet.values()
                .get(spreadsheetId="1uEkPu8l7XUlTIM17S_Sdn40YcvbM4xEHWuXpuf7hGNE", range=google_sheet_range)
                .execute()
            )
            values = result.get("values", [])
            self.fill_data_to_profile_table(values)

    def continue_gologin_apply_in_driver(self, profile_table_row_index):
        driver = self.gologin_profile_selenium_drivers[profile_table_row_index]
        random_create_profile_id = generate_random_string(5)
        go_login_continue_create_profile_thread = GoLoginContinueCreateProfileThread((profile_table_row_index, driver, {
            "email|password": self.profile_table.item(profile_table_row_index, 7).text(),
        }))
        (go_login_continue_create_profile_thread.go_login_continue_create_profile_update_result_signal
         .connect(self.update_result_cell_profile_table))
        self.gologin_continue_create_profile_threads[random_create_profile_id] = go_login_continue_create_profile_thread
        self.gologin_continue_create_profile_threads[random_create_profile_id].start()

    def connect_gologin(self):
        gologin_api_key = self.gologin_api_key_input.text().strip()
        if not gologin_api_key:
            self.set_gologin_result_label("API Key is empty", QColor("red"))
            return
        self.set_gologin_result_label("Đang kết nối Go Login...", QColor("yellow"))
        url = "https://api.gologin.com/browser/v2"
        payload = {}
        headers = {'Authorization': f'Bearer {gologin_api_key}', 'Content-Type': 'application/json'}
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()
            profiles = data.get("profiles", [])
            num_profiles = len(profiles)
            self.set_gologin_result_label(f"Kết nối Go Login thành công ({num_profiles} profile)", QColor("green"))
        except Exception as e:
            print(f"Error connecting to GoLogin API: {e}")
            self.set_gologin_result_label("Kết nối Go Login chưa thành công", QColor("red"))

    def set_gologin_result_label(self, text, color):
        self.connect_gologin_result_label.setText(text)
        self.connect_gologin_result_label.setStyleSheet(f"color: {color.name()};")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec())
