import config
import datetime
from py_backend.date_and_time.conversion import Convert
from werkzeug.security import generate_password_hash


class SlotMaker:

    @staticmethod
    def assign_slots_scheduling():
        try:
            config.logger.log("INFO", "Trying to fetch doctors details for making new slots")
            doctors_fetch_query = "select email, start_time, end_time, session, break_start, break_end from " \
                                  "medhub.doctor where active = True and time_set = True allow filtering "
            info = config.cassandra.session.execute(doctors_fetch_query).all()
            config.logger.log("INFO", "Inserting new slots")
            for i in info:
                date = datetime.date.today() + datetime.timedelta(days=15)
                appointments = Convert().sessions_in_a_day(date, i.start_time, i.end_time, i.break_start, i.break_end, i.session)
                for appointment in appointments:
                    record = {
                        "appt_id": generate_password_hash(i.email + datetime.datetime.now().isoformat())[21:],
                        "doctor_email": i.email,
                        "patient_email": "NA",
                        "diagnosis": "NA",
                        "prescription": "NA",
                        "session": i.session,
                        "start": appointment,
                        "status": "NA",
                        "issue": "NA"
                    }
                    config.cassandra.insert_one("medhub.appointment", record)
        except Exception as e:
            config.logger.log("ERROR", str(e))

    @staticmethod
    def make_slots_first_time(email, start_time, end_time, break_start, break_end, session):
        try:
            for i in range(0, 15):
                date = datetime.date.today() + datetime.timedelta(days=i)
                appointments = Convert().sessions_in_a_day(date, start_time, end_time, break_start, break_end, session)
                for appointment in appointments:
                    record = {
                        "appt_id": generate_password_hash(email + datetime.datetime.now().isoformat())[21:],
                        "doctor_email": email,
                        "patient_email": "NA",
                        "diagnosis": "NA",
                        "prescription": "NA",
                        "session": session,
                        "start": appointment,
                        "status": "NA",
                        "issue": "NA"
                    }
                    config.cassandra.insert_one("medhub.appointment", record)
        except Exception as e:
            config.logger.log("ERROR", str(e))
