####
## CS_Parser_Swagger
## Simple helper type class for parsing Swagger files into ColdSalt internal format
## Author: jason nordenstam
####

import sys
import json

standard_methods = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE", "OPTIONS", "TRACE"]


class CSParserSwagger:

    def __init__(self, verbose = False):
        self.verbose = verbose

    def pickEnvironment(self, endpoints):
        print "\nMultiple environment endpoints detected. Please Select one."
        for endpoint in endpoints:
            print "%s - %s: %s: %s" % (endpoint['count'], endpoint['accessibility'], endpoint['type'], endpoint['url'])
        selection = int(raw_input("Select: "))

        return selection

    def parseSwagger(self, inputfile):
        endpoint_collection = []
        print "\nParsing Swagger collection file %s" % str(inputfile)
        swagger_data = json.loads(open(inputfile).read())
        swagger_items = swagger_data["paths"]
        if(self.verbose):
            print swagger_data["info"]["title"]

        # swagger can define URLs in a few different ways
        # first let's check for the "endpoints" definitions
        if "x-api-definition" in swagger_data:
            if "endpoints" in swagger_data["x-api-definition"]:
                # even with "endpoints" there are external and internal options
                endpoints = []
                endpoint_count = 0
                for accessibility in swagger_data["x-api-definition"]["endpoints"].keys():
                    for endpoint_key in  swagger_data["x-api-definition"]["endpoints"][accessibility].keys() :
                        if swagger_data["x-api-definition"]["endpoints"][accessibility][endpoint_key] is not None:
                            point = {}
                            point['count'] = endpoint_count
                            point['accessibility'] = accessibility
                            point['type'] = endpoint_key
                            point['url'] = swagger_data["x-api-definition"]["endpoints"][accessibility][endpoint_key]
                            endpoints.append(point)
                            endpoint_count = endpoint_count + 1
                _error_count = 0
                # if there are mulitple environments, prompt the user to pick one
                _selection = self.pickEnvironment(endpoints)
                # check and see if it's in range
                while _selection > endpoint_count - 1 or _selection < 0:
                    _error_count = _error_count + 1
                    print "Invalid selection. Pick an environment between 0 and %s" % (endpoint_count-1)
                    _selection = self.pickEnvironment(endpoints)
                    if _error_count > 5:
                        print "Stop messing around."
                        sys.exit(1)

                base_url = endpoints[_selection]["url"]
        else:
            #if there aren't endpoints, try to use host and basePath
            # but also check for a scheme
            if "schemes" in swagger_data:
                base_url = swaggers_data["schemes"] + swagger_data["host"] + swagger_data["basePath"]
            else:
                base_url = "http://" + swagger_data["host"] + swagger_data["basePath"]

        if(self.verbose):
            print "base_url= " + base_url

        # swagger can define parameters in several ways so...
        # first we'll check for 'global' parameters
        global_params = {}
        try:
            if swagger_data["parameters"] is not None:
                for param in swagger_data["parameters"].keys():
                    #print param
                    _local_param = {}
                    _local_param["name"] = swagger_data["parameters"][param]["name"]
                    _local_param["in"] = swagger_data["parameters"][param]["in"]

                    global_params[swagger_data["parameters"][param]["name"]] = _local_param
        except KeyError:
            print "No global parameters found."

        for path_key in swagger_items.keys():
            for method_key in swagger_items[path_key].keys():
                if method_key.upper() in standard_methods:
                    api_endpoint = {}
                    headers = {}
                    queryString = {}

                    api_endpoint['name'] = swagger_items[path_key][method_key]["summary"]

                    api_endpoint['method'] = method_key.upper()
                    api_endpoint['body'] = ""
                    # handle parameters
                    # swagger parameters can be defined in several ways
                    # first check if they are defined under
                    if "parameters" in swagger_items[path_key][method_key].keys() :
                        for param in swagger_items[path_key][method_key]["parameters"]:
                            _local_param = param
                            if "$ref" in param:
                                # if the param references a global param, grab that param
                                # and 'overwrite' the 'loop' 'copy'
                                param_ref = param["$ref"].split("#/parameters/")[1]
                                _local_param = global_params[param_ref]

                            if(_local_param["in"] == "header"):
                                headers[_local_param["name"]] = "{" + _local_param["name"] + "}"
                                global_params[_local_param["name"]] = _local_param

                            if(_local_param["in"] == "query"):
                                queryString[_local_param["name"]] = "{" + _local_param["name"] + "}"
                                global_params[_local_param["name"]] = _local_param

                            if(_local_param["in"] == "body"):
                                # get the ref....
                                _body = {}
                                _raw_body = swagger_data["definitions"][_local_param["schema"]["$ref"].split("#/definitions/")[1]]["properties"]
                                for _body_item in _raw_body.keys():
                                    _body[_body_item] = "{%s}" % (_body_item)
                                api_endpoint["body"] = str(_body)
                    # format querysting into url
                    if(bool(queryString)):
                        formatted= "&".join("%s=%s" % (key, queryString[key]) for key in queryString.keys())
                        api_endpoint['url'] = base_url + path_key + "?" + formatted
                    else:
                        api_endpoint['url'] = base_url + path_key
                    api_endpoint['headers'] = headers
                    # add to dictionary
                    endpoint_collection.append(api_endpoint)
                    if(self.verbose):
                        print "    " +  api_endpoint["name"]
                        print "      " + api_endpoint["url"]
                        print "      " + api_endpoint["method"]
                        print "      " + str(api_endpoint["body"])
                        print "      ----------------"
        return endpoint_collection
