import pandas as pd
import datetime
import requests
import logging
from pymongo import MongoClient
import openai_secret_manager
import psutil
import os
from cryptography.fernet import Fernet


class MongoDBClient:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)

    def insert_one(self, collection_name, data):
        db = self.client[collection_name]
        db.insert_one(data)

    def find_one(self, collection_name, query):
        db = self.client[collection_name]
        return db.find_one(query)


class SocialMediaAI:
    def __init__(self, mongo_db_client, google_analytics_api_key, openai_api_key):
        self.mongo_db_client = mongo_db_client
        self.google_analytics_api_key = google_analytics_api_key
        self.openai_api_key = openai_api_key
        self.social_media_collection_name = "social_media_data"

    def retrieve_social_media_data(self):
        end_date = datetime.datetime.now().date().strftime('%Y-%m-%d')
        start_date = (datetime.datetime.now().date() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        social_media_collection = self.mongo_db_client.find_one(self.social_media_collection_name, {"start_date": start_date, "end_date": end_date})

        if social_media_collection:
            data = social_media_collection["data"]
        else:
            url = "https://www.googleapis.com/analytics/v3/data/ga?ids=ga%3A123456789&start-date={}&end-date={}&metrics=ga%3Asessions&dimensions=ga%3AsocialNetwork&access_token={}".format(start_date, end_date, self.google_analytics_api_key)
            response = requests.get(url)
            data = pd.json_normalize(response.json()["rows"])
            self.mongo_db_client.insert_one(self.social_media_collection_name, {"start_date": start_date, "end_date": end_date, "data": data.to_dict()})

        return data

    def analyze_trends_and_patterns(self):
        data = self.retrieve_social_media_data()
        prompt = "Based on the social media data from the past 30 days, what are some trends and patterns?"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.openai_api_key}',
        }
        data = {
            'prompt': prompt,
            'temperature': 0.5,
            'max_tokens': 50,
            'n': 1,
            'stop': '.'
        }
        response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=data)

        ideas = response.json()["choices"][0]["text"].strip().split("\n")
        return ideas

    def repurpose_existing_content(self):
        data = self.retrieve_social_media_data()
        prompt = "Based on the social media data from the past 30 days, what are some ways to repurpose existing content?"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.openai_api_key}',
        }
        data = {
            'prompt': prompt,
            'temperature': 0.5,
            'max_tokens': 50,
            'n': 1,
            'stop': '.'
        }
        response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=data)

        reused_content = response.json()["choices"][0]["text"].strip().split("\n")
        return reused_content

    def main_function(self, prompt):
        data = self.retrieve_social_media_data()
        ideas = self.analyze_trends_and_patterns()
        reused_content = self.repurpose_existing_content()

        print("Here are some ideas based on the social media data:")
        for idea in ideas:
            print("- " + idea)

        print("\nHere is some reused content:")
        for content in reused_content:
            print("- " + content)

    def test_ai_assistant(self):
        data = self.retrieve_social_media_data()
        assert isinstance(data, pd.DataFrame)

        ideas = self.analyze_trends_and_patterns()
        assert isinstance(ideas, list)

        reused_content = self.repurpose_existing_content()
        assert isinstance(reused_content, list)

        print("All tests passed!")

    def monitor_performance(self):
        start_time = datetime.datetime.now()
        self.main_function("Test Prompt")
        end_time = datetime.datetime.now()
        print("Response time: {}".format(end_time - start_time))

        process = psutil.Process(os.getpid())
        print("CPU usage: {}%".format(psutil.cpu_percent()))
        print("Memory usage: {} MB".format(process.memory_info().rss / 1024 / 1024))

    def user_feedback(self, feedback):
        feedback_collection = self.mongo_db_client["feedback"]
        feedback_collection.insert_one({"feedback": feedback})

    def generate_report(self):
        data = self.mongo_db_client.find_one(self.social_media_collection_name)
        report = "Social media data for the past 30 days:\n\n"
        report += data["data"].to_string(index=False)

        return report

    def preprocess_data(self, data):
        data = data.dropna()
        data = data.reset_index(drop=True)
        return data

    def handle_errors(self):
        try:
            self.main_function("Test Prompt")
        except Exception as e:
            logging.error(e)
            self.send_alert()

    def log_requests_responses(self):
        logging.basicConfig(filename='requests.log', level=logging.DEBUG)
        logging.debug('Request made at {}'.format(datetime.datetime.now()))
        self.main_function("Test Prompt")
        logging.debug('Response received at {}'.format(datetime.datetime.now()))

    def encrypt_data(self, data):
        key = Fernet.generate_key()
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return (encrypted_data, key)

    def decrypt_data(self, data, key):
        f = Fernet(key)
        decrypted_data = f.decrypt(data).decode()
        return decrypted_data

    def balance_load(self):
        if len(requests.get("http://localhost:5000").json()) > 10:
            pass
        else:
            self.main_function("Test Prompt")

def main():
    secrets = openai_secret_manager.get_secret("social_media_ai")
    google_analytics_api_key = secrets["google_analytics_api_key"]
    openai_api_key = secrets["openai_api_key"]
    mongodb_connection_string = secrets["mongodb_connection_string"]
    mongodb_client = MongoDBClient(mongodb_connection_string)
    social_media_ai = SocialMediaAI(mongodb_client, google_analytics_api_key, openai_api_key)

    # Call different functions to test
    social_media_ai.main_function("Test Prompt")
    social_media_ai.test_ai_assistant()
    social_media_ai.monitor_performance()
    social_media_ai.user_feedback("Some feedback")
    social_media_ai.generate_report()
    social_media_ai.handle_errors()
    social_media_ai.log_requests_responses()
    encrypted_data, key = social_media_ai.encrypt_data("Some sensitive data")
    decrypted_data = social_media_ai.decrypt_data(encrypted_data, key)
    social_media_ai.balance_load()

if __name__ == "__main__":
    main()

       


