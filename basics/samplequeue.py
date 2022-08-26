import asyncio

from random import choice
from asyncio import Queue


NUM_OF_CUSTOMERS = 5
NUM_OF_COOKS = 2

class Food:
    def __init__(self, name: str, wait_time_in_sec: int) -> None:
        self._name = name
        self._wait_time_in_sec = wait_time_in_sec

    @property
    def name(self):
        return self._name

    @property
    def wait_time_in_sec(self):
        return self._wait_time_in_sec


    def __str__(self) -> str:
        return "Food name: {}, wait time: {}".format(self._name, self._wait_time_in_sec)


class Customer:
    def __init__(self, customer_id: int, food_wanted: Food) -> None:
        self._customer_id = customer_id
        self._food_wanted = food_wanted

    @property
    def food(self) -> Food:
        return self._food_wanted

    @property
    def customer_id(self):
        return self._customer_id
    
    
class Chef:
    def __init__(self, id: int) -> None:
        self._id = id

async def produce(cust_queue: Queue, consumer_id: int):
    all_food = [
        Food("pizza", 5),
        Food("salad", 3),
        Food("fries", 2),
        Food("fried_chicken", 8)
    ]
    food_wanted = choice(all_food)
    new_customer =  Customer(
        customer_id=consumer_id, 
        food_wanted=food_wanted)

    await cust_queue.put(new_customer)
    message = f"customer id:{consumer_id} came in and wants {food_wanted.name} that will take {food_wanted.wait_time_in_sec} seconds"
    print(message)

async def consumer(cust_queue: Queue, chef_id: int):
    while True:

        customer = await cust_queue.get()

        customer_id = customer.customer_id
        food = customer.food
        food_name = food.name
        food_cook_time = food.wait_time_in_sec

        print(f"chef #{chef_id} is taking care of customer id:{customer_id} with order {food_name}")
        await asyncio.sleep(food_cook_time)

        print(f"chef #{chef_id} finished cooking {food_name}")
        cust_queue.task_done()

async def get_chef_queue(n=1) -> Queue:
    chef_queue = Queue()
    for i in range(n):
        chef = Chef(id=i)
        await chef_queue.put(chef)
    return chef_queue

async def main():
    customer_queue = Queue()

    producers = [asyncio.create_task(produce(customer_queue, i)) 
                 for i in range(NUM_OF_CUSTOMERS)]
    
    consumers = [asyncio.create_task(consumer(customer_queue, i))
                 for i in range(NUM_OF_COOKS)]
    
    await asyncio.gather(*producers)
    await customer_queue.join()
    
    for c in consumers:
        c.cancel()
 
asyncio.run(main())    