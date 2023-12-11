from fastapi import FastAPI
import requests
import asyncpg
import asyncio

app = FastAPI()
DATABASE_URL = "postgresql://robin:robin@localhost/pokemon"
pokemons = None  # Variable to store retrieved Pokemon data

# url = "https://pokeapi.co/api/v2/pokemon/?limit=100"
# res = requests.get(url)

async def fetch_pokemon_data():
    global pokemons
    url = "https://pokeapi.co/api/v2/pokemon/?limit=100"
    res = requests.get(url)

    if res.status_code == 200:
        pokemons = res.json()['results']

@app.on_event("startup")
async def startup_event():
    await create_table()
    if not pokemons:
        await fetch_pokemon_data()
        await populate_database()

async def create_table():# Function to create a PostgreSQL table
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS pokemon_data (
            id SERIAL PRIMARY KEY,
            name TEXT,
            image_url TEXT,
            types TEXT[]
        )
    ''')
    await conn.close()

async def insert_data(pokemon_data):# Function to insert data into the PostgreSQL table
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        INSERT INTO pokemon_data (name, image_url, types)
        VALUES ($1, $2, $3)
    ''', pokemon_data["name"], pokemon_data["image_url"], pokemon_data["types"])
    await conn.close()

async def get_all_pokemon_data():# Function to retrieve all data from the PostgreSQL table
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch('SELECT * FROM pokemon_data')
    await conn.close()
    return rows

async def populate_database():
    tasks = []
    for pokemon in pokemons:
        pokemon_url = pokemon['url']
        pokemon_res = requests.get(pokemon_url)

        if pokemon_res.status_code == 200:
            pokemon_data = pokemon_res.json()
            name = pokemon_data['name']
            image_url = pokemon_data['sprites']['front_default']
            types = [type_data['type']['name'] for type_data in pokemon_data['types']]

            pokemon_info = {
                "name": name,
                "image_url": image_url,
                "types": types
            }
            tasks.append(insert_data(pokemon_info))
    await asyncio.gather(*tasks)

async def get_filtered_pokemon_data(name: str = None, type: str = None):# Function to retrieve filtered data from the PostgreSQL table  
    conn = await asyncpg.connect(DATABASE_URL)
    query = 'SELECT * FROM pokemon_data WHERE true'
    params = []

    if name:
        query += ' AND name = $1'
        params.append(name.lower())

    if type:
        if not name:
            query += ' AND $1 = ANY(types)'
        else:
            query += ' AND $2 = ANY(types)'
        params.append(type.lower())

    rows = await conn.fetch(query, *params)
    await conn.close()
    return rows

@app.get("/api/v1/pokemons")
async def get_pokemons_from_db(name: str = None, type: str = None):
    pokemon_data = await get_filtered_pokemon_data(name, type)
    return pokemon_data
# async def get_pokemons_from_db(name: str = None, type: str = None):
#     tasks = []
#     for pokemon in pokemons:
#         pokemon_url = pokemon['url']
#         pokemon_res = requests.get(pokemon_url)

#         if pokemon_res.status_code == 200:
#             pokemon_data = pokemon_res.json()
#             name = pokemon_data['name']
#             image_url = pokemon_data['sprites']['front_default']
#             types = [type_data['type']['name'] for type_data in pokemon_data['types']]

#             pokemon_info = {
#                 "name": name,
#                 "image_url": image_url,
#                 "types": types
#             }
#             tasks.append(insert_data(pokemon_info))
#     await asyncio.gather(*tasks)
#     pokemon_data = await get_filtered_pokemon_data(name, type)
#     return pokemon_data
# async def get_pokemons():
#     tasks = []
#     for pokemon in pokemons:
#         pokemon_url = pokemon['url']
#         pokemon_res = requests.get(pokemon_url)

#         if pokemon_res.status_code == 200:
#             pokemon_data = pokemon_res.json()
#             name = pokemon_data['name']
#             image_url = pokemon_data['sprites']['front_default']
#             types = [type_data['type']['name'] for type_data in pokemon_data['types']]

#             pokemon_info = {
#                 "name": name,
#                 "image_url": image_url,
#                 "types": types
#             }
#             tasks.append(insert_data(pokemon_info))
#     await asyncio.gather(*tasks)
#     pokemon_data = await get_all_pokemon_data()
#     return pokemon_data
