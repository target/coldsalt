####
## CS_Parser_Curl
## Simple helper type class for parsing curl input into ColdSalt internal format
## Author: jason nordenstam
####

import json

class CSParserCurl:

    def __init__(self, verbose = False):
        self.verbose = verbose


    def parseCurl(self, inputfile):
        endpoint_collection = []
        lines = []
        print "\nParsing curl file %s" % str(inputfile)
        with open(inputfile) as f:
            lines = f.readlines()

        if self.verbose:
            print "Found %s lines..." % len(lines)

        for line in lines:
            if line.find("\'") > 0:
                line = line.replace("\'", "\"")

            api_endpoint = {}
            # method
            method_index = line.find("-X")
            # if a method is not specified, treat it as a GET
            if method_index == -1:
                method = "GET"
            else:
                method = line[method_index : method_index + 16].split()[1]
            api_endpoint['method'] =  method

            # headers
            headers = {}
            headers_index = line.find("-H")
            # each header starts with -H so look through them
            for x in xrange(line.count("-H")):
                # split out the current header
                header = line.split("-H")[x+1].split("\"")[1]
                # jam it into the dictionary
                headers[header.split(":")[0]] = header.split(":")[1].strip()
            # add the dictionary to the endpoint object
            api_endpoint['headers'] = headers
            # url stuff
            if line.find("\"http") == -1:
                # maybe it's not quoted?
                url = line[line.find("http"):].strip()
            else:
                url = line[line.find("\"http"):].split("\"")[1].strip()

            api_endpoint['url'] = url
            # name - curl doesn't really have a place for names, so grab the stuff
            # after /v# and use that
            base_name = url[url.find("/v"):url.find("?")].strip()
            name = method + " " + base_name

            api_endpoint['name'] = name

            # TODO this really only supports json data with -d
            # TODO make this handle --data and non-jsaon data
            # data - could be -d or --data
            brk_str = ""
            if "--data" in line:
                 brk_str = "data"
            elif "-d" in line:
                brk_str = "d"

            # if no data, do nothing
            if brk_str != "":
                tmp = line.split("-")
                for x in tmp:
                    if x.startswith(brk_str):
                        # slice out the data, add the length of the brk_str since find will
                        # return the start index of our string
                        tmp_data = x[x.find(brk_str)+len(brk_str):].strip()
                        # need to clean up opening and closing quotes
                        # determine if JSON or form encoded
                        #print tmp_data
                        if tmp_data[1:len(tmp_data)-1].startswith("{"):
                            try:
                                jsn_data = json.loads(tmp_data[1:len(tmp_data)-1])
                            except ValueError as e:
                                print "[!] Error occured parsing json. Please verify format is correct."
                                jsn_data = ""

                            api_endpoint["body"] = jsn_data
                        else:
                            api_endpoint["body"] = tmp_data[1:len(tmp_data)-1]
            else:
                api_endpoint["body"] = ""

            endpoint_collection.append(api_endpoint)

            if(self.verbose):
                print "    " +  api_endpoint["name"]
                print "      " + api_endpoint["url"]
                print "      " + api_endpoint["method"]
                print "      " + str(api_endpoint["body"])
                print "      ----------------"

        return endpoint_collection
