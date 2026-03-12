import requests
from collections import Counter

def test_routing():
    results = []
    for i in range(10):
        try:
            response = requests.get("http://localhost:7001/")
            print(f"Request {i+1}: Status {response.status_code}, Body: {response.text.strip()}")
            results.append(response.text.strip())
        except Exception as e:
            print(f"Request {i+1}: Failed with {e}")
            results.append("Failed")

    counts = Counter(results)
    print("\nSummary of responses:")
    for body, count in counts.items():
        print(f"'{body}': {count} times")

if __name__ == "__main__":
    test_routing()
