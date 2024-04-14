import sqlite3

def get_connection():
  # Connect to SQLite database (or create it if it doesn't exist)
  conn = sqlite3.connect('meetings.db')
  c = conn.cursor()

  # Create a table to store meeting information and recording file location
  c.execute('''CREATE TABLE IF NOT EXISTS meeting_recordings
              (id INTEGER PRIMARY KEY, meeting_name TEXT, recording_file TEXT)''')

  # Commit the changes and close the connection
  conn.commit()
  return conn

def write_to_database(meeting_name, recording_file):
  conn = get_connection()
  c = conn.cursor()
  c.execute("INSERT INTO meeting_recordings (meeting_name, recording_file) VALUES (?, ?)",
            (meeting_name, recording_file))
  conn.commit()
  conn.close()
  return "Meeting recorded and information saved to database."