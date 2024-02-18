import csv
import logging
import sys
from dataclasses import dataclass, fields, astuple
import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://djinni.co"
HOME_URL = urljoin(BASE_URL, "/jobs/?primary_keyword=Python")

VACANCIES_CSV_PATH = "vacancies.csv"


@dataclass
class Vacancy:
    company: str
    title: str
    description: str
    link: str


VACANCY_FIELD = [field.name for field in fields(Vacancy)]


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)4s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


# parse page and create a new class Vacancy of each attribute
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


def get_num_pages(page_soup: BeautifulSoup) -> int:
    # find block list with pagination
    pagination = page_soup.select_one(".pagination_with_numbers")

    if pagination is None:
        return 1

    # find late number like int
    return int(pagination.select("li")[-2].text.split()[0])


def get_single_page_vacancies(page_soup: BeautifulSoup) -> [Vacancy]:
    vacancies = page_soup.find_all(class_='job-list-item position-relative')

    return [parse_single_vacancy(vacancy) for vacancy in vacancies]


def get_home_vacancies() -> [Vacancy]:
    logging.info("Start parsing vacancies")
    page = requests.get(HOME_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    # find num of pages in the web
    num_pages = get_num_pages(first_page_soup)

    # create the first page with vacancies
    all_vacancies = get_single_page_vacancies(first_page_soup)

    # in page add query parameter "page" as a second arg in requests.get
    for page_num in range(2, num_pages + 1):
        logging.info(f"Start parsing page: {page_num}")
        page = requests.get(HOME_URL, {"page": page_num}).content
        soup = BeautifulSoup(page, "html.parser")
        all_vacancies.extend(get_single_page_vacancies(soup))

    return all_vacancies


def write_vacancies_to_csv(vacancies: [Vacancy]) -> None:
    with open(VACANCIES_CSV_PATH, "w") as file:
        writer = csv.writer(file)
        writer.writerow(VACANCY_FIELD)
        writer.writerows([astuple(vacancy) for vacancy in vacancies])


def main():
    vacancies = get_home_vacancies()
    write_vacancies_to_csv(vacancies)


if __name__ == '__main__':
    main()
