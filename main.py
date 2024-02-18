# This is a sample Python script.
from dataclasses import dataclass
import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# BASE_URL = "https://djinni.co/jobs/?primary_keyword=Python"
BASE_URL = "https://djinni.co"
HOME_URL = urljoin(BASE_URL, "/jobs/?primary_keyword=Python")


@dataclass
class Vacancy:
    company: str
    title: str
    description: str
    link: str


def parse_single_vacancy(vacancy: BeautifulSoup) -> Vacancy:
    description = vacancy.select_one(".job-list-item__description > span")["data-original-text"].strip()
    pattern = r'<\/?(br|b)\s?\/?>'
    description = re.sub(pattern, '', description)
    return Vacancy(
        company=vacancy.select_one(".d-flex > a.mr-2").text.strip(),
        title=vacancy.select_one(".job-list-item__link").text.strip(),
        description=description,
        link=urljoin(BASE_URL, vacancy.select_one(".job-list-item__link")["href"].strip())
    )


def get_home_vacancies() -> [Vacancy]:
    page = requests.get(HOME_URL).content
    soup = BeautifulSoup(page, "html.parser")

    vacancies = soup.find_all(class_='job-list-item position-relative')

    result = [parse_single_vacancy(vacancy) for vacancy in vacancies]

    print(result)


def main():
    get_home_vacancies()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
