# RecipesApi

All URIs are relative to *http://127.0.0.1:5000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getRecipe**](RecipesApi.md#getRecipe) | **GET** /recipe/{recipeId} | Get single recipe
[**getRecipeList**](RecipesApi.md#getRecipeList) | **GET** /recipe | Retrieve all available recipes
[**postRecipe**](RecipesApi.md#postRecipe) | **POST** /recipe/{recipeId} | Select recipe and start brew session


<a name="getRecipe"></a>
# **getRecipe**
> Recipe getRecipe(recipeId)

Get single recipe

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **recipeId** | **String**| Recipe ID | [default to null]

### Return type

[**Recipe**](../Models/Recipe.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getRecipeList"></a>
# **getRecipeList**
> RecipeList getRecipeList()

Retrieve all available recipes

    This docstring will show up as the description and short-description for the openapi docs for this route.

### Parameters
This endpoint does not need any parameter.

### Return type

[**RecipeList**](../Models/RecipeList.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="postRecipe"></a>
# **postRecipe**
> StepsList postRecipe(recipeId)

Select recipe and start brew session

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **recipeId** | **String**| Recipe ID | [default to null]

### Return type

[**StepsList**](../Models/StepsList.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

