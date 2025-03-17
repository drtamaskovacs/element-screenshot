from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait #
from selenium.webdriver.support import expected_conditions as EC #
import time
from PIL import Image

# Bejelentkezési adatok
# EMAIL = "admin@sptech.ch"
PASSWORD = "9ds0KstwKRdVYZtHCfYO04o0YJKCNbTX"

# Selenium beállítása
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Fej nélküli mód, ha nem kell látnod a böngészőt
options.add_argument("--window-size=1920,1080")

# WebDriver inicializálása
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # 1. Nyisd meg a bejelentkezési oldalt
    driver.get("http://localhost:8000/login")  # Cseréld ki a megfelelő URL-re
    time.sleep(1)  # Adj időt a betöltéshez

    # 2. Email mező kitöltése
    # email_field = driver.find_element(By.NAME, "username")  # Cseréld le, ha más az input mező neve
    # email_field.send_keys(EMAIL)

    # 3. Jelszó mező kitöltése
    password_field = driver.find_element(By.NAME, "password")  # Cseréld le, ha más az input mező neve
    password_field.send_keys(PASSWORD)

    # 4. Login gomb keresése és kattintás
    login_button = driver.find_element(By.XPATH, "//button[@type='submit' and span[text()='Log in']]")
    login_button.click()

    # 5. Várakozás a bejelentkezés után az oldal betöltésére
    time.sleep(1)  # Ha lassan tölt be, növeld ezt az értéket

    # 6. Nyisd meg a kívánt oldalt (ha más oldalra kell menned bejelentkezés után)
    driver.get("http://localhost:8000/workspaces/48180477-e986-4889-9010-f15f6191c41a/source/f6873dcd-ffe7-4da8-aa5b-35285b25ae4b")  # Source connector config a MCO PoC-ben
    time.sleep(1)

    # 7. Expandálandó elemek keresése
    # Stream nyitas
    expand_element = driver.find_element(By.XPATH, "//p[contains(text(), '| Globs:')]")
    button_element = expand_element.find_element(By.XPATH, "./ancestor::button")
    aria_expanded_value = button_element.get_attribute("aria-expanded")
    print(aria_expanded_value)

    if aria_expanded_value=='false':
        button_element.click()
        time.sleep(1)  # Várunk, hogy a tartalom betöltődjön
    
    # "Optional field" elem keresése a streamben, ha zarva van, akkor kinyitasa
    expand_element = driver.find_element(By.XPATH, "//p[text()='Optional fields']")
    button_element = expand_element.find_element(By.XPATH, "./ancestor::button")
    aria_expanded_value = button_element.get_attribute("aria-expanded")
    print(aria_expanded_value)

    if aria_expanded_value=='false':
        button_element.click()
        time.sleep(1)  # Várunk, hogy a tartalom betöltődjön

    # "Optional field" elem keresése az fooldalon, ha zarva van, akkor kinyitasa
    expand_element = driver.find_elements(By.XPATH, "//p[text()='Optional fields']")
    button_element = expand_element[2].find_element(By.XPATH, "./ancestor::button")
    aria_expanded_value = button_element.get_attribute("aria-expanded")
    print(aria_expanded_value)

    if aria_expanded_value=='false':
        button_element.click()
        time.sleep(1)  # Várunk, hogy a tartalom betöltődjön

    # 8. Görgethető menü megkeresése (cseréld ki a megfelelő CLASS_NAME-re vagy XPATH-ra!)
    scrollable_div = driver.find_element(By.CLASS_NAME, "SourceItemPage-module__pageBody__8a3a27")  # Cseréld ki a megfelelő osztályra!

    # 9. Visszagörgetés a tetejére
    driver.execute_script("arguments[0].scrollTop = 0", scrollable_div)
    time.sleep(1)

    # 10. Screenshot készítés
    div_location = scrollable_div.location
    div_height = int(scrollable_div.get_attribute("scrollHeight"))
    window_width = int(scrollable_div.size["width"])
    window_height = int(scrollable_div.size["height"])
    number_picture = (div_height // window_height) + 1
    lastpicture_height = div_height % window_height
    scrollbar_width = int(driver.execute_script("""return arguments[0].offsetWidth - arguments[0].clientWidth;""", scrollable_div)) # scrollbar szelessege

    #Definialjuk a kepek nagysagat
    img_prop = []

    for i in range(number_picture):
        picture_data = {
            "x": 0,
            "y": i * window_height,
            "width": window_width
        }

        if i == number_picture - 1:
            picture_data["height"] = lastpicture_height  # Speciális magasság az utolsó képre
        else:
            picture_data["height"] = window_height  # Normál magasság       

        # Hozzáadjuk a listához
        img_prop.append(picture_data)

    #Screenshot-olunk   
    screenshots = []

    for i, img in enumerate(img_prop):
        #Itt csinalajuk a full screenshotot
        current_scroll_position = img["y"]
        driver.execute_script("arguments[0].scrollTop = arguments[1]", scrollable_div, current_scroll_position)
        time.sleep(1)
        file_name = f"screenshot_{current_scroll_position}.png"
        driver.save_screenshot(file_name)

        # Kivágjuk a megfelelő részt a képből
        full_screenshot = Image.open(file_name)
        if i == len(img_prop) - 1:
            cropped_screenshot = full_screenshot.crop(( 
                int(div_location["x"]),
                int(div_location["y"] + window_height - lastpicture_height),
                int(div_location["x"] + window_width - scrollbar_width),
                int(div_location["y"] + window_height)
            ))    
        else:
            cropped_screenshot = full_screenshot.crop(( 
                int(div_location["x"]),
                int(div_location["y"]),
                int(div_location["x"] + window_width - scrollbar_width),
                int(div_location["y"] + window_height)
            ))
        
        cropped_screenshot.save(file_name)
        #print(i+1,'. screenshot elkeszult')

        screenshots.append(file_name)

    # 10. Képek összefűzése
    images = [Image.open(img) for img in screenshots]
    total_width = images[0].width
    total_height = sum(img.height for img in images)

    final_image = Image.new("RGB", (total_width, total_height))
    y_offset = 0

    for img in images:
        final_image.paste(img, (0, y_offset))
        y_offset += img.height

    final_image.save("Screenshot_SourceConnectorConfig.png")
    print("📸 A full screenshotok elkészült!")

finally:
    driver.quit()
