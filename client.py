# Distributed system using RPC
# First between N clients and a single server
# For 8-10 amount of servers linked has to increase

# The systems main functionality is to serve as a notebook

from datetime import datetime
import xmlrpc.client

# Ask user for input & send to server
# Topic, tect and timestamp for the note
# Name search terms to lookup data on wikipedia


def menu():
    print("Options:")
    print("1) Add note\n2) Get notes\n3) Query Wikipedia\n0) Quit")
    try:
        choice = int(input("Your choice: "))
        return choice
    except ValueError as error:
        print("Error:", error)


class rpcClient:
    def __init__(self):
        self.server = None

    def connect(self):
        try:
            self.server = xmlrpc.client.ServerProxy("http://localhost:8080")
        except Exception as error:
            print("Error:", error)
            exit()

    def start_client(self):
        while True:
            choice = menu()

            if choice == 1:
                topic = input("Enter your topic: ")
                text = input("Enter your note: ")
                date = datetime.now()
                timestamp = date.strftime("%m/%d/%Y - %H:%M:%S")

                if not self.server.add_note(topic, text, timestamp):
                    print("Couldn't add the note.")
                    return

            elif choice == 2:
                try:
                    search_topic = input("Enter the topic: ")
                    notes = self.server.get_notes(search_topic)
                    if notes:
                        # print(notes)
                        for note in notes:
                            print(f"Text: {note['text']}")
                            print(f"Timestamp: {note['timestamp']}")
                            print()
                        else:
                            print("No notes yet.")
                except Exception as e:
                    print("Error: ", e)
            elif choice == 3:
                wiki_topic = input(
                    "What do u want to search from Wikipedia? ").lower()
                res = self.server.add_wikipedia_link(wiki_topic)
                result = self.server.query_wikipedia(wiki_topic)
                if isinstance(result, dict):
                    print(f"Title: {result['title']}")
                    print(f"Link: {result['link']}")
            elif choice == 0:
                print("Thank u for using this program :)")
                break
            else:
                print("Invalid option. Please, try again.\n")

# If the topic exists on the XML, the data will be appended to the stucture => append the data to an existing topic
# If not, a new XML entry will be made


# Get the contents of the XML database on given topic
if __name__ == '__main__':
    client = rpcClient()
    client.connect()
    client.start_client()


# Security => involves communication over the network => authentication, encryption, authorization
# Scalability => Ensuring that the performance of the RPC system is not degraded as amount of clients increase => Load balancing
# Fault tolerance => Redundancy, failover
