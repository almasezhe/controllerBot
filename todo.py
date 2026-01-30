import db

#Database Structure
#task TEXT, description TEXT, deadline TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP


#TODO
#add CRUD
#add Keyboard under the message
def add_todo(message:str):
    text = message.removeprefix("/addtask ").lstrip()
    cursor.execute('INSERT INTO TodoList (task, description, deadline) VALUES (?, ?, ?)', ('newuser', 'newuser@example.com', 28))
    connection.commit()