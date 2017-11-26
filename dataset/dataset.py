#!/usr/bin/python

import requests
import urllib3
import os
import pandas as pd
import math
import pprint
import json
import time
import sys
from multiprocessing import Pool
from PIL import Image

# To-do: remove obviously flawed images(duplicated ones; damaged ones)

def bing_search(query, count=8, offset=0):
    """Invokes Bing Image Search API to obtain images.
    Official documentation by Azure:
    https://docs.microsoft.com/en-us/azure/cognitive-services/bing-image-search/search-the-web

    The set of images from Bing can be classified into two types here: Original ones and Derivative ones.
    Original ones are the direct searching results for the term, and the total results usually contain 700-1000 images,
    but a large amount of them can be irrelevant.
    Derivative ones are those visually similar to the original ones. For every original image, there usually comes
    90-100 similar images.

    This function gets the original images set.

    Args:
        query: Query term for target data set.
        count: Number of the original images. count * 100 is approximately the size of the whole date set.
        offset: Position parameter which specifies the number of results to skip. Notice this parameter should
        be dealt with carefully if the whole searching results are needed.

        (The maximum number of results returned once is 150 now, and whole results number is usually 700-1000.
        Microsoft may change that limit later, but before that, this function should be invoked 3-5 times with carefully
        calculated offset parameter in order to grab all the results.)

    Returns:
        Information for original images in Json format.

    Raises:
        None.
    """
    url = 'https://api.cognitive.microsoft.com/bing/v5.0/images/search'
    # Query string parameters.
    payload = {
        'q': query,
        'count': count,
        'offset': offset,
        'modulesRequested': 'all'
    }
    # Custom headers.
    headers = {
        'Content-Type': 'multipart/form-data',
        'Ocp-Apim-Subscription-Key': 'cd2f8800f47840fda58b777410b41a7e'
    }
    try:
        response = requests.post(url, params=payload, headers=headers)
    except:
        print "damn!"
    return response.json()

def dataFrame(result):
    """Builds up a data frame structure for all the return results(image sets).

    Args:
        result: Raw response, returned from Bing, for a certain key word.

    Returns:
        A data frame structure, which organizes certain information extracted from the raw response.

    Raises:
        None.
    """
    link_list = [item['contentUrl'] for item in result]
    df = pd.DataFrame(link_list, columns = ["contentUrl"])
    df["name"] = [item['name'] for item in result]
    df["encodingFormat"] = [item['encodingFormat'] for item in result]
    df["insights"] = [item['imageInsightsToken'] for item in result]
    df["imageId"] = [item['imageId'] for item in result]
    return df

def bing_search_adv(imageId, insightsToken):
    """Obtains the insight of one image. Insight information usually consists of captions, descriptions,
    visually similar images.
    Official documentation by Azure:
    https://docs.microsoft.com/en-us/azure/cognitive-services/bing-image-search/search-the-web

    The set of images from Bing can be classified into two types here: Original ones and Derivative ones.
    Original ones are the direct searching results for the term, and the total results usually contain 700-1000 images,
    but a large amount of them can be irrelevant.
    Derivative ones are those visually similar to the original ones. For every original image, there usually comes
    90-100 similar images.

    This function uses information of the original ones to get the derivative ones.

    Args:
        imageId: Unique id for every returned result(image) from Bing.
        insightsToken: Token for the insight information of the image.

    Returns:
        Insight information of the derivative images in Json format.

    Raises:
        None.
    """
    url = 'https://api.cognitive.microsoft.com/bing/v5.0/images/search'
    # Query string parameters.
    payload = {
        'id': imageId,
        'insightsToken': insightsToken,
        'modulesRequested': 'all'
    }
    headers = {
        'Content-Type': 'multipart/form-data',
        'Ocp-Apim-Subscription-Key': 'cd2f8800f47840fda58b777410b41a7e'
    }
    # Make GET requests.
    response = requests.post(url, params=payload, headers=headers)
    # Get JSON response.
    return response.json()

def download(dFrame, dir_path, imageNo):
    """Downloads one original image and its visually similar images.

    Args:
        dFrame: Pandas data structure DataFrame.Two-dimensional size-mutable, potentially heterogeneous tabular
        data structure with labeled axes (rows and columns).

        query: Query term for target data set.

    Returns:
        None.

    Raises:
        Errors occurred when downloading.
    """
    if 1 == 1:
        try:
            pic_url = str(dFrame.iloc[imageNo, 0]).encode('utf-8')
            pic_name = str(dFrame.iloc[imageNo, 1]).encode('utf-8')
            pic_encoding = str(dFrame.iloc[imageNo, 2]).encode('utf-8')
            pic_insightsToken = str(dFrame.iloc[imageNo, 3]).encode('utf-8')
            pic_id = str(dFrame.iloc[imageNo, 4]).encode('utf-8')
            # Download one original image.
            pic = requests.get(pic_url, verify=False, timeout=10)
        except Exception as e:
            pass
        else:
            if pic.status_code == 200:
                # Make the directory.
                if imageNo < 10:
                    img_dir = dir_path + '/img' + '0' + str(imageNo)
                else:
                    img_dir = dir_path + '/img' + str(imageNo)
                simi_dir = img_dir + '/similar_images'

                if os.path.exists(img_dir):
                    pass
                else:
                    os.mkdir(img_dir)

                # Save this original image.
                orig_file = img_dir + '/' + 'image' + str(imageNo) + '.' + pic_encoding
                with open(orig_file, 'wb') as picF:
                    picF.write(pic.content)
                print "Saving %s" % orig_file

                # Get the insight of this original image.
                result_insight = bing_search_adv(pic_id, pic_insightsToken)

                # Download the derivative images of this original image.
                simi_num = 0
                if 'visuallySimilarImages' in result_insight.keys():
                    if os.path.exists(simi_dir):
                        pass
                    else:
                        os.mkdir(simi_dir)
                    for simi_pic_item in result_insight['visuallySimilarImages']:
                        simi_pic_id = simi_pic_item['imageId'].encode('utf-8')
                        simi_pic_link = simi_pic_item['contentUrl'].encode('utf-8')
                        simi_pic_format = simi_pic_item['encodingFormat'].encode('utf-8')
                        simi_pic_insightsToken = simi_pic_item['imageInsightsToken'].encode('utf-8')
                        try:
                            simi_pic = requests.get(simi_pic_link, verify=False, timeout=5)
                        except Exception as e:
                            pass
                        else:
                            pass

                        # Save the derivative images.
                        if simi_pic.status_code == 200:
                            simi_file = simi_dir + '/' + 'simi_img' + str(simi_num) + '.' + simi_pic_format
                            with open(simi_file, 'wb') as simi_picF:
                                simi_picF.write(simi_pic.content)
                            simi_num += 1
                            print "Saving %s" % simi_file

def download_images(dFrame, query, flag):
    """Downloads all the images.

    The specific module used for downloading is the Requests module.(http://docs.python-requests.org/en/master/)
    Multiprocessing method is employed to boost efficiency.

    Args:
        dFrame: Pandas data structure DataFrame.Two-dimensional size-mutable, potentially heterogeneous tabular
        data structure with labeled axes (rows and columns).

        query: Query term for target data set.

    Returns:
        Directory path for this image set.

    Raises:
        Errors occurred when downloading.
    """
    
    querystr = ''
    
    # Timestamp is utilized to make every data set unique.
    unique_id = str(int(time.time()))
    # Set the desired directory for the data set at here.
    querystr = querystr.join(query.split(' '))
    ## dir_path = str(os.getcwd()) + '/dataset/' + querystr + '-' + unique_id
    if flag == False:
        # subset
        dir_path = str(os.path.split(os.path.realpath(__file__))[0]) + '/sub_datasets/' + querystr + '-' + unique_id
    else:
        dir_path = str(os.path.split(os.path.realpath(__file__))[0]) + '/' + querystr + '-' + unique_id
    # print dir_path
    
    if os.path.exists(dir_path):
        pass
    else:
        os.mkdir(dir_path)
    # !
    urllib3.disable_warnings()
    p = Pool()
    for imageNo in range(dFrame.shape[0]):
        # download(dFrame, dir_path, imageNo)
        p.apply_async(download, args=(dFrame, dir_path, imageNo,))
    p.close()
    p.join()
    return dir_path

def generate_file_list(root_dir, label=1):
    """Generate the list and file for all the images.

    Args:
        root_dir: the path of the root directory for the disease.
        label: (Reserved)

    Returns:
        None.

    Raises:
        None.
    """
    standardFormat = ['jpg', 'jpeg', 'png']
    # name = root_dir.split('/')[1]
    name = root_dir + ".txt"
    print "writing file: " + name
    item_list = []
    
    # funny error0: f = open(..) 
    for img_dir_no in os.listdir(root_dir):
        img_dir = os.path.join(root_dir, img_dir_no)
        img_dir_similar = os.path.join(img_dir, "similar_images")
        
        # for mac
        if '.DS_Store' in img_dir:
            continue

        for item in os.listdir(img_dir):
            try:
                if item == "similar_images":
                    item_dir = img_dir + "/" + item
                    num = 0
                    for simi_imgs in os.listdir(item_dir):
                        item_path = item_dir + "/" + simi_imgs
                        if any(ext in item_path for ext in standardFormat):
                            try:
                                tempF = Image.open(item_path)
                                tempF.load()
                            except Exception as e:
                                print(item_path)
                                os.remove(item_path)
                            else:
                                statinfo = os.stat(item_path)
                                if statinfo.st_size >= 7300:
                                    item_list.append(item_path)
                                    # # funny error0: f.write(...)
                else:
                    pass
            except:
                pass
    # funny error0: f.close() 
    with open(name, "w") as F:
        for item in item_list:
            F.write(item + '\n')
    return
    
def dataset(query, count=10, flag = True):
    """Wraps up the whole procedure to obtain data.

    Args:
        query: Query term for target data set.
        count: Number of original images set. count * 100 is approximately the size of the whole date set.
        flag: True -> datasets for diseases; False -> datasets for symptoms;

    Returns:
        None. The dataset will be saved to the same directory with which this script runs.

    Raises:
        Errors occurred when downloading.
    """

    result = bing_search(query, count)
    dFrame = dataFrame(result.get('value', {}))
    dir_path = download_images(dFrame, query, flag)
    generate_file_list(dir_path)

def checkCurrentData(query):
    """
    """
    extension = ".txt"
    dataset_dir = os.getcwd() + "/dataset"
    dir_list = os.listdir(dataset_dir)
    dir_for_query = ''

    for item in dir_list:
        item = item.lower()
        if (query.lower() in item) and (extension in item):
             dir_for_query = item.split('.')[0]
             # print dir_for_query
    
    if len(dir_for_query) != 0:
        generate_file_list(dataset_dir + '/' + dir_for_query, label=1)        
        return True

if __name__ == "__main__":
    sub_flag = ""
    if len(sys.argv) < 2: 
        print "Usage: python %s 'QUERY TERM' (optional) 'SUB' " % (sys.argv[0])
        sys.exit()

    query = sys.argv[1]
    if len(sys.argv) == 3:
        sub_flag = sys.argv[2]
        # print "SUB"
    else:
        # dataset for diseases
        if checkCurrentData(query):
            print "Dataset <%s> exists and seems good." % (query) 
            sys.exit()

    print "Start downloading data set for <%s>." % (query)
    t_start = time.time()
    # Set the second parameter to change the number of results.
    # For current version of the script, (count >= 150) can cause problems.
    if sub_flag != "":
        print "SUB"
        dataset(query, count = 20, flag = False)
    else:
        print "MAIN"
        dataset(query, count = 20, flag = True)
    t_end = time.time()
    print "Dataset %s downloaded in %0.2f seconds." % (query, (t_end - t_start))
