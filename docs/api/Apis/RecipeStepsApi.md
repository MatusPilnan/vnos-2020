# RecipeStepsApi

All URIs are relative to *http://127.0.0.1:5000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**deleteStepStart**](RecipeStepsApi.md#deleteStepStart) | **DELETE** /step/{stepId} | Finish specified step
[**postStepStart**](RecipeStepsApi.md#postStepStart) | **POST** /step/{stepId} | Start specified step


<a name="deleteStepStart"></a>
# **deleteStepStart**
> RecipeStep deleteStepStart(stepId)

Finish specified step

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stepId** | **String**| Step ID | [default to null]

### Return type

[**RecipeStep**](../Models/RecipeStep.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="postStepStart"></a>
# **postStepStart**
> RecipeStep postStepStart(stepId)

Start specified step

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stepId** | **String**| Step ID | [default to null]

### Return type

[**RecipeStep**](../Models/RecipeStep.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

