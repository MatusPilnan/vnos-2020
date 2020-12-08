# BrewSessionStatusApi

All URIs are relative to *http://127.0.0.1:5000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**deleteBrewStatus**](BrewSessionStatusApi.md#deleteBrewStatus) | **DELETE** /status | Reset state - unselect any selected recipe
[**getBrewStatus**](BrewSessionStatusApi.md#getBrewStatus) | **GET** /status | Get currently selected recipe with steps


<a name="deleteBrewStatus"></a>
# **deleteBrewStatus**
> deleteBrewStatus()

Reset state - unselect any selected recipe

### Parameters
This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined

<a name="getBrewStatus"></a>
# **getBrewStatus**
> BrewSession getBrewStatus()

Get currently selected recipe with steps

### Parameters
This endpoint does not need any parameter.

### Return type

[**BrewSession**](../Models/BrewSession.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

