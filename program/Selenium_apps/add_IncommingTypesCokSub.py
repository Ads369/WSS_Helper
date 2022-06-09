from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pathlib import Path
import urllib
import time
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent
driver_path = Path(BASE_DIR, "driver", "chromedriver")
driver = webdriver.Chrome(executable_path=driver_path)

# Get security data
with open(r"config/config.yaml", encoding="utf8") as f:
    config = yaml.safe_load(f)

# Work Server Admin
login = urllib.parse.quote(config["selenium"]["admin_login"], safe="")
pswd = urllib.parse.quote(config["selenium"]["admin_password"], safe="")
main_link = config["selenium"]["docs_main_url"]
driver.get(f"https://{login}:{pswd}@{main_link}")

# task ИТ-СЭД-2022-0216
driver.get(f"https://{main_link}dms/_layouts/WSS/DBF/UI/ListView.aspx?listID=738")

tt = [
    # ('Изменение начальных показаний по справке УК','Проведение перерасчета'),
]

for i in tt:
    type_cok_str = i[1]
    naming_sub_str = i[0]
    print(naming_sub_str)

    # Create new element
    create_btn = driver.find_element(By.LINK_TEXT, "Создать элемент")
    create_btn.click()

    # switch to new tab
    driver.switch_to.window(driver.window_handles[-1])

    # fill field "Наименование"
    naming = driver.find_element(
        By.XPATH, '//*[@id="divTextField16150"]/div/div/div/input'
    )
    naming.clear()
    naming.send_keys(naming_sub_str)

    # fill field "Вид обращения"
    btn_1 = driver.find_element(
        By.XPATH,
        "//*" '[@id="listForm_fieldControl16149_pnlFieldControl"]' "/div/div[1]/div[2]",
    )
    btn_1.click()
    time.sleep(1)

    # select values of grid
    grid = driver.find_element(By.XPATH, '//*[@id="divGrid"]')
    rows = driver.find_elements(By.XPATH, '//*[@id="gridLookupItems"]/tbody/tr')
    print(len(rows))
    for row in rows:
        if row.text == type_cok_str:
            print(row.text)
            row.click()
    time.sleep(1)

    # ok grid btn
    ok_btn = driver.find_element(By.XPATH, '//*[@id="btnOk"]/div/div')
    ok_btn.click()

    # Update cards
    btn_upd = driver.find_element(By.XPATH, '//*[@id="btnUpdate"]')
    btn_upd.click()
    print("+")
    time.sleep(1)

    # switch to new tab
    driver.switch_to.window(driver.window_handles[0])
