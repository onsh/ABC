import time
import random

for i in range(5):
    print("START")
    rndm = random.randint(1, 10)
    time.sleep(rndm)
    print(str(rndm) + ' sec.')

