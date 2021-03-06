try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar

try:
    input = raw_input
except NameError:
    pass

try:
    from urllib.request import HTTPCookieProcessor, build_opener, install_opener, Request, urlopen
    from urllib.parse import urlencode
except ImportError:
    from urllib2 import HTTPCookieProcessor, build_opener, install_opener, Request, urlopen
    from urllib import urlencode

import re
from time import sleep
import webbrowser
from random import randrange
from bs4 import BeautifulSoup
import requests

def genURL(quarter, year, SLN):
    return "https://sdb.admin.uw.edu/timeschd/uwnetid/sln.asp?QTRYR="+quarter+"+"+year+"&SLN="+SLN

ses = requests.Session()

def login(user, pwd, url):
    login_page = ses.get(url)
    post_page = login_page.url  # UW verifies at the same url
    mid_post = "https://sdb.admin.uw.edu/Shibboleth.sso/SAML2/POST"

    # Passing general UW login
    soup_login = BeautifulSoup(login_page.content, "html.parser").find('form').find_all('input')
    my_dict = {}
    for u in soup_login:
        if u.has_attr('value'):
            my_dict[u['name']] = u['value']
    my_dict['j_username'] = user
    my_dict['j_password'] = pwd

    # Passing individual app verification
    ses.post(post_page, data=my_dict)
    mid_page = ses.get(url)
    soup_check = BeautifulSoup(mid_page.content, "html.parser").find('form').find_all('input')
    mid_dict = {}
    for u in soup_check:
        if(u.has_attr('name')):
            mid_dict[u['name']] = u['value']
    ses.post(mid_post, data=mid_dict)


def checkOpen(url):
    return -1 == ses.get(url).text.find('** Closed **')

def register(courses):
    register_page = ses.get("https://sdb.admin.uw.edu/students/uwnetid/register.asp")
    soup_register = BeautifulSoup(register_page.content, "html.parser").find('form').find_all('input')
    reg_dict = {}
    for u in soup_register:
        if(u.has_attr('name')):
            reg_dict[u['name']] = ''
            if(u.has_attr('value')):
                reg_dict[u['name']] = u['value']
    course_index = 0
    for key, val in reg_dict.items():
        if(key.find('sln') != -1 and val == '' and course_index < len(courses)):
            reg_dict[key] = courses[course_index]
            course_index += 1
        print(key + ": " + reg_dict[key])
    input('Press enter to register')
    # This line is hecka broken. Do not uncomment.
    # ses.post(register_page.url, data=reg_dict)
    print(ses.get(register_page.url).text)


user = input('UW NET ID: ')
pwd = input('PASSWORD: ')

#Setting courses to check
sln1 = input('Course to add (enter q to begin checking): ')
courses = [sln1]
scheduling = True
while(scheduling):
    sln = input('Course to add (enter q to begin checking): ')
    if(sln != 'q'):
        courses.append(sln)
    else:
        scheduling = False

# Beginning the UW account session
check_url = "https://sdb.admin.uw.edu/timeschd/uwnetid/sln.asp?QTRYR=WIN+2018&SLN="+sln1
login(user, pwd, check_url)

#Check courses and open registration when one opens
checking = True
while(checking):
    checking = False
    for course in courses:
        target_url = "https://sdb.admin.uw.edu/timeschd/uwnetid/sln.asp?QTRYR=WIN+2018&SLN="+course
        isOpen = checkOpen(target_url)
        if(not isOpen):
            checking = True
        else:
            print(course + " is open!")
    print('.')
    sleep(1)
    if(not checking):
        # register(courses)
        webbrowser.open_new("https://sdb.admin.uw.edu/students/uwnetid/register.asp")

print('Done.')
