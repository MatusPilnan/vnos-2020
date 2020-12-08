# ScaleApi

All URIs are relative to *http://127.0.0.1:5000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**deleteScaleRes**](ScaleApi.md#deleteScaleRes) | **DELETE** /scale | Tare the scale
[**patchScaleRes**](ScaleApi.md#patchScaleRes) | **PATCH** /scale | Start scale calibration
[**putScaleRes**](ScaleApi.md#putScaleRes) | **PUT** /scale | Find scale reference units, after weight was PUT on the scale


<a name="deleteScaleRes"></a>
# **deleteScaleRes**
> deleteScaleRes()

Tare the scale

### Parameters
This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined

<a name="patchScaleRes"></a>
# **patchScaleRes**
> patchScaleRes(grams)

Start scale calibration

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **grams** | **Integer**| Real weight used for calibration | [default to null]

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined

<a name="putScaleRes"></a>
# **putScaleRes**
> putScaleRes()

Find scale reference units, after weight was PUT on the scale

### Parameters
This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined

