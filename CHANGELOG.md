# Changelog

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
