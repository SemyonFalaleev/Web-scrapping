import requests
import bs4
from fake_headers import Headers
import re
from pprint import pprint
from tqdm import tqdm
import json

def search_key_word(list_key_word, description):
    for word in list_key_word:
        pattern = re.compile(rf"{word}", re.IGNORECASE)
        if re.search(pattern, description.text):
            return True
    return False

def get_link_vacancy(link_to_recource):
    response = requests.get(f"{link_to_recource}", headers=get_fake_headers())
    soup = bs4.BeautifulSoup(response.text, features='lxml')
    vacancy_card = soup.findAll("span", class_="serp-item__title-link-wrapper")
    vacancy_link_list = [vacancy.find("a", class_="bloko-link")["href"] for vacancy in vacancy_card]
    return vacancy_link_list

def get_fake_headers():
        return Headers().generate()

def get_next_page_link(before_page_link):
    response = requests.get(f"{before_page_link}", headers=get_fake_headers())
    soup = bs4.BeautifulSoup(response.text, features='lxml')
    next_page_link = soup.find('a', attrs={'data-qa':'pager-next', 'class': 'bloko-button'})
    if next_page_link == None:
        return False
    else:
        return f'https://spb.hh.ru{next_page_link["href"]}'

def get_info_vacancy(link_list, result_dict):
    info_dict = {}
    for link in tqdm(link_list):
        response = requests.get(f'{link}', headers=get_fake_headers())
        soup = bs4.BeautifulSoup(response.text, features='lxml')
        text_description = soup.find('div', class_="g-user-content")
        if text_description == None:
            text_description = soup.find('div', class_="tmpl_hh_content")
        try:
            if not search_key_word(['Django', 'Flask'], text_description):
                continue
        except Exception as ex:
            print("description")
            print(ex)
            print(link)
            pprint(response)
            pprint(text_description)
            return 
        
        salary = soup.find('span', class_="magritte-text___pbpft_3-0-8 magritte-text_style-primary___AQ7MW_3-0-8 magritte-text_typography-label-1-regular___pi3R-_3-0-8")
        if salary == None:
            salary = soup.find('div', attrs={"data-qa": "vacancy-salary"})
        try:
            salary_str =salary.text.replace("\xa0", " ")
        except Exception as ex:
            print("salary")
            print(ex)
            print(link)
            pprint(response)
            pprint(salary)
            return 

        try:
            town_str = soup.find("div" ,
            class_="magritte-text___pbpft_3-0-8 magritte-text_style-primary___"\
                "AQ7MW_3-0-8 magritte-text_typography-paragraph-2-regular___VO638_3-0-8")
            if town_str == None:
                town_str = soup.find("a" ,
                class_="magritte-link___b4rEM_4-1-2 magritte-link_style_neutral"\
                    "___iqoW0_4-1-2 magritte-link_block___Lk0iO_4-1-2")  
            town_str = town_str.text
        except Exception as ex:
            print("town")
            print(ex)
            print(link)
            pprint(response)
            pprint(soup.find('a', attrs={'data-qa':'vacancy-view-location'}))   
            return
        try:
            company_str = soup.find('span', class_="vacancy-company-name").text
        except Exception as ex:
            print("company")
            print(ex)
            print(link)
            pprint(response)
            pprint(soup.find('span', class_="vacancy-company-name"))
            return 
        try:
            vacancy_name = soup.find('h1', class_="bloko-header-section-1").text
        except Exception as ex:
            print("vacancy")
            print(ex)
            print(link)
            pprint(response)
            pprint(soup.find('h1', class_="bloko-header-section-1"))
            return 
        if vacancy_name not in result_dict:
            info_dict[vacancy_name]= {}
            info_dict[vacancy_name]['salary']=salary_str
            info_dict[vacancy_name]['town']=town_str
            info_dict[vacancy_name]['company']=company_str
            info_dict[vacancy_name]['link']=link
        else:
            vacancy_name = f'{vacancy_name}({company_str})'
            info_dict[vacancy_name]= {}
            info_dict[vacancy_name]['salary']=salary_str
            info_dict[vacancy_name]['town']=town_str
            info_dict[vacancy_name]['company']=company_str
            info_dict[vacancy_name]['link']=link
    return info_dict

def main(link):
    all_result = {}
    while link != False:
        link_vacancy = get_link_vacancy(link)
        pprint(link)
        result_dict = get_info_vacancy(link_vacancy, result_dict=all_result)
        if type(result_dict) != type({}):
            break
        all_result.update(result_dict)
        print(all_result)
        with open("result.json", 'w', encoding='utf-8') as file:
            json.dump(all_result, file, ensure_ascii=False, indent=4)
        link = get_next_page_link(link)
   
    

if __name__ == "__main__":
    main("https://spb.hh.ru/search/vacancy?text=python&area=1&area=2")




