from locust import HttpUser, task, between

class MLApiUser(HttpUser):
    wait_time = between(1, 3)  # Simulate user think time between requests

    @task(2)  # Weighted to run more often than insights
    def predict_image(self):
        with open("data/test/cats/9.jpg", "rb") as image_file:
            self.client.post("/predict", files={"file": image_file})

    @task(1)
    def get_insights(self):
        self.client.get("/data-insights")
