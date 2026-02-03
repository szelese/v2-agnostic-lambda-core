import json
from locust import HttpUser, task, between

class AgnosticLambdaUser(HttpUser):
    # Avarage wait time between tasks
    wait_time = between(1, 2)
    # Base URL for the Lambda function endpoint
    @task
    def test_lambda_endpoint(self):
        payload = {
            "test_key": "locust_test_v2",
            "source": "performance_validation"
        }
        
        headers = {
            "Content-Type": "application/json"
        }

        # Root path test
        with self.client.post("/", data=json.dumps(payload), headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get("status") == "success":
                    response.success()
                else:
                    response.failure(f"Unexpected status logic: {res_data}")
            else:
                response.failure(f"HTTP Error: {response.status_code}")
    # Test for security headers on non-existent route
    @task(1)
    def test_security_route_protection(self):
        with self.client.get("/robots.txt", catch_response=True) as response:
            if response.status_code == 404:
                if "Strict-Transport-Security" in response.headers:
                    response.success()
                else:
                    response.failure("Security headers missing from 404 response")
            else:
                response.failure(f"Route protection failed: {response.status_code}")