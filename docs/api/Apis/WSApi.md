# WSApi

All URIs are relative to *http://127.0.0.1:5000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getWebSocketKeg**](WSApi.md#getWebSocketKeg) | **GET** /brizolit/je/cesta/neprestrelna/vesta | Resource format for WS messages
[**postWebSocketKeg**](WSApi.md#postWebSocketKeg) | **POST** /brizolit/je/cesta/neprestrelna/vesta | Format of WS message with temperature


<a name="getWebSocketKeg"></a>
# **getWebSocketKeg**
> WSKeg getWebSocketKeg()

Resource format for WS messages

### Parameters
This endpoint does not need any parameter.

### Return type

[**WSKeg**](../Models/WSKeg.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="postWebSocketKeg"></a>
# **postWebSocketKeg**
> Temperature postWebSocketKeg()

Format of WS message with temperature

### Parameters
This endpoint does not need any parameter.

### Return type

[**Temperature**](../Models/Temperature.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

