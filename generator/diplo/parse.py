import os
import json
import asyncio
import aiohttp
from pprint import pprint

import requests


def parseFromApi():
    items = []
    url = "https://extapi.satbayev.university/diploma/1.0.1/getAll"
    for i in range(73):
        # for i in range(73):
        res = requests.post(url=url, headers={"Authorization": "Basic ZGlwbG9tYV9uZnQ6RGQxMjM0NTY="}, json={
            "PageId": i
        })
        if res.status_code == 200:
            body = json.loads(res.content)["result"]["items"]
            items.append(body)
            # for item in body:
            #     items.append(item)
            #     if item["Status"] == "Graduated":
            #         jsonItem = {
            #             "name_en": item["FIO"]["NameEn"],
            #             "name_kz": item["FIO"]["NameKz"],
            #             "name_ru": item["FIO"]["NameRu"],
            #             "speciality": item["Speciality"],
            #             "email": item["Email"] if item["Email"] and isinstance(item["Email"], str) else None,
            #             "grant": item["GrantTitle"] if item["GrantTitle"] and isinstance(item["GrantTitle"],
            #                                                                              str) else None,
            #             "gender": "мужской" if item["Sex"] == "M" else "женский",
            #             "city": item["City"] if item["City"] and isinstance(item["City"], str) else None,
            #             "nationality": item["Nationality"] if item["Nationality"] and isinstance(item["Nationality"],
            #                                                                                      str) else None,
            #             "iin": item["IIN"],
            #             "phone": item["Phone"] if item["Phone"] and isinstance(item["Phone"], str) else None,
            #             "gpa": item["GPA"] if item["GPA"] and isinstance(item["GPA"], float) else None,
            #             "region": item["Region"] if item["Region"] and isinstance(item["Region"], str) else None,
            #             "date_of_birth": item["BirthDate"],
            #             "with_honor": False if item["WithHonor"] == "N" else True,
            #             "year": item["Protocol"]["Date"],
            #
            #             "education_type": item["EducationType"],
            #             "study_direction": item["DirectionStudy"],
            #
            #             "degree": "Master" if item["DegreeType"] == 2 else "Bachelor"
            #         }
    with open("data-04-03-2024.json", "w", encoding="utf-8") as json_file:
        # Dump the JSON data to the file with proper encoding
        json.dump(items, json_file, ensure_ascii=False, indent=2)

parseFromApi()

