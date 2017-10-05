####
## CS_Parser_Postman
## Simple helper type class for parsing Postman files into ColdSalt internal format
## Author: jason nordenstam
####

import sys
import json


class CSParserPostman:

    def __init__(self, verbose = False):
        self.verbose = verbose


    def parsePostman(self, inputfile):
        endpoint_collection = []
        print "\nParsing postman collection file %s" % str(inputfile)
        postman_data = json.loads(open(inputfile).read())
        try:
            postman_items = postman_data["item"]
        except KeyError as ke:
            print "Key Error in postman file. Is it v2?"
            sys.exit("Invalid Postman File")

        if(self.verbose):
            print postman_data["info"]["name"]

        for endpoints in postman_items:

            if "item" not in endpoints:
                api_endpoint = {}
                headers = {}
                api_endpoint['name'] = endpoints["name"]
                if "raw" in endpoints["request"]["url"]:
                    api_endpoint['url'] = endpoints["request"]["url"]["raw"]
                else:
                    api_endpoint['url'] = endpoints["request"]["url"]
                api_endpoint['method'] =  endpoints["request"]["method"]
                # get headers
                for value in endpoints["request"]["header"]:
                    headers[value["key"]] = value["value"]

                if "body" in endpoints["request"]:
                    if "raw" == endpoints["request"]["body"]["mode"]:
                        api_endpoint["body"] = endpoints["request"]["body"]["raw"]
                    else:
                        api_endpoint["body"] = ""
                else:
                    api_endpoint["body"] = ""

                api_endpoint['headers'] = headers
                # once the data for an endpoint is parsed out, add it to dictionary
                endpoint_collection.append(api_endpoint)
                if(self.verbose):
                    print "  " +  endpoints["name"]
                    print "    " +  api_endpoint["name"]
                    print "      " + str(api_endpoint["url"])
                    print "      " + api_endpoint["method"]
                    print "      " + api_endpoint["body"]
                    print "      ----------------"
            else:
                for items in endpoints["item"]:

                    api_endpoint = {}
                    headers = {}
                    api_endpoint['name'] = items["name"]
                    api_endpoint['url'] = items["request"]["url"]
                    api_endpoint['method'] =  items["request"]["method"]
                    # get headers
                    for value in items["request"]["header"]:
                        headers[value["key"]] = value["value"]

                    api_endpoint['headers'] = headers
                    # once the data for an endpoint is parsed out, add it to dictionary
                    if "body" in endpoints["request"]:
                        if "raw" == endpoints["request"]["body"]["mode"]:
                            api_endpoint["body"] = endpoints["request"]["body"]["raw"]
                        else:
                            api_endpoint["body"] = ""
                    else:
                        api_endpoint["body"] = ""

                    endpoint_collection.append(api_endpoint)
                    if(self.verbose):
                        print "  " +  endpoints["name"]
                        print "    " +  api_endpoint["name"]
                        print "      " + api_endpoint["url"]
                        print "      " + api_endpoint["method"]
                        print "      ----------------"

        return endpoint_collection
