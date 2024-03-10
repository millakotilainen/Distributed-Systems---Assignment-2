import datetime
from socketserver import ThreadingMixIn
import xml.etree.ElementTree as ET
from xmlrpc.server import SimpleXMLRPCServer

import requests


# Threading
class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

# RPC Server class


class rpcServer:
    def __init__(self):
        try:
            self.database = ET.parse('database.xml')
        except ET.ParseError:
            # If parsing fails, create an empty XML structure
            self.database = ET.ElementTree(ET.Element('notes'))
        self.root = self.database.getroot()

    # Server side for adding notes
    def add_note(self, topic, text, timestamp):
        # Check if there already is a note for this topic
        for note in self.root.findall('note'):
            if note.find('topic').text == topic:
                text_elem = note.find('text')
                # Adding new text to existing text
                text_elem.text += f"\n{text}"
                timestamp_elem = note.find('timestamp')
                timestamp_elem.text = timestamp  # Updating the timestamp
                self.database.write('database.xml')
                return "Note added to existing topic"

        # Create a new note element
        note = ET.Element('note')
        topic_elem = ET.SubElement(note, 'topic')
        topic_elem.text = topic
        text_elem = ET.SubElement(note, 'text')
        text_elem.text = text
        timestamp_elem = ET.SubElement(note, 'timestamp')
        timestamp_elem.text = timestamp

        # Append the note to the root element
        self.root.append(note)
        # Write the changes back to the XML file
        self.database.write('database.xml')
        return "Note added."

    def get_notes(self, topic):
        # print(topic)
        notes = []
        try:
            tree = ET.parse('database.xml')
            root = tree.getroot()

            for note in root.findall('note'):
                # Making sure the results aren't case sensitive
                if note.find('topic').text.lower() == topic:
                    # print("found " + topic)
                    text = note.find('text').text
                    timestamp = note.find('timestamp').text

                    notes.append(
                        {'text': text, 'timestamp': timestamp})
        except ET.ParseError:
            print("Failed to parse the XML file.")
        return notes

    def query_wikipedia(self, topic):
        try:
            res = requests.get(
                f"https://en.wikipedia.org/w/api.php?action=opensearch&search={topic}&limit=1&format=json")
            data = res.json()
            # Extracting the first title from the list of titles
            title = data[1][0]
            # First lin from list of links
            link = data[3][0]
            return {"title": title, "link": link}
        except Exception as e:
            return f"Error querying Wikipedia API: {e}"

    def add_wikipedia_link(self, topic):
        for note in self.root.findall('note'):
            if note.find('topic').text.lower() == topic.lower():
                info = self.query_wikipedia(topic)
                if isinstance(info, dict):
                    link = info.get('link')
                    text_elem = note.find('text')
                    existing_text = text_elem.text
                    if f"Wikipedia Link: {link}" not in existing_text:
                        wikipedia_note = f"\n\nWikipedia Link: {link}"
                        text_elem.text = existing_text + wikipedia_note
                        self.database.write('database.xml')
                        return f"Wikipedia link added for {topic}"
                else:
                    return f"Error: {info}"
        # If the note doesn't exist, add new note
        new_note = ET.Element('note')
        topic_elem = ET.SubElement(new_note, 'topic')
        topic_elem.text = topic
        info = self.query_wikipedia(topic)
        if isinstance(info, dict):
            link = info.get('link')
            text_elem = ET.SubElement(new_note, 'text')
            text_elem.text = f"Wikipedia Link: {link}"
            timestamp_elem = ET.SubElement(new_note, 'timestamp')
            timestamp_elem.text = datetime.datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
            self.root.append(new_note)
            self.database.write('database.xml')
            return f"Topic {topic} created and Wikipedia link added"
        else:
            return f"Error: {info}"

    def handle_add_wikipedia_link(self, topic):
        response = self.add_wikipedia_link(topic)
        return response


if __name__ == '__main__':
    server = SimpleXMLRPCServer(('localhost', 8080))
    server.register_instance(rpcServer())
    server.register_function(
        rpcServer().handle_add_wikipedia_link, 'add_wikipedia_link')
    server.serve_forever()
