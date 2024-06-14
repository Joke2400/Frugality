import time
import logging
import threading
from app.utils.tests.fixture import test_client, orm_populated_clean_slate


def send_request(client):
    start_time = time.time()
    client.post(
        url="/stores/",
        json={
            "store_id": 542862479,
            "store_name": None
            }
        )
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000
    logging.debug(f"Request took {elapsed_time:.2f}ms")

"""
def test_store_route_sends_200(test_client, orm_populated_clean_slate):
    response = test_client.post(
        url="/stores/",
        json={
            "store_id": 542862479,
            "store_name": None
            }
        )
    assert response.status_code == 200
    

async def test_perf_of_100_store_requests(test_client, orm_populated_clean_slate):
    
    def send_requests():
        threads = []
        for _ in range(100):
            thread = threading.Thread(target=send_request, args=[test_client])
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()

    request_thread = threading.Thread(target=send_requests)
    start_time = time.time()
    request_thread.start()
    request_thread.join()
    
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000
    logging.debug(f"All requests took {elapsed_time:.2f}ms")
"""