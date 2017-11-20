# COLDSALT

Coldsalt is a simple Python program to speed up ingesting API data for penetration testing.

## Getting Started

Written and tested with Python 2.7.10. Not tested under Python 3.

### Prerequisites

Coldsalt uses the Requests library.   

To see if you have Requests installed, use the following command (assuming you use pip):  
```shell
pip show requests
```

To install Requests with pip, use the following command:  
```shell
pip install requests
```

### Optional functionality

Coldsalt has hooks to use BurpBuddy to automatically populate Intruder and Repeater.

You can get BurpBuddy here: https://github.com/tomsteele/burpbuddy/releases  

Coldsalt was developed and tested with BurpBuddy v3.0.0-BETA.

## Running Coldsalt

Usage example:
```
python coldsalt.py --mode swagger -i swagger_example.json --checkonly
python coldsalt.py --mode postman -i postman_example.json -e environment.json --output awesome.csv

-h, --help            show this help message and exit
-a, --allmethods      Make API calls for all HTTP methods including state
                      change related methods.
--burpbuddy BURPBUDDY
                      IP:port of Burp Budy instance. Defaults to
                      localhost:8081.
--checkonly           enable debug mode. No requests will be sent
-c CONTENTTYPE, --contenttype CONTENTTYPE
                      Force or override Content-Type on requests
-e ENVIRONMENT, --environment ENVIRONMENT
                      The environment.json file to parse.
--headers HEADERS     The headers.json file to parse.
-i INPUT, --input INPUT
                      The JSON collection file, Postman or Swagger, to
                      parse.
--mode {curl,postman,swagger}
                      Which mode, or collection type, to use. Choices are
                      'curl', 'postman', or 'swagger'
--output OUTPUT       write output/audit log to a csv
--proxy PROXY         IP:Port of proxy to use. Defaults to localhost:8080.
-v, --verbose         Enable verbose output.
-x, --xperimental     enable Xperimental Burp mode

```

By default, Coldcalt will only send GET, HEAD, and OPTION requests. You can override this with the -a and --allmethods flags.

If you're unsure about the quality of the documentation provided to you by the project team, start with the --checkonly flag. This will run the "parser" "engine" and look for missing parameters.  

If you do not have an environment file, COLDSALT will create a file stub for you. You can copypasta the output into your file editor of choice. Be sure to clean up errant line breaks and update the values.

Even if you have an environment file, if there are placeholders/variables defined in your collection file that are not defined in your environment file, COLDSALT will still output templated key value pairs for the missing parameters.

Once all the things check out, make sure you have Burp running on 8080 and run the script again.

### Supported Formats

 - Postman v2
 - Swagger
 - curl

If you are using a Postman file, make sure it is Postman v2.

To use curl requests, make sure they are in a text file, one request per line with the host at the end of the command. Generally, you can get a file ready with a combo of grep and awk.

### Setting Headers

Suppose you have a Swagger or Postman file that doesn't have any placeholders for required headers, what then?

Coldsalt gives you two options.  
``` -c CONTENTTYPE, --contenttype CONTENTTYPE ``` can be used to set an arbitrary Content-Type header.  
``` --headers HEADERS ``` lets you specify a json file that can contain any number of headers in the following format:
```
{"name": "generic header file",
"values": [{"key": "foo", "value": "bar"},
	{"key": "X-Test", "value": "true"}
	]}
```

Headers specified with ```--headers``` will override any duplicated headers from within the Swagger or Postman files.  
Content-Type set by ```-c``` will override all other Content-Type values.  

## Contributing

Please see [Contributing](/CONTRIBUTING.md).

## License

This project is licensed under the Apache License v2. Please see [License](/LICENSE) for more details.
