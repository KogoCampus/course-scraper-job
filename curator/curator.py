import json
import os
import boto3

# school format = "simon_fraser_university"
def updateCleansed(id, school):
    f = open(os.getcwd() + '/curator/curator.json')
    data = json.load(f)

    if data.get(school):
        data[school]["previous_scraped_data_id_cleansed"] = data[school]["latest_scraped_data_id_cleansed"]
        data[school]["latest_scraped_data_id_cleansed"] = id
    else:
        data[school] = {
            "latest_scraped_data_id_cleansed": id,
            "previous_scraped_data_id_cleansed": "",
        }
    writeJson(data)
    f.close()

def updateUncleansed(id, school):
    f = open(os.getcwd() + '/curator/curator.json')
    data = json.load(f)

    if data.get(school):
        data[school]["previous_scraped_data_id_uncleansed"] = data[school]["latest_scraped_data_id_uncleansed"]
        data[school]["latest_scraped_data_id_uncleansed"] = id
    else:
        data[school] = {
            "latest_scraped_data_id_uncleansed": id,
            "previous_scraped_data_id_uncleansed": "",
        }
    writeJson(data)
    f.close()



def writeJson(data):
    with open(os.getcwd() + '/curator/curator.json', 'w') as f:
        json.dump(data, f)