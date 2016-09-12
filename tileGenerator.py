# Photo mosaic tile generator
#
# Author: Joe Polin
# Date: September, 2016
# Description: Download pictures from google and convert to desired format.

# User parameters:
nphotos = 1000
search_query = "boobs"
photo_size = (80, 80) # (w, h) in pixels
write_dir = "photos/"

# Developer parameters:
max_results_per_request = 150 # max is 150
max_requests_per_run = 100 # 1000/month!
developer_key = '17b0eb9d0c21479c99343569bc465e55'
request_domain = 'api.cognitive.microsoft.com'
request_path = "/bing/v5.0/images/search?%s"

# Globals
requests_made = 0

# Web parsing/querying
import httplib, urllib, base64, json
from urlparse import urlparse, parse_qs

# Threading
from multiprocessing import Pool

# Standard
import queue, os, time, signal

# Iterator that can be used to get image results
class imageSearchURLs:
    def __init__(self, search_query, nresults):
        self.headers = {
            'Content-Type': 'multipart/form-data', 
            'Ocp-Apim-Subscription-Key': developer_key,
            'safeSearch': 'strict',
        }
        self.urls = queue.Queue()
        self.query = search_query
        self.nresults = nresults
        self.results_returned = 0
        self.results_offset = 0 # Used by request url

    def __iter__(self):
        return self

    def loadMoreResults(self):
        global requests_made
        # Keep requests from getting out of control--we're on a budget!
        if requests_made >= max_requests_per_run:
            print "Can not make any more requests in this run--max reached"
            raise StopIteration
        else:
            print "Making request for image search results (count = %d, offset = %d)" \
                % (max_results_per_request, self.results_offset)
        # Make request
        params = urllib.urlencode({
            "q":self.query, 
            "count":max_results_per_request, 
            "offset":self.results_offset})
        conn = httplib.HTTPSConnection(request_domain)
        conn.request("POST", request_path % params, "{body}", self.headers)
        requests_made += 1
        response = conn.getresponse()     
        raw_response = response.read()   
        conn.close()
        # Parse response
        data = json.loads(raw_response)
        results = data['value']
        for r in results:
            img_url = r['thumbnailUrl']
            self.urls.put(img_url)
        # Update params for next run
        self.results_offset += max_results_per_request


    def next(self):
        # Done
        if self.results_returned == self.nresults:
            raise StopIteration
        # Need to populate queue
        if self.urls.empty():
            self.loadMoreResults()
        # Return next result
        self.results_returned += 1
        return self.urls.get()

# Download a photo at a url
def download_image(remote_url, local_path): # TODO, overwrite = True):
    getter = urllib.URLopener()
    # Require size
    remote_url += "&w=%d&h=%d&c=7"%photo_size
    getter.retrieve(remote_url, local_path)


def run():
    # Create thread pool
    pool = Pool(processes = 8, maxtasksperchild = 1)

    # Signal handler closes down pool
    def signal_handler(signal, frame):
        print "ctrl+c caught; collecting processes"
        pool.close()
        pool.join()
        print "Processes joined"

    # Catch ctrl+c
    signal.signal(signal.SIGINT, signal_handler)

    print "Searching for %s" % search_query
    counter = 0
    for url in imageSearchURLs(search_query, nphotos):        
        print "%d. "%(counter+1), url
        counter += 1
        # Assign to pool
        args = [url, os.path.join(write_dir, str(counter)+".jpg")]
        pool.apply_async(download_image, args)        


if __name__=="__main__":
    start_time = time.time()
    run()
    print "Run time: %f seconds" % (time.time()-start_time)

    # Run time results
    # Non-threaded: 11.42 seconds for 50 requests
    # 4 threads: 1.35 seconds


