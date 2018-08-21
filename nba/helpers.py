from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.common.exceptions as selexc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from nba_exceptions import InvalidBrowserError
import sqlite3
import traceback
import sys

browser = "chrome"

def detect_browser():

    # Detect user's browser and set browser to be the best available one.
    # Raise InvalidBrowserError if no supported browser is found.

    global browser

    try:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome()
    except (selexc.WebDriverException, FileNotFoundError) as exc:
        pass
    else:
        driver.quit()
        return

    try:
        options = webdriver.FirefoxOptions()
        options.add_argument('headless')
        driver = webdriver.Firefox()
    except (selexc.WebDriverException, FileNotFoundError) as exc:
        pass
    else:
        browser = "firefox"
        driver.quit()
        return

    try:
        driver = webdriver.PhantomJS()
    except (selexc.WebDriverException, FileNotFoundError) as exc:
        pass
    else:
        browser = "PhantomJS"
        print("Using PhantomJS, which is an unsupported browser.",
            "Consider installing Chrome or Firefox.", file=sys.stderr)
        driver.quit()
        return

    try:
        driver = webdriver.Opera()
    except (selexc.WebDriverException, FileNotFoundError) as exc:
        pass
    else:
        browser = "opera"
        print("Using Opera. Opera does not support headless mode, so",
            "consider installing Chrome or Firefox.", file=sys.stderr)
        return

    try:
        driver = webdriver.Safari()
    except (selexc.WebDriverException, FileNotFoundError) as exc:
        pass
    except selexc.SessionNotCreatedException:
        print("To use Safari for scraping, enable 'Allow Remote",
            "Automation' option in Safari's Develop menu. Safari does not",
            "support headless mode, so consider installing Chrome or Firefox",
            file=sys.stderr)
    else:
        browser = "safari"
        print("Using Safari. Safari does not support headless mode, so",
            "consider installing Chrome or Firefox.", file=sys.stderr)
        return

    raise InvalidBrowserError("No supported browsers found. Install Chrome or Firefox for",
        "optimal usage.")

def get_players(link):

    # Return BeautifulSoup page of stats.nba.com's list of players.

    global browser

    if browser == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('user-agent=Kobe')
        driver = webdriver.Chrome(chrome_options=options)
    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument('headless')
        options.add_argument('user-agent=Kobe')
        driver = webdriver.Firefox(firefox_options=options)
    elif browser == "PhantomJS":
        driver = webdriver.PhantomJS()
    elif browser == "opera":
        driver = webdriver.Opera()
    elif browser == "safari":
        driver = webdriver.Safari()
    else:
        raise InvalidBrowserError("No valid browser found.")
    driver.get(str(link))
    soup = BeautifulSoup(driver.page_source, features='lxml')
    driver.quit()
    return soup

def get_player_trad(link, mode="both"):

    # Return an html table of an NBA player's career regular season and
    # playoffs stats.

    global browser

    if browser == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('user-agent=Kobe')
        driver = webdriver.Chrome(chrome_options=options)
    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument('headless')
        options.add_argument('user-agent=Kobe')
        driver = webdriver.Firefox(firefox_options=options)
    elif browser == "PhantomJS":
        driver = webdriver.PhantomJS()
    elif browser == "opera":
        driver = webdriver.Opera()
    elif browser == "safari":
        driver = webdriver.Safari()
    else:
        raise InvalidBrowserError("No valid browser found.")

    driver.get(str(link))
    if mode == "season":
        try:
            html = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            return [BeautifulSoup(html.get_attribute('innerHTML'),
                features='lxml')]
        finally:
            driver.quit()
    try:
        htmls = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
        )
        soup = BeautifulSoup(htmls[0].get_attribute('innerHTML'),
            features='lxml')
        psoup = soup
        psoup = BeautifulSoup(htmls[2].get_attribute('innerHTML'),
                features='lxml')
        if mode == "playoffs":
            return [psoup]
        elif mode == "both":
            return [soup, psoup]
    finally:
        driver.quit()

def scrape_player_trad(page, id, playoffs=False):

    # Create database table for a player if it doesn't already exist.
    # Write regular season or playoffs stats to the table as specified by
    # the playoffs flag.

    if playoffs == False:
        pcheck = 0
    else:
        pcheck = 1

    db = sqlite3.connect('data.db')
    player_writer = db.cursor()
    name = 'p' + str(id)

    try:
        player_writer.execute('''CREATE TABLE %s(playoffs INTEGER)''' % name)
    except sqlite3.OperationalError:
        pass
    else:
        for statistic in page.find_all("th"):
            if "class" in statistic.attrs and "text" in statistic["class"]:
                tag = statistic.span
            else:
                tag = statistic
            file_string = str(tag).split('>')[1].split('<')[0]
            if file_string in ["Season", "TEAM"]:
                player_writer.execute('''ALTER TABLE %s ADD %s
                    TEXT''' % (name, file_string))
            else:
                if '%' in file_string:
                    file_string = file_string.replace("%", "percent")
                if '3' in file_string:
                    file_string = file_string.replace("3", "three")
                player_writer.execute('''ALTER TABLE %s ADD %s
                    NUMERIC''' % (name, file_string))
    db.commit()

    # Update table even if it already exists:

    values = []
    entries = []
    for statistic in page.tbody.find_all("td"):
        if "class" in statistic.attrs:
            if "player" in statistic["class"]:
                if len(values) > 0:
                    entries.append(tuple(values))
                values = [pcheck]
                values.append(str(statistic.a['href']).split('=')[1].
                    split('&')[0])
            elif "text" in statistic["class"]:
                values.append(str(statistic.span).split('>')[1].
                    split('<')[0])
        else:
            temp = str(statistic).split('>')[1].split('<')[0]
            if temp in ['', '-', None]:
                values.append(None)
            else:
                values.append(float(str(statistic).
                    split('>')[1].split('<')[0]))
    if len(values) > 0:
        entries.append(tuple(values))
    values = [pcheck]
    for total in page.tfoot.find_all("td"):
        value = str(total).split('>')[1].split('<')[0]
        if value in ["", "-"]:
            value = None
        if value == "Overall: ":
            value = "CAREER"
        values.append(value)

    entries.append(tuple(values))
    place = ', '.join('?' * len(values))
    player_writer.executemany('''INSERT INTO %s values (%s)''' %
        (name, place), entries)
    db.commit()
    db.close()
