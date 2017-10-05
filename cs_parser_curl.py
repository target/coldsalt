####
## CS_Parser_Curl
## Simple helper type class for parsing curl input into ColdSalt internal format
## Author: jason nordenstam
####

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
            print "Found %s lines..." % len(_lines)

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
        
            endpoint_collection.append(api_endpoint)

            if(self.verbose):
                print "    " +  api_endpoint["name"]
                print "      " + api_endpoint["url"]
                print "      " + api_endpoint["method"]
                print "      ----------------"

        return endpoint_collection
