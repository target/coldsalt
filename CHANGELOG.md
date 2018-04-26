# Changelog

## v0.7.1  

### New Features  
- Added some robustness to the way variables are handled with Curl requests with JSON data. It's still not perfect, but it's better.    


## v0.7.0  

This version is a Release Candidate for version 1.0. While more testing is needed, this version should support all methods and body contents for Curl, Postman, and Swagger.  

### New Features  
- Enhanced support for Curl with data elements. `-d` and `--data` should both parse correctly now. JSON and form encoded should parse as well. Placeholders can be injected with variables as well.  
- Minor text changes on ERROR messages.   
- Cleaned up a stray print statement.  


## v0.6.0  

### New Features  
- Added initial support for request bodies for Curl. Initial code supports JSON specified with -d.  

### Known Issues  
- Other forms of data, such as --data or form encoded, won't parse right now. More to come. TBD.
- Curl parser might not inject variables into request bodies yet. I should probably test if it does. It might. But it might not. No promises.   


## v0.5.1

### Fixes  
- Added some error handling for parsing Swagger files without Summary fields.


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
