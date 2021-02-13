import httpx


class BrewersFriend:

    @staticmethod
    async def get_beerxml_recipe(recipe_id=None, recipe_url=None):
        if not recipe_id:
            if not recipe_url:
                raise ValueError("No ID or URL specified!")
            else:
                recipe_id = BrewersFriend.recipe_id_from_url(recipe_url)

        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.get(
                f"https://www.brewersfriend.com/homebrew/recipe/beerxml1.0/{recipe_id}")
            if response.status_code == 200:
                if response.headers['Content-Type'].startswith('text/xml'):
                    return response.text, recipe_id
                elif 'Recipe Not Found' in response.text:
                    raise FileNotFoundError
                elif 'Permission Error' in response.text:
                    raise PermissionError
            return None, None

    @staticmethod
    def recipe_id_from_url(recipe_url: str):
        recipe_url = recipe_url.rstrip('/')
        return recipe_url.split('/')[-2]
