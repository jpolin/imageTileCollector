# imageTileCollector
Simple script to download the first n images for a Bing image search with a specified size. Intended to be used for generating photo mosaics, but could also be used to simply download 10,000 puppy pictures.

##Usage##

Currently, all parameters are set at the top of the python file. Be sure that the destination folder exists. It will overwrite exsiting pictures in the output folder in each run, so be careful! 

If you will be using this extensively, please secure your own Microsoft AppID (free); the current one is collectively limited to 1000 search queries per month (which may be exhausted at this point). You can paste your own key in the respective field at the top of the source file.
