from datetime import datetime
#import pymongo
class Log:
    def __init__(self):
        pass

    def write_log(self, sessionID, log_message):
        #dbConn = pymongo.MongoClient("mongodb://localhost:27017/")  # opening a connection to Mongo
        #db = dbConn['botDB']  # connecting to the database called crawlerDB
        #mydict = {"sessionid": sessionID, "message": log_message} # saving that detail to a dictionary
        #table= db[sessionID]
        #x = table.insert_one(mydict)
        #dbConn.close()

        self.file_object = open("conversationLogs/"+sessionID+".txt", 'a+')
        self.now = datetime.now()
        self.date = self.now.date()
        self.current_time = self.now.strftime("%H:%M:%S")
        self.file_object.write(
          str(self.date) + "/" + str(self.current_time) + "\t\t" + log_message + "\n")
        self.file_object.close()
