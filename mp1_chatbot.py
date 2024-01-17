import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import redis
import json
#import random
import randfacts
import yahoo_fin
from yahoo_fin import stock_info

# Available commands to be printed for the !help command
available_commands = """
                    Here are the available commands that I support:
                        !help: List of commands
                        !weather: Weather update
                        !fact: Random fun fact
                        !whoami: Your user information

                    These are your available options:
                        1: Identify yourself
                        2: Join a channel
                        3: Leave a channel
                        4: Send a message to a channel
                        5: Get info about a user
                        6: Get current stock price for selected companies
                        7: Play a short Redis quiz game to test your Redis knowledge
                        8: Exit
                    """


# Create dictionary with weather data 
weather_dict =  {                   
                "new york": {
                "Temperature": 72,
                "Wind Speed": 10,
                "Chance of Rain": 30
                },
                "boston": {
                "Temperature": 68,
                "Wind Speed": 5,
                "Chance of Rain": 15    
                },
                "los angeles": {
                "Temperature": 80,
                "Wind Speed": 5,
                "Chance of Rain": 10
                },
                "chicago": {
                "Temperature": 65,
                "Wind Speed": 15,
                "Chance of Rain": 50
                    }
                 }

# Create guide of company names and stock symbols
stocks = """ 
             Google: GOOGL
             Amazon: AMZN
             Meta: META
             Apple: AAPL
             JPMorgan Chase and Co: JPM
             Goldman Sachs Group Inc: GS
             Morgan Stanley: MS
             AbbVie Inc: ABBV
             Pfizer Inc: PFE
             
             """

# Create a list of stored stocks
stocks_list = ['GOOGL', 'AMZN', 'META', 'AAPL', 'JPM', 'GS', 'MS', 'ABBV', 'PFE']

# Initialize Redis connection
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

class Chatbot:
    def __init__(self, host='redis', port=6379):
        self.client = redis.StrictRedis(host=host, port=port)
        self.pubsub = self.client.pubsub()
        self.username, self.age, self.gender, self.location = None, None, None, None 

    def introduce(self):
        # Provide an introduction and list of commands
        intro = """                       
                                     (^.^)
                                    /     \\
                                    |  o  |
                                    \  -  /
                                     \___/

        Hello! My name is Brobot. I'm your friendly neighborhood Redis chatbot.
        
        Here are the special commands that I support:
            !help: List of commands
            !weather: Weather update
            !fact: Random fun fact
            !whoami: Your user information

        These are your options:
            1: Identify yourself
            2: Join a channel
            3: Leave a channel
            4: Send a message to a channel
            5: Get info about a user
            6: Get current stock price for selected companies
            7: Play a short Redis quiz game to test your Redis knowledge
            8: Exit
        """
        print(intro)
        while not self.username:
            self.username = input('Please enter a username to begin: ') 
        
        
    def identify(self, age, gender, location):
        # Store user information in Redis
         user_key = f'user:{self.username}'
         redis_client.hset(user_key, mapping = {
            'name': self.username,
            'age': age,
            'gender': gender,
            'location': location
         })
         self.age = age
         self.gender = gender
         self.location = location
         print(f'Hello, {self.username}' + "! You've been identified.")

   
    def join_channel(self, channel_name):
        # Join a channel
        redis_client.sadd(f'channel:{channel_name}', self.username)
        print(f'Joined channel: {channel_name}')
        choice = input("Do you want to [listen] or [send]?: ")

        if choice == "listen":
            pubsub = redis_client.pubsub()
            pubsub.subscribe(channel_name)
            print(f"Listening to channel: {channel_name} ...")
            while True:
                for message in pubsub.listen():
                    if message['type'] == 'message':
                        print(f"[{channel_name}] {message['data'].decode('utf-8')}")

        elif choice == "send":
            print(f"Sending messages to channel: {channel_name} ...")
            while True:
                message = input('Enter your message or enter "stop" to exit: ')
                if message.lower() == "stop":
                    break
                else:
                    message = message = f'{self.username}: {message}'
                    message_obj = {
                                "from: ": self.username,
                                "message: ": message
                                }
                    redis_client.publish(channel_name, message)

    def leave_channel(self, channel_name):
        # Leave a channel
        redis_client.srem(f'channel:{channel_name}', self.username)
        print(f'Left channel: {channel_name}')
        

    def send_message_to_channel(self, channel_name, message):
        # Send a message to a channel
        message_obj = {
            "from: ": self.username,
            "message: ": message
        }
        redis_client.publish(channel_name, json.dumps(message_obj))
        print('Message sent successfully')


    def get_random_fact(self):
        # Display a random fact for the user
        fact = randfacts.get_fact()
        print(fact)

    def get_weather(self, city):
        # Retrieve weather information for a city for the user
        if city.lower() in weather_dict:
            city_data = weather_dict[city]
            print(f"Weather data for {city}:")
            print(f"Temperature: {city_data['Temperature']}°F")
            print(f"Wind Speed: {city_data['Wind Speed']} mph")
            print(f"Chance of Rain: {city_data['Chance of Rain']}%")

        else:
            print(f"Sorry, weather data for {city} is not available. Please enter another city.")

    def get_other_user(self, username):
        # Get user info from the database
        user_key = f'user:{username}'
        user_info = self.client.hgetall(user_key)
        print("User Information:")
        for field, value in user_info.items():
            print(f"{field.decode()}: {value.decode()}")

    def get_user(self):
        # Get user info from the database
        user_key = f'user:{self.username}'
        user_info = self.client.hgetall(user_key)
        print("User Information:")
        for field, value in user_info.items():
            print(f"{field.decode()}: {value.decode()}")

    def get_stock(self, corp):
        # Get current stock price of a company and display it to the user
        stock = corp.upper()
        if stock not in stocks_list:
            print("Sorry. Price information about this stock is not available.")
        else:
            price = stock_info.get_live_price(stock).round(2)
            print(f"The current market price for {stock} stock is: ${price}")

    def quiz_game(self):
        # Allow the user to play a short Redis quiz game
        print('Welcome to the Redis Quiz! ')
        score = 0
        total_questions = 5
        
        answer=input('Question 1: What command allows you to add multiple values to a set in Redis? ')
        if answer.lower()=='sadd':
            score += 1
            print('Correct! :D')
        else:
            print('Wrong answer :(')
        
        answer=input('Question 2: What Redis command lists all the values in the hash? ')
        if answer.lower()=='hvals':
            score += 1
            print('Correct! :D')
        else:
            print('Wrong answer :(')
        
        answer=input('Question 3: What Redis command lists all the keys in the hash? ')
        if answer.lower()=='hkeys':
            score += 1
            print('Correct! :D')
        else:
            print('Wrong answer :(')

        answer=input('Question 4: What Redis command allows for the insertion of multiple key-value pairs? ')
        if answer.lower()=='mset':
            score += 1
            print('Correct! :D')
        else:
            print('Wrong answer :(')

        answer=input('Question 5: What Redis command allows for multiple clients to listen for messages published to a specifc key? ')
        if answer.lower()=='subscribe':
            score += 1
            print('Correct! :D')
        else:
            print('Wrong answer :(')
        
        print('Thank you for playing the Redis Quiz game! You attempted', score, "questions correctly.")
        final_score = score/total_questions * 100
        print(f"Your final score is {final_score}%")

def main():
    bot = Chatbot()
    bot.introduce()

    # Main interaction loop here
    while True:
        command = input("Enter your command: ")
        if command == '1':
            age = input("Enter your age: ")
            gender = input("Enter your gender: ")
            location = input("Enter your location: ")
            bot.identify(age, gender, location)
        elif command == '2':
            channel_name = input("Enter the channel you want to join: ")
            bot.join_channel(channel_name)
        elif command == '3':
            channel_name = input("Enter the channel you want to leave: ")
            bot.leave_channel(channel_name)
        elif command == '4':
            channel_name = input("Enter the channel you want to send your message to: ")
            message = input("Enter your message: ")
            bot.send_message_to_channel(channel_name, message)
        elif command == '5':
            username = input("Enter the username you want to get info about: ")
            bot.get_other_user(username)
        elif command == '6':
            print("Below is a list of some famous companies and their stock symbols.")
            print(stocks)
            while True:
                corp = input('Enter the company stock symbol to get the current stock price, or enter "quit" to exit: ')
                if corp.lower() == "quit":
                    print("Exiting the stock mode.")
                    break
                else:
                    bot.get_stock(corp)
        elif command == '7':
            bot.quiz_game()
        elif command == '8':
            print("Bye for now. I hope you'll chat with me again soon!")
            break
        elif command == '!help':
            print(available_commands)
        elif command == '!fact':
            bot.get_random_fact()
        elif command == '!weather':
            while True:
                city = input('Enter the city for which you would like a weather update or enter "quit" to exit: ')
                if city.lower() == 'quit':
                    print("Exiting the weather mode.")
                    break
                else:
                    bot.get_weather(city)
        elif command == '!whoami':
            bot.get_user()
        else:
            print("Sorry, that's an invalid command. Please choose an option from the list or enter one of the special commands.")

if __name__ == "__main__":
    main()
   


