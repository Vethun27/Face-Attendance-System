
from datetime import datetime, timedelta
import face_recognition


class attendancyInfo:
    def __init__(self,database):

        if database == None:
            print("No connection to Database")
            return None
        
        #private variables
        self._collection_users = database["users"]
        self._collection_attendancy = database["attendancy"]
    


    def getFilteredDatesAndTime(self, userId, attendancy_table, startDate_filter, endDate_filter):
        
        corrected_start_date = datetime.strptime(startDate_filter.get(), "%d.%m.%y") - timedelta(days=1)
        start_date = corrected_start_date.strftime("%d.%m.%y")
        end_date = endDate_filter.get()

        if start_date < end_date:
        
            query = {"_userId":userId, "date":{"$gte": start_date, "$lte": end_date}}
            results = self._collection_attendancy.find(query)

            if self._collection_attendancy.count_documents(query) != 0:
                for result in results:
                    dataset = (result["date"], self.find_userName_by_id(userId), " ", result["time"], result["status"]) #TODO: add department field
                    dataset_id = attendancy_table.insert("", "end", values=dataset)
                    if result["status"] == "Start":
                        attendancy_table.tag_configure(f"{dataset_id}", background="green")
                        attendancy_table.item(dataset_id, tags=(f"{dataset_id}",))
                    else:
                        attendancy_table.tag_configure(f"{dataset_id}", background="red")
                        attendancy_table.item(dataset_id, tags=(f"{dataset_id}",))

            else:
                 CTkMessagebox(title="Error", message="No Data found", icon="cancel")
        else:
             CTkMessagebox(title="Error", message="Invalid Dates", icon="cancel")
