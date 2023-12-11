from fastapi import FastAPI
from database import create_table, pokemons, get_filtered_pokemon_data, populate_database, fetch_pokemon_data
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await create_table()
    if not pokemons:
        await fetch_pokemon_data()
        await populate_database()

@app.get("/api/v1/pokemons")
async def get_pokemons_from_db(name: str = None, type: str = None):
    pokemon_data = await get_filtered_pokemon_data(name, type)
    return pokemon_data