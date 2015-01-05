#!/usr/bin/env python

import urllib2
import json
import splunk.Intersplunk as si
import splunk.entity as entity
import splunk.mining.dcutils as dcu

logger = dcu.getLogger()

class Faroo(object):
    """ Does a Faroo search and results a result set into Splunk

    ##Syntax
        faroo fieldname=<field>

    ##Description
    Searches Faroo search engine for a field passed to the command. This is a streaming command hence it can do millions of searches at a time. Compare to Google where you are limited to a set of API calls per day or other paid Search Engine API like Bing. 

    ##Example
        
    """
    def __init__(self, APIKey):
        """
        Faroo Contructor 
            Provides the necessary pieces to make a rest query via the Faroo API
            @param APIKey: api key to use in a query
        """
        self._apikey = APIKey

    def query(self, keyword):
        """
        Public Method: query
            Used to make an API query out to Faroo, returns a json response
        @param keyword: keyword to search for
        """
        try:
            encoded_keyword = urllib2.quote(keyword.encode("utf8"))
            self._apicall = 'http://www.faroo.com/api?q=' + encoded_keyword + '&start=1&length=10&l=en&src=web&f=json&key=' + self._apikey
            response = urllib2.urlopen(self._apicall).read()
            results = json.loads(response)
            return results
        except Exception as e:
            results = si.generateErrorResults(str(e))
            logger.exception(e)
            si.outputResults(results)

#need a function outside the faroo constructor to get the API key from Splunk
def getKey(sessionKey):
    # list api_key
    ent = entity.getEntities('faroo/conf/setupentity',namespace='SA-faroo', owner='nobody',sessionKey=sessionKey)

    # return first set of cred
    for value in ent.values():
        return value['api_key']
def parseResults(content,query):
    output = dict()

    try:
        for key,value in content.iteritems():
            output.update({'query':query,'match':'yes','title':content['title'],'description':content['kwic'],'url':content['url'],'domain':content['domain']})
        return output
    except Exception as e:
        results = si.generateErrorResults(str(e))
        logger.exception(e)

if __name__ == '__main__':
    
    results, dummyresults, settings = si.getOrganizedResults()
    keywords, options = si.getKeywordsAndOptions()
    try: 
        # get session key from settings
        s_key = settings['sessionKey']

        # retrive APIKey for Faroo from the setup entity
        APIKey = getKey(s_key)
    
        # faroo object
        faroo = Faroo(APIKey)
        
        answers = []
        for field_to_match in options.values():
            for entry in results:
                if entry[field_to_match]:
                    results = faroo.query(entry[field_to_match])
                    #logger.wdarn(json.dumps(results,sort_keys=True, indent=4))
                    if results['results']:
                        for item in results['results']:
                            answers.append(parseResults(item,entry[field_to_match]))
                    else:
                        answers.append({'query':entry[field_to_match],
                                        'match':'no',
                                        'title':'',
                                        'description':'',
                                        'url':'',
                                        'domain':''})


        si.outputResults(answers)
    except Exception as e:
        results = si.generateErrorResults(str(e))
        logger.exception(e)
        si.outputResults(results)




