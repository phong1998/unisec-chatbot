from rasa_core_sdk import Action
from rasa_core_sdk.forms import FormAction
from rasa_core_sdk.events import SlotSet, AllSlotsReset
import pymongo
import re
client = pymongo.MongoClient("localhost", 27017)
db=client["unisec-db"]

class ActionHoiDanhSachNganh(Action):
   def name(self):
      return "action_hoi_danh_sach_nganh"

   def run(self, dispatcher, tracker, domain):
      university = tracker.get_slot("ten_truong")

      if len(university) == 0:
         dispatcher.utter_message("Bạn muốn hỏi điểm chuẩn của trường nào ?")
         return

      res = db.admission_scores.find({'university': re.compile('^' + university + '$', re.IGNORECASE), 'year': 2019})

      mes = ""
      for entry in res:
         mes = mes + entry["major_name"] + entry["score"] + "\n"
      if len(mes) == 0:
         res = db.admission_scores.find({'university': re.compile('^' + university + '$', re.IGNORECASE), 'year': 2018})
         for entry in res:
            mes = mes + entry["major_name"] + entry["score"] + "\n"
               
      if len(mes) == 0:
         dispatcher.utter_message("Hiện chưa có thông tin điểm chuẩn " + university)
      else:
         dispatcher.utter_message("điểm chuẩn: "  + mes)
      #dispatcher.utter_message("hello")
      #return [SlotSet("diem_chuan",["vukihai"])]


class FormHoiDiemChuan(FormAction):
   def name(self):
      return "form_hoi_diem_chuan"

   @staticmethod
   def required_slots(tracker):
      return ["ten_truong"]

   def submit(self, dispatcher, tracker, domain):
      university = tracker.get_slot("ten_truong")
      major = tracker.get_slot("ten_nganh")
      year = tracker.get_slot("nam")

      query = {'university': re.compile('^' + university + '$', re.IGNORECASE), 'year': int(year)}
      if not major is None:
         query['major_name'] = re.compile('^' + major + '$', re.IGNORECASE)
      res = db.admission_scores.find(query)

      mes = ""
      for entry in res:
         mes = mes + entry["major_name"] + ":" + entry["score"] + " khối " + entry['combine'] +"\n"
               
      if len(mes) == 0:
         dispatcher.utter_message("Hiện chưa có thông tin điểm chuẩn " + university + " năm " + str(year))
      else:
         if not major is None:
            dispatcher.utter_message("điểm chuẩn ngành "+ major + " năm "  + str(year) + ": " )
            dispatcher.utter_message(mes)
            return []
         dispatcher.utter_message("Sau đây là điểm chuẩn đại học "+ university + " năm "  + str(year))
         dispatcher.utter_message(mes)
      return []
      #dispatcher.utter_message("hello")
      #return [SlotSet("diem_chuan",["vukihai"])]

class FormHoiDanhSachNganh(FormAction):
   def name(self):
      return "form_hoi_danh_sach_nganh"

   @staticmethod
   def required_slots(tracker):
      return ["ten_truong"]

   def submit(self, dispatcher, tracker, domain):
      university = tracker.get_slot("ten_truong")
      
      
      query = {'name': re.compile('^' + university + '$', re.IGNORECASE)}
      
      res = db.universities.find(query)
      numOfMajor = 0
      mes = ""
      try:
         numOfMajor = len(res[0]['majors'])
         for entry in res[0]['majors']:
            mes = mes + entry['major_name'] + "\n"
      except:
         print("error")
      if len(mes) == 0:
         dispatcher.utter_message("Hiện chưa có thông tin các ngành đào tạo của " + university)
      else:
         dispatcher.utter_message("Trường "+ university + " hiện đào tạo "  + str(numOfMajor) + " ngành")
         dispatcher.utter_message(mes)
      return []
      #dispatcher.utter_message("hello")
      #return [SlotSet("diem_chuan",["vukihai"])]
    