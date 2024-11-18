import json
import os

# school format = "simon_fraser_university"
async def update(id, school):
    path = os.getcwd() + '/scrapers/curator/curator.json'
    f = open(path)
    if os.stat(path).st_size == 0:
        obj = {
            school: {
                "latest_scraped_data_id": id,
                "previous_scraped_data_id": "",
            }
        }
        writeJson(obj)
        f.close()
        return
    else:
        data = json.load(f)
        if data.get(school):
            print('school existed')
            data[school]["previous_scraped_data_id"] = data[school]["latest_scraped_data_id"]
            data[school]["latest_scraped_data_id"] = id
        else:
            print("school doesn't exist - newly created")
            data[school] = {
                "latest_scraped_data_id": id,
                "previous_scraped_data_id": "",
            }
        writeJson(data)
        f.close()



def writeJson(data):
    with open(os.getcwd() + '/scrapers/curator/curator.json', 'w') as f:
        json.dump(data, f)
    f.close()