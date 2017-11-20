# Changelog

## v0.5.0

- Added a new flag ```--headers``` to allow for arbitrary headers added to all requests.


## v0.4.1

### Fixes
- Fixed Swagger file parsing when body parameters are inline objects instead of references.


## v0.4

## New Features
- Added a new flag ```-c``` and ```--contenttype``` to force or override the content-type header sent on requests.

### Fixes
- When parsing body data for Swagger, the resulting string wasn't proper JSON. This has been fixed.  


## v0.3

### New Features  
- POST, PUT, and PATCH bodies should be populated from Swagger collections. A placeholder/variable is injected into the body for each parameter. The placeholder gets parsed before the request is sent just like any other parameter.


## v0.2

### New Features  
- Initial support of All Methods option. See below.  
- POST, PUT, and PATCH bodies should be populated from Postman collections.  

### Fixes
- Proxy strings should be concatenated correctly now.
- Parsing Postman files should be more robust.

### Known Issues  
- POST, PUT, and PATCH bodies from Swagger and Curl are not currently populated.  
