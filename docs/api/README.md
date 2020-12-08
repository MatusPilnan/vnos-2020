# Documentation for Var:Pivo API

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *http://127.0.0.1:5000*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*BrewSessionStatusApi* | [**deleteBrewStatus**](Apis/BrewSessionStatusApi.md#deletebrewstatus) | **DELETE** /status | Reset state - unselect any selected recipe
*BrewSessionStatusApi* | [**getBrewStatus**](Apis/BrewSessionStatusApi.md#getbrewstatus) | **GET** /status | Get currently selected recipe with steps
*RecipeStepsApi* | [**deleteStepStart**](Apis/RecipeStepsApi.md#deletestepstart) | **DELETE** /step/{stepId} | Finish specified step
*RecipeStepsApi* | [**postStepStart**](Apis/RecipeStepsApi.md#poststepstart) | **POST** /step/{stepId} | Start specified step
*RecipesApi* | [**getRecipe**](Apis/RecipesApi.md#getrecipe) | **GET** /recipe/{recipeId} | Get single recipe
*RecipesApi* | [**getRecipeList**](Apis/RecipesApi.md#getrecipelist) | **GET** /recipe | Retrieve all available recipes
*RecipesApi* | [**postRecipe**](Apis/RecipesApi.md#postrecipe) | **POST** /recipe/{recipeId} | Select recipe and start brew session
*ScaleApi* | [**deleteScaleRes**](Apis/ScaleApi.md#deletescaleres) | **DELETE** /scale | Tare the scale
*ScaleApi* | [**patchScaleRes**](Apis/ScaleApi.md#patchscaleres) | **PATCH** /scale | Start scale calibration
*ScaleApi* | [**putScaleRes**](Apis/ScaleApi.md#putscaleres) | **PUT** /scale | Find scale reference units, after weight was PUT on the scale
*WSApi* | [**getWebSocketKeg**](Apis/WSApi.md#getwebsocketkeg) | **GET** /brizolit/je/cesta/neprestrelna/vesta | Resource format for WS messages
*WSApi* | [**postWebSocketKeg**](Apis/WSApi.md#postwebsocketkeg) | **POST** /brizolit/je/cesta/neprestrelna/vesta | Format of WS message with temperature


<a name="documentation-for-models"></a>
## Documentation for Models

 - [BrewSession](Models/BrewSession.md)
 - [Ingredient](Models/Ingredient.md)
 - [Recipe](Models/Recipe.md)
 - [RecipeList](Models/RecipeList.md)
 - [RecipeListStyle](Models/RecipeListStyle.md)
 - [RecipeStep](Models/RecipeStep.md)
 - [StepsList](Models/StepsList.md)
 - [Temperature](Models/Temperature.md)
 - [WSKeg](Models/WSKeg.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

All endpoints do not require authorization.
