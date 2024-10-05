import asyncio
import aiohttp
import more_itertools
from sqlalchemy import select
from models import SessionDB, SwapiPeople, init_orm


MAX_REQUESTS = 5


async def get_people(person_id, session):
    response = await session.get(f"https://swapi.dev/api/people/{person_id}/")
    json_data = await response.json()
    person_info = {}
    necessary_info = ('species', 'starships', 'vehicles')
    if json_data.get('films'):
        if len(json_data['films']):
            coros_f = (session.get(f"{film_url}") for film_url in json_data['films'])
            films = await asyncio.gather(*coros_f)
            coros_f_r = (film.json() for film in films)
            films_json = await asyncio.gather(*coros_f_r)
            films_titles = (film['title'] for film in films_json)
            films_str = ', '.join(films_titles)
            person_info['films'] = films_str
    if json_data.get('homeworld'):
        response = await session.get(f"{json_data['homeworld']}")
        hw_json = await response.json()
        person_info['homeworld'] = hw_json['name']
    for info_type in necessary_info:
        if json_data.get(f'{info_type}'):
            if len(json_data[f'{info_type}']):
                coros_i = (session.get(f"{elem}") for elem in json_data[f'{info_type}'])
                infos = await asyncio.gather(*coros_i)
                coros_i_r = (info.json() for info in infos)
                infos_json = await asyncio.gather(*coros_i_r)
                infos_titles = (info['name'] for info in infos_json)
                person_info[f'{info_type}'] = ', '.join(infos_titles)
    return json_data, person_info


async def insert_people(people_list):
    async with (SessionDB() as session):
        for person_tuple in people_list:
            result = await session.execute(
                select(SwapiPeople).where(SwapiPeople.name == person_tuple[0].get('name'),
                                          SwapiPeople.birth_year == person_tuple[0].get('birth_year'),
                                          SwapiPeople.gender == person_tuple[0].get('gender'),
                                          SwapiPeople.height == person_tuple[0].get('height'))
            )
            if not result.first():
                session.add(SwapiPeople(birth_year=person_tuple[0].get('birth_year'),
                                        eye_color=person_tuple[0].get('eye_color'),
                                        films=person_tuple[1].get('films'),
                                        gender=person_tuple[0].get('gender'),
                                        hair_color=person_tuple[0].get('hair_color'),
                                        height=person_tuple[0].get('height'),
                                        homeworld=person_tuple[1].get('homeworld'),
                                        mass=person_tuple[0].get('mass'),
                                        name=person_tuple[0].get('name'),
                                        skin_color=person_tuple[0].get('skin_color'),
                                        species=person_tuple[1].get('species'),
                                        starships=person_tuple[1].get('starships'),
                                        vehicles=person_tuple[1].get('vehicles'))
                            )

        await session.commit()


async def main():
    await init_orm()
    async with aiohttp.ClientSession() as session_http:
        id_list = list(range(1, 84))
        id_list.remove(17)
        coros = (get_people(i, session_http) for i in id_list)
        for coros_chunk in more_itertools.chunked(coros, MAX_REQUESTS):
            people_list = await asyncio.gather(*coros_chunk)
            task = asyncio.create_task(insert_people(people_list))
            await task


asyncio.run(main())
