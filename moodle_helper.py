import re
import time
from getpass import getpass
from selenium import webdriver
from rich.console import Console
from rich.markdown import Markdown
from selenium.common.exceptions import NoSuchElementException

USERNAME_PATTERN = "S[0-9]{10}"
console = Console()

def get_browser_driver():   
  # also other driver like ChromeDriver can be used (use correct version)
  # https://chromedriver.chromium.org/
  return webdriver.Safari()

def get_user_data():
  console.print("USER DATA:", style="bold")
  while True:
    username = console.input("Enter your [bold blue]username[/]: ")
    password = console.input("Enter your [bold blue]password[/]: ", password=True)
    if (re.match(USERNAME_PATTERN, username)):
      return { "username": username, "password": password }
    else:
      console.log("[bold red] Error in username. (has to match " + USERNAME_PATTERN + ")[/] ")

def get_submission_data():
  console.print("SUBMISSION DATA:", style="bold")
  submission_url = console.input("Enter [bold blue]submission url[/]: ")
  submission_pattern = console.input("Enter [bold blue]submission pattern[/]: ")
  return { "url": submission_url, "pattern": submission_pattern }

def get_all_submission_urls(a_tags):
  urls = [] # list of tupel
  for tag in a_tags:
    if re.search(".*assignsubmission_file.*", tag.get_attribute("href")):
      urls.append((tag.text, tag.get_attribute("href")))
      console.log(tag.get_attribute("href"))
  return urls

def get_filtered_submissions(submissions, pattern):
  filtered_urls = []
  for url in submissions:
    if re.search(pattern, url[0]):
      filtered_urls.append(url[1])
      console.log(url[0] + " -> " + url[1])
  return filtered_urls

def get_agreement_for_download():
  agree = ''
  while True:
    agree = console.input("[bold blue]Download filtered sumbissions? (y,n)[/]: ")
    if re.match('(y|n)', agree):
      return agree == 'y'

def download_submissions(browser_driver, submissions):
  with console.status("Downloading...") as status:
    for submission in filtered_urls:
        browser_driver.get(submission)
        console.log(f"submission " + submission + " downloaded")

def is_logged_in(browser_driver):
    try:
        browser_driver.find_element_by_id("loginerrormessage")
    except NoSuchElementException:
        return True
    return False


console.print(Markdown("# Tutorium Helper (Moodle Submission Downloader)"))

while True:
  user_data = get_user_data()
  console.print(Markdown("---"))

  submission_data = get_submission_data()
  console.print(Markdown("---"))

  console.print("BROWSER CONFIG AND LOGIN", style="bold")
  driver = get_browser_driver()
  driver.get(submission_data["url"])
  console.print(Markdown("---"))

  driver.find_element_by_id("username").send_keys(user_data["username"])
  driver.find_element_by_id("password").send_keys(user_data["password"])
  driver.find_element_by_id("loginbtn").click()
  time.sleep(2)
  if is_logged_in(driver):
    break
  else:
    console.print("Error, wrong username or password!", style="bold red")
  driver.close()
console.print(Markdown("---"))

console.print("SEARCHING FOR SUBMISSIONS:", style="bold")
all_submission_urls = get_all_submission_urls(driver.find_elements_by_xpath("//a[@href]"))
console.print(Markdown("---"))

console.print("FILTER SUBMISSIONS:", style="bold")
filtered_urls = []
if submission_data["pattern"] == '':
  filtered_urls = get_filtered_submissions(all_submission_urls, ".*")
else:
  filtered_urls = get_filtered_submissions(all_submission_urls, ".*" + submission_data["pattern"] + ".*")
console.print(Markdown("---"))

console.print("DOWNLOAD:", style="bold")
if get_agreement_for_download():
  console.print(Markdown("---"))
  download_submissions(driver, filtered_urls)
console.print(Markdown("---"))

driver.close()
