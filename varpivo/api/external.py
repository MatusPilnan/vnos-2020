import httpx


class BrewersFriend:

    @staticmethod
    async def get_beerxml_recipe(recipe_id):
        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.get(
                f"https://www.brewersfriend.com/homebrew/recipe/beerxml1.0/{recipe_id}")
            if response.status_code == 200:
                if response.headers['Content-Type'].startswith('text/xml'):
                    return response.text
                elif 'Recipe Not Found' in response.text:
                    raise FileNotFoundError
                elif 'Permission Error' in response.text:
                    raise PermissionError
            return None
