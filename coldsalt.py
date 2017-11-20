import sys, json, argparse, requests, re, random, csv
from cs_parser_postman import CSParserPostman    # used to parse Postman
from cs_parser_swagger import CSParserSwagger    # used to parse swagger input
from cs_parser_curl import CSParserCurl    # Used to parse curl input
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def parseURL(urlString):
    """Parses a request URL and replaces all placeholders/variables with the associated values from the environment file."""
    finalUrl = urlString
    patterns = {"postman": "{{[\w]*}}*", "swagger": "{[\w]*}*", "curl": "{[\w]*}*"}
    parameters = re.findall(patterns[args.mode], urlString)

    for param in parameters:
        cleanParam = param.replace("{","").replace("}","")
        if cleanParam not in env_var:
            print "!ERROR found parameter not in ENVIRONMENT VARIABLES: " + str(cleanParam)
            if cleanParam not in missing_parameters:
                missing_parameters.append(cleanParam)
        finalUrl = finalUrl.replace(param, env_var.get(cleanParam, ""))
    return finalUrl

def parseBody(bodyString):
    """Parses a request body and replaces all placeholders/variables with the associated values from the environment file."""

    finalBody = bodyString

    patterns = {"postman": "{{[\w]*}}*", "swagger": "{[\w]*}*", "curl": "{[\w]*}*"}
    parameters = re.findall(patterns[args.mode], bodyString)

    for param in parameters:
        #print "param: " + param
        cleanParam = param.replace("{","").replace("}","")
        #print cleanParam
        if "" != cleanParam:
            if cleanParam not in env_var:
                print "!ERROR found parameter not in ENVIRONMENT VARIABLES: %s !" % cleanParam
                if cleanParam not in missing_parameters:
                    missing_parameters.append(cleanParam)
            finalBody = finalBody.replace(param, env_var.get(cleanParam, ""))

    # make sure we end up with a json string with double quote delimiters
    finalBody = finalBody.replace("\'","\"")

    return finalBody


def sendRequest(requestUrl, requestMethod, requestHeaders, requestBody):
    """Send the request as passed in."""
    r = ""
    if requestMethod == "GET":
        r = requests.get(requestUrl, headers=requestHeaders, proxies=p, verify=False)
    elif requestMethod == "HEAD":
        r = requests.head(requestUrl, headers=requestHeaders, proxies=p, verify=False)
    elif requestMethod == "OPTIONS":
        r = requests.options(requestUrl, headers=requestHeaders, proxies=p, verify=False)
    elif requestMethod == "POST":
        r = requests.post(requestUrl, headers=requestHeaders, proxies=p, verify=False, data=requestBody)
    elif requestMethod == "PUT":
        r = requests.put(requestUrl, headers=requestHeaders, proxies=p, verify=False, data=requestBody)
    elif requestMethod == "PATCH":
        r = requests.patch(requestUrl, headers=requestHeaders, proxies=p, verify=False, data=requestBody)
    elif requestMethod == "DELETE":
        r = requests.delete(requestUrl, headers=requestHeaders, proxies=p, verify=False)
    else:
        print "Unsupported Method: " + str(requestMethod)
    return r


def fixHeaders(requestHeaders):
    """Parses request headers and replaces all placeholders/variables with the associated values from the environment file."""
    newHeaders = dict()
    for key in requestHeaders:
        if "{" in requestHeaders[key]:
            value = requestHeaders[key].replace("{","").replace("}","")

            if value in env_var:
                newHeaders[key] = env_var.get(value, "")
            else:
                if value not in missing_parameters:
                    print "!ERROR found header parameter not in ENVIRONMENT VARIABLES: " + str(value)
                    missing_parameters.append(value)
                newHeaders[key] = requestHeaders[key]
        else:
            newHeaders[key] = requestHeaders[key]
    return newHeaders



def doBurpStuff():
    """If BurpBudy is enabled, move requests to Intruder and Repeater."""
    if args.verbose:
        print "Checking if BurpBuddy is available..."
    # check if burpbuddy is active
    _url = BURP_BUDDY_URL + "/ping"
    try:
        _status = requests.get(_url, verify=False, timeout=3)
    except:
        _status.text = ""
    # if we get PONG as a response, API is active
    if  _status.text == "PONG":
        # pull proxy history
        if args.verbose:
            print "Getting proxy history from BurpBuddy..."
        _url = BURP_BUDDY_URL + "/proxyhistory"
        _history = requests.get(_url, verify=False)
        if _history.status_code == requests.codes.ok:
            _request_data = json.loads(_history.text)
            _repeater_url = BURP_BUDDY_URL + "/send/repeater"
            _intruder_url = BURP_BUDDY_URL + "/send/intruder"
            for _r in _request_data:
                # build burpbuddy request
                _post_data = {}
                _post_data["host"] = _r["http_service"]["host"]
                _post_data["port"] = _r["http_service"]["port"]
                _post_data["use_https"] = "true" if _r["http_service"]["protocol"] == "https" else "false"
                _post_data["request"] = _r["request"]["raw"]
                if args.verbose:
                    print _post_data
                requests.post(_repeater_url, data=json.dumps(_post_data), verify=False)
                requests.post(_intruder_url, data=json.dumps(_post_data), verify=False)


def writeAuditLog():
    """Write out a csv file with the endpoints parsed and called."""
    with open(args.output, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(audit_log)


def parseHeaders(headerFile, headerDict):
    print "\nStarting to parse headers file: " + str(headerFile)
    header_data = json.loads(open(headerFile).read())
    for value in header_data["values"]:
        #header_data[value["key"]] = str(value["value"])
        headerDict[str(value["key"])] = str(value["value"])
    if(args.verbose):
        print "---------------------------------------------------"
        print "parsed header file:  " + str(headerFile)
        print "current headers: "
        print str(headerDict)

    return headerDict


# Print splash screen
def printSplash():
    print "\n"
    print """  ___|       |     |  ___|        | |   """
    print """ |      _ \  |  _` |\___ \   _` | | __| """
    print """ |     (   | | (   |      | (   | | |   """
    print """\____|\___/ _|\__,_|_____/ \__,_|_|\__| """
    print " "
    print "Version: %s " % version
    print "\n\n"


parser = argparse.ArgumentParser(description="Cold Salt - automating API requests from common collection files.")
parser.add_argument("-a","--allmethods", help="Make API calls for all HTTP methods including state change related methods.", action="store_true", default="false")
parser.add_argument("--burpbuddy", help="IP:port of Burp Budy instance. Defaults to localhost:8081.", default="127.0.0.1:8081")
parser.add_argument("--checkonly", help="enable debug mode. No requests will be sent", action="store_true", default="false")
parser.add_argument("-c","--contenttype", help="Force or override Content-Type on requests")
parser.add_argument("-e", "--environment", help="The environment.json file to parse.")
parser.add_argument("--headers", help="The headers.json file to parse.")
parser.add_argument("-i", "--input", help="The JSON collection file, Postman or Swagger, to parse.")
parser.add_argument("--mode", choices=['curl', 'postman', 'swagger'], help="Which mode, or collection type, to use. Choices are 'curl', 'postman', or 'swagger'")
parser.add_argument("--output", help="write output/audit log to a csv")
parser.add_argument("--proxy", help="IP:Port of proxy to use. Defaults to localhost:8080.", default="127.0.0.1:8080")
parser.add_argument("-v", "--verbose", help="Enable verbose output.", action="store_true")
parser.add_argument("-x", "--xperimental", help="enable Xperimental Burp mode", action="store_true")
args = parser.parse_args()


# global variables
version = "beta 0.5.0"
safe_methods = ["GET", "HEAD", "OPTIONS"]
standard_methods = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE", "OPTIONS"]
env_var = dict()
headers = dict()
audit_log = []
live_token = ""
requests.packages.urllib3.disable_warnings(InsecureRequestWarning) # disable this since we're sending requests through Burp
missing_parameters = []
p = {"http": "http://" + args.proxy, "https": "https://" + args.proxy}

#


printSplash()

print args.input

if args.environment:
    print "\nStarting to parse environment file: " + str(args.environment)
    env_data = json.loads(open(args.environment).read())
    for value in env_data["values"]:
        env_var[value["key"]] = value["value"]
    if(args.verbose):
        print "---------------------------------------------------"
        print "parsed environment file:  " + str(args.environment)
        print "found these environment variables: "
        print str(env_var)



# let's build a dictionary for each request and put all of them into a list
# each endpoint dictionary is {name, url, method, headers[] }
collection_items = []
globalHeaders = dict()

_file = args.input
# parse disparate input formats into simple dict entries
if args.mode == "postman":
    requestParser = CSParserPostman(verbose = args.verbose)
    collection_items = requestParser.parsePostman(args.input)
elif args.mode == "swagger":
    requestParser = CSParserSwagger(verbose = args.verbose)
    collection_items = requestParser.parseSwagger(args.input)
elif args.mode =="curl":
    requestParser = CSParserCurl(verbose = args.verbose)
    collection_items = requestParser.parseCurl(args.input)


print "\nGetting ready to send requests"

allowed_methods = []
if args.allmethods == True:
    allowed_methods = standard_methods
else:
    allowed_methods = safe_methods

# do header stuff.....
# TODO see if this step can be done when the dict is built...
globalHeaders["User-Agent"] = "coldsalt"
# see if we've got a header file to parse...
if args.headers:
    globalHeaders = parseHeaders(headerFile=args.headers, headerDict=globalHeaders)

# force Content-Type overrides other header settings
if "None" != str(args.contenttype):
    #print "overriding content type!"
    if "content-type" in headers.keys():
        globalHeaders["content-type"] = args.contenttype
    elif "Content-Type" in headers.keys():
        globalHeaders["Content-Type"] = args.contenttype


for endpoint in collection_items:
    if endpoint["method"] in allowed_methods:
        headers = dict()
        url = parseURL(endpoint["url"])
        method = endpoint["method"]
        if "body" in endpoint:
            body = parseBody(endpoint["body"])
            print body
        else:
            body = ""

        # merge global headers
        headers = dict(fixHeaders(endpoint["headers"]).items() + globalHeaders.items())

        if(args.verbose):
            print "-------------"
            print "Request"
            print "  url: " + str(url)
            print "  method: " + str(method)
            print "  headers: " + str(headers)
            print "  body: " + str(body)
        else:
            if(args.checkonly == "false"):
                print "Sending: " + str(method) + " " + str(url)
        if(args.checkonly == "false"):
            resp = sendRequest(url, method, headers, body)

            audit_log.append([endpoint["name"], method, url, resp.status_code])
            print " - Response Status: " +  str(resp.status_code)
        else:
            audit_log.append([endpoint["name"], method, url, "Not Requested"])
    else:
        #unsafe methods
        url = parseURL(endpoint["url"])
        audit_log.append([endpoint["name"], endpoint["method"], url, "Not Requested"])

# for any parameters set in the Input file that don't have values in the Environment file, write out a stub
if len(missing_parameters) > 0:
    print "\n----------------------"

    contents = ",".join('{"key": "%s", "value": "<INSERTVALUE>"}' % param for param in missing_parameters)
    if(args.environment):
        print "Please add the following parameters to your environment file: "
        print contents
    else:
        print "Missing parameters helper file stub: "
        print '{"name": "generic config file", "values": [%s]}' % contents

if args.xperimental:
    doBurpStuff()

if(args.output):
    writeAuditLog()
