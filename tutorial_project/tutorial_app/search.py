import json
import urllib, urllib2
import os 

BING_API_KEY = os.environ.get('BING_API_KEY')

def run_query(search_terms):
	root_url = 'https://api.datamarket.azure.com/Bing/Search/'
	source = 'Web'
	results_per_page = 10
	# Offset specifies where in the results list to start from.
	offset = 0

	# Wrap quotes around our query terms as required by the Bing API.
    # The query we will then use is stored within variable query.
	query = "'{0}'".format(search_terms)
	query = urllib.quote(query)

	#construct search url , format json response

	search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
					root_url,
					source,
					results_per_page,
					offset,
					query )


# Setup authentication with the Bing servers.
    # The username MUST be a blank string, and put in your API key!
	username = ''

	#create pw mgr to handle authentication
	password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

	password_mgr.add_password(None, search_url, username, BING_API_KEY)

	results = [] #init results list

	try:
		#prep for connection to bing servers
		handler = urllib2.HTTPBasicAuthHandler(password_mgr)
		opener =  urllib2.build_opener(handler)
		urllib2.install_opener(opener)

		# Connect to the server and read the response generated.

		response = urllib2.urlopen(search_url).read()

		json_response = json.loads(response)

		for result in json_response['d']['results']:
			results.append({
				'title' : result['Title'],
				'link' : result['Url'],
				'summary' : result['Description']
								})
			
	except urllib2.URLError as e:
		print search_url
		print "Error when querying the Bing API: ", e

	return results
