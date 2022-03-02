import time

# Decorator to attempt connections again if there was an exception
def retry(func, tries=3, wait=3):
    def wrapper(*args, **kwargs):
        attempts = 0
        delay = wait

        while attempts < tries:
            try:
                return func(*args, **kwargs)

            except Exception as e:
                print(e)
                attempts += 1
                if not attempts == tries:
                    print('Attemping to connect again...')
                    time.sleep(delay)
                    delay *= 2
                    
        else:
            print("Given up trying to connect")
            raise Exception
    return wrapper