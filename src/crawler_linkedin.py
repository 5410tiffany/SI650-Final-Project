import os, time, json
from selenium import webdriver


def sign_in(driver,url,account,password):
    
    driver.get(url)
    
    session_key = driver.find_element_by_css_selector('#session_key')
    session_key.send_keys(account)
    
    session_password = driver.find_element_by_css_selector('#session_password')
    session_password.send_keys(password)

    btn_sign_in = driver.find_element_by_css_selector('.sign-in-form__submit-button')
    btn_sign_in.click()

def parseProfile(driver,url_profile,verbose = False):
    t_sleep = 0.5
    profile = {
            "Education":[],
            "Experience":[]
    }


    driver.get(url_profile)
    time.sleep(t_sleep)
    driver.execute_script("document.body.style.zoom='30%'")
    time.sleep(t_sleep)

    js_cmd = "var q=document.getElementsByClassName('experience-section')[0].scrollIntoView()"
    driver.execute_script(js_cmd)
    experience_section = driver.find_element_by_css_selector('#experience-section')    
    exp_list = experience_section.find_elements_by_tag_name('li')
    print('%d work exp'%(len(exp_list)))
    for idx_exp, exp in enumerate(exp_list):
        exp_json = {
            "title"  : None,
            "company": None,
            "period" : None,
            "description": None
        }

        try:
            exp_json['title'] = exp.find_element_by_tag_name('h3').get_attribute('innerText')
        except Exception as e:
            print(e)

        try:
            exp_json['company'] = exp.find_element_by_class_name('pv-entity__secondary-title').get_attribute('innerText')
        except Exception as e:
            print(e)

        try:
            exp_json['period'] = exp.find_element_by_class_name('pv-entity__date-range').find_elements_by_tag_name('span')[1].get_attribute('innerText')
        except Exception as e:
            print(e)

        try:
            exp_json['description'] = exp.find_element_by_class_name('inline-show-more-text').get_attribute('innerText')
        except Exception as e:
            print(e)

        profile["Experience"].append(exp_json)

        if verbose:
            print('------------------------------- %d -------------------------------'%(idx_exp))
            for key,value in exp_json.items():
                if value == None:
                    value = ""
                print(key,value)

    js_cmd = "var q=document.getElementsByClassName('education-section')[0].scrollIntoView()"
    driver.execute_script(js_cmd)
    education_section = driver.find_element_by_css_selector('#education-section')
    edu_list = education_section.find_elements_by_tag_name('li')
    print('%d degree'%(len(edu_list)))
    for idx_edu, edu in enumerate(edu_list):
        edu_json = {
            "school": None,
            "degree": None,
            "major" : None,
            "period": None
        }
        try:
            degree_info = edu.find_element_by_class_name('pv-entity__degree-info')
        except Exception as e:
            print(e)

        try:
            edu_json['school'] = degree_info.find_element_by_class_name('pv-entity__school-name').get_attribute('innerText')
        except Exception as e:
            print(e)

        try: 
            program_info = degree_info.find_elements_by_tag_name('p')
            for item in program_info:
                key,value = item.text.split('\n')
                if key == "Degree Name":
                    edu_json['degree'] = value
                elif key == "Field Of Study":
                    edu_json['major'] = value
        except Exception as e:
            print(e)

        try: 
            edu_json['period'] = edu.find_element_by_class_name('pv-entity__dates').find_elements_by_tag_name('span')[-1].get_attribute('innerText')
        except Exception as e:
            print(e)

        profile["Education"].append(edu_json)
        
        if verbose:
            print('------------------------------- %d -------------------------------'%(idx_edu))
            for key,value in edu_json.items():
                if value == None:
                    value = ""
                print(key,value)
    return profile
cwd = os.getcwd()
path_driver = os.path.join( cwd,'browser_driver','chromedriver' )
path_data_json = os.path.join(  cwd,'dataset','data_json'  )
path_urls_profile = 'LinkedIn_profile_urls.txt'

url_sign_in = "https://www.linkedin.com/"
account = "ben0630884@gmail.com"
password = "010902084"


#url_profile = 'https://www.linkedin.com/in/hsuan-hsueh-huang/'

driver = webdriver.Chrome(path_driver)
sign_in(driver,url_sign_in,account,password)

with open(path_urls_profile) as f:
    lines = f.readlines()
    for idx_line, line in enumerate(lines):
        url_profile = line.rstrip()
        cv_name = os.path.basename(url_profile[:-1])
        print('------------------------',idx_line,url_profile)
        profile = parseProfile(driver,url_profile,True)
        with open(cv_name+'.json', "w") as outfile:
            json.dump(profile, outfile,indent=4)