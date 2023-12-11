from fastapi import FastAPI
import requests
import asyncpg
import asyncio

app = FastAPI()

# Your PostgreSQL database credentials
DATABASE_URL = "postgresql://username:password@localhost/db_name"

url = "https://pokeapi.co/api/v2/pokemon/?limit=10"  # Limiting to the first 5 Pokémon for demonstration
res = requests.get(url)

if res.status_code != 200:
    print('Error during fetch')
    exit()

pokemons = res.json()['results']

# Function to create a PostgreSQL table
async def create_table():
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

# Function to insert data into the PostgreSQL table
async def insert_data(pokemon_data):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        INSERT INTO pokemon_data (name, image_url, types)
        VALUES ($1, $2, $3)
    ''', pokemon_data["name"], pokemon_data["image_url"], pokemon_data["types"])
    await conn.close()

@app.on_event("startup")
async def startup_event():
    await create_table()

@app.get("/api/v1/pokemons")
async def get_pokemons():
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

            # Queue the data insertion task
            tasks.append(insert_data(pokemon_info))

    # Execute all insertion tasks concurrently
    await asyncio.gather(*tasks)
    return {"message": "Data inserted into PostgreSQL"}
