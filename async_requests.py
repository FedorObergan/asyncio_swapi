import asyncio
import aiohttp
import more_itertools
from models import SessionDB, SwapiPeople, init_orm


MAX_REQUESTS = 5


async def get_people(person_id, session):
    response = await session.get(f"https://swapi.dev/api/people/{person_id}/")
    json_data = await response.json()
    films = []
    films_str = ''
    person_info = {}
    person_info['homeworld'] = ''
    person_info['species'] = ''
    person_info['starships'] = ''
    person_info['vehicles'] = ''
    necessary_info = ('species', 'starships', 'vehicles')
    if json_data.get('films'):
        if len(json_data['films']):
            for film_url in json_data['films']:
                response = await session.get(f"{film_url}")
                film_json = await response.json()
                films.append(film_json['title'])
            films_str = ', '.join(films)
    if json_data.get('homeworld'):
        response = await session.get(f"{json_data['homeworld']}")
        hw_json = await response.json()
        person_info['homeworld'] = hw_json['name']
    for info_type in necessary_info:
        if json_data.get(f'{info_type}'):
            if len(json_data[f'{info_type}']):
                info = []
                for elem in json_data[f'{info_type}']:
                    response = await session.get(f"{elem}")
                    info_json = await response.json()
                    info.append(info_json['name'])
                person_info[f'{info_type}'] = ', '.join(info)
    return (json_data, films_str, person_info.get('homeworld'), person_info.get('species'),
            person_info.get('starships'), person_info.get('vehicles'))


async def insert_people(people_list):
    async with (SessionDB() as session):
        orm_model_list = []
        for person_tuple in people_list:
            orm_model_list.append(SwapiPeople(birth_year=person_tuple[0].get('birth_year'),
                                              eye_color=person_tuple[0].get('eye_color'),
                                              films=person_tuple[1],
                                              gender=person_tuple[0].get('gender'),
                                              hair_color=person_tuple[0].get('hair_color'),
                                              height=person_tuple[0].get('height'),
                                              homeworld=person_tuple[2],
                                              mass=person_tuple[0].get('mass'),
                                              name=person_tuple[0].get('name'),
                                              skin_color=person_tuple[0].get('skin_color'),
                                              species=person_tuple[3],
                                              starships=person_tuple[4],
                                              vehicles=person_tuple[5])
                                  )
        session.add_all(orm_model_list)
        await session.commit()


async def main():
    await init_orm()
    async with aiohttp.ClientSession() as session_http:
        id_list = list(range(1, 84))
        id_list.remove(17)
        coros = (get_people(i, session_http) for i in id_list)
        for coros_chunk in more_itertools.chunked(coros, MAX_REQUESTS):
            people_list = await asyncio.gather(*coros_chunk)
            asyncio.create_task(insert_people(people_list))

        tasks = asyncio.all_tasks()
        main_task = asyncio.current_task()
        tasks.remove(main_task)
        await asyncio.gather(*tasks)

