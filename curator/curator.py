import json
import os
import boto3

# school format = "simon_fraser_university"
async def updateCleansed(id, school):
    path = os.getcwd() + '/curator/curator.json'
    f = open(path)
    if os.stat(path).st_size == 0:
        print("no uncleansed data")
        return
    else:
        data = json.load(f)
        if data.get(school):
            print('school existed')
            data[school]["previous_scraped_data_id_cleansed"] = data[school]["latest_scraped_data_id_uncleansed"]
            data[school]["latest_scraped_data_id_cleansed"] = id
        else:
            print("school doesn't exist - newly created")
            data[school] = {
                "latest_scraped_data_id_cleansed": id,
                "previous_scraped_data_id_cleansed": "",
            }
        writeJson(data)
        f.close()

async def updateUncleansed(id, school):
    path = os.getcwd() + '/curator/curator.json'
    f = open(path)
    if os.stat(path).st_size == 0:
        obj = {
            school: {
                "latest_scraped_data_id_uncleansed": id,
                "previous_scraped_data_id_uncleansed": "",
                "latest_scraped_data_id_cleansed": "",
                "previous_scraped_data_id_cleansed": "",
            }
        }
        writeJson(obj)
        f.close()
        return
    else:
        data = json.load(f)
        if data.get(school):
            print('school existed')
            data[school]["previous_scraped_data_id_uncleansed"] = data[school]["latest_scraped_data_id_uncleansed"]
            data[school]["latest_scraped_data_id_uncleansed"] = id
        else:
            print("school doesn't exist - newly created")
            data[school] = {
                "latest_scraped_data_id_uncleansed": id,
                "previous_scraped_data_id_uncleansed": "",
            }
        writeJson(data)
        f.close()



def writeJson(data):
    with open(os.getcwd() + '/curator/curator.json', 'w') as f:
        json.dump(data, f)
    f.close()