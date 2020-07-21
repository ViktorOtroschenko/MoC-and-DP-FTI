from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import time
import re
import random

headers = {'user-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

def hh(main_link, search_str, n_str):

    html = requests.get(main_link+'/search/vacancy?clusters=true&enable_snippets'
                                  '=true&text='+search_str+'&showClusters=true', headers=headers).text
    parsed_html = bs(html, 'lxml')

    jobs = []
    for i in range(n_str):
        jobs_block = parsed_html.find('div', {'class': 'vacancy-serp'})
        jobs_list = jobs_block.findChildren(recursive=False)
        for job in jobs_list:
            job_data = {}
            req = job.find('span', {'class': 'g-user-content'})
            if req is not None:
                main_info = req.findChild()
                job_name = main_info.getText()
                job_link = main_info['href']
                salary = job.find('div', {'class': 'vacancy-serp-item__compensation'})
                if not salary:
                    salary_min = None
                    salary_max = None
                    salary_currency = None
                else:
                    salary = salary.getText().replace(u'\xa0', u'')

                    salary = re.split(r'\s|-', salary)

                    if salary[0] == 'до':
                        salary_min = None
                        salary_max = int(salary[1])
                    elif salary[0] == 'от':
                        salary_min = int(salary[1])
                        salary_max = None
                    else:
                        salary_min = int(salary[0])
                        salary_max = int(salary[1])

                    salary_currency = salary[2]
                job_data['name'] = job_name
                job_data['salary_min'] = salary_min
                job_data['salary_max'] = salary_max
                job_data['salary_currency'] = salary_currency
                job_data['link'] = job_link
                job_data['site'] = main_link
                jobs.append(job_data)
        time.sleep(random.randint(1, 10))
        next_btn_block = parsed_html.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
        next_btn_link = next_btn_block['href']
        html = requests.get(main_link+next_btn_link, headers=headers).text
        parsed_html = bs(html, 'lxml')

    return jobs

search_str = 'Python'
n_str = 2
main_link = 'https://krasnodar.hh.ru'

def parser_hh(main_link, search_str, n_str):
    vacancy_date = []
    vacancy_date.extend(hh(main_link, search_str, n_str))

    df_hh = pd.DataFrame(vacancy_date)

    return df_hh

df_hh = parser_hh(main_link, search_str, n_str)
filename_hh = 'search_hh.csv'
df_hh.to_csv(filename_hh, index=False, encoding='utf-8')

print('End of search')