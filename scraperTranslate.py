# Libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import shutil, time, os
from datetime import datetime, timedelta
from datetime import date, timedelta
from pathlib import Path
from os import walk
import datetime as dt
import time, shutil, os
from datetime import datetime
import os.path  
import zipfile
from zipfile import ZipFile 


# Get config from plain text file
def getConfigScrapper():
    directory_down = os.path.join( os.getcwd() , 'download' ) 
    path_chrome_dv = os.path.join( os.getcwd() , 'chromedriver.exe' )
    return directory_down, path_chrome_dv

# Setup Scrapper 
def setupChrome(path_chrome_dv, directory):
    options = Options()
    
    #options.headless = True
    options.add_experimental_option(
        "prefs", {
            "download.default_directory": directory ,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
    )
    options.add_argument("--lang=es")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome( path_chrome_dv ,options=options )
    #driver = webdriver.Chrome( path_chrome_dv ,chrome_options=options )
    return driver

def translate(driver, sentence, slep=3):
    #verifica la url y redirige si no es la deseada
    if driver.current_url != "https://translate.google.cl/?sl=th&tl=es":
        driver.get('https://translate.google.cl/?sl=th&tl=es')
        time.sleep(slep)

    #verifica si el boton de limpiar traduccion existe y de hacerlo lo presiona
    clearBtn = driver.find_element_by_xpath("/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz[1]/div[2]/div/div/span/button/i")
    if clearBtn!=None:
        if clearBtn.get_attribute("aria-hidden")!='true':
            clearBtn.click()
    
        # input.clear() #comentado por q no es necesario con el clearBtn
    input = driver.find_element_by_xpath("/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz[1]/span/span/div/textarea")
    
    #ingreso el texto
    input.send_keys(sentence)
    time.sleep(slep)
    try:
        wait = WebDriverWait(driver, 60)
        wait.until(ec.visibility_of_element_located((By.XPATH, "/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz[2]/div[5]/div"))) # Espera que aparezcan datos en la primera fila del panel 
        driver.implicitly_wait(1)
    except Exception as e:
        print(e)


    #obtengo la supuesta traduccion y de ser igual la retorna, de lo contrario la limpia
    output=""
    try:
        output = driver.find_element_by_xpath("/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz[2]/div[5]/div")
        return output.text
    except Exception as e:
        print(e)
        
    clearBtn = driver.find_element_by_xpath("/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz[1]/div[2]/div/div/span/button/i")
    if clearBtn!=None:
        if clearBtn.get_attribute("aria-hidden")!='true':
            clearBtn.click()
    

def main(skip=3, enc='TIS-620'):
    timeStart = dt.datetime.now()
    print('')
    print('*****************************************************')
    print('**** Translate - SCRAPPER ****')
    print('*****************************************************')
    print('')

    # Setup chrome-driver
    directory_down, path_chrome_dv = getConfigScrapper()
    driver = setupChrome(path_chrome_dv, directory_down)
    print('- Correcta configuración de Selenium ')

    readFolder='readFolder'

    if not os.path.exists( os.path.join(os.getcwd(),readFolder)):
        try:
            os.makedirs(os.path.join(readFolder))
        except OSError as e:
            if e.errno != e.errno.EEXIST:
                raise

    translateDestinyFolder='translated'
    if not os.path.exists( os.path.join(os.getcwd(),translateDestinyFolder)):
        try:
            os.makedirs(os.path.join(translateDestinyFolder))
        except OSError as e:
            if e.errno != e.errno.EEXIST:
                raise

    fileContain = "~" #omite archivos abiertos
    text_files = [f for f in os.listdir(os.path.join(os.getcwd(),readFolder)) if not(fileContain in f)]
    if len(text_files)>0:
        for i in range(len(text_files)):
            print(" - Abriendo archivo {}".format(text_files[i]))
            filename = "./{}/{}".format(readFolder, text_files[i])
            if os.path.exists(filename):
                f = open (filename,'r', encoding=enc)
                sf = open("./{}/{}".format(translateDestinyFolder, text_files[i]), "a+", encoding="utf-8") #corregir los character maps undefined (los de español q no existen en el otro)
                num_lines_sf = sum(1 for line in sf)
                # mensaje = f.read()
                for index, linea in enumerate(f):
                    
                    sentencia = linea.replace("\n", "")

                    if (index+1)>skip and (index+1)>=num_lines_sf:
                        # print(linea)
                        
                        partes = sentencia.split("|")
                        for i in range(len(partes)-1):
                            partes[i] = partes[i].strip()
                        if len(partes)>3:
                            partes = [partes[0], " | ".join(partes[1:-1]),partes[-1]]

                        traduccion = translate(driver, partes[1])
                        if traduccion!=None:
                            #limpiar de la traduccion
                            traduccion= traduccion.replace("\n volume_up\ncontent_copy\nshare", "").replace("\n", "")
                            sf.write("{}|{}| \n".format(partes[0], traduccion))  
                        else:
                            print("La linea [{}] no se pudo traducir.".format(sentencia))
                            sf.write("{} \n".format(sentencia))  
                    # print(sentencia)  
                    else:
                        sf.write("{} \n".format(sentencia))  
                f.close()
                sf.close()

    
    # Close program
    driver.close()

    timeEnd = dt.datetime.now()
    print("[{} - {}] Fin del programa. Duracion: [{}]".format(timeStart.strftime("%H:%M:%S"), timeEnd.strftime("%H:%M:%S"), (timeEnd-timeStart)))

main()