# Final Project
# Online Recipe Finder
# Geoffrey Won
# 12/01/2025

import sqlite3
import requests
import tkinter
from tkinter import messagebox, END



#THE API Key and Search Engine (I had to use CHATGPT) to figure out how to create these 2
#----------------API----------------------------

API_KEY = "AIzaSyCvLlt5kR9WAVm_8Lal7NvvPxcvI7O7yzo" #This creates an agreement between googleAPI and me
SEARCH_ENGINE_ID = "97dd7e609628d4593" #This is my own personally made google search engine that I will do the searching on



#THIS PART IS STRICTLY FOR THE TABLE OF DATA
#-----------DATABASE-----------------

def initialize_database():
    global connect, cursor
    # Connect to the database
    connect = sqlite3.connect('recipes.db')
    cursor = connect.cursor()

    # SUCCESSFULLY CONNECTED AND CREATED THE DATABASE
    print("DATABASE HAS BEEN CONNECTED")

    # Create the table
    cursor.execute( """
    CREATE TABLE IF NOT EXISTS RecipeBook (
        RecipeNum INTEGER PRIMARY KEY AUTOINCREMENT,
        RecipeName TEXT,
        url TEXT,
        ingredients_list TEXT
    )
    """)

    last_results = []
    connect.commit()
    

def save_recipe_to_database(name, url, summary):
    cursor.execute(
        "INSERT INTO RecipeBook (RecipeName, url, ingredients_summary) VALUES (?, ?, ?)",
        (name, url, summary)
    )
    connect.commit()

    
initialize_database()

def view_saved_recipe():
    result_box.delete("1.0", END)
    cursor.execute("SELECT RecipeName, url FROM RecipeBook")
    saved = cursor.fetchall()

#-----------Search For Recipes Using API---------------------#

def search_recipes(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query + " recipe"
    }

    response = requests.get(url, params)
    data = response.json()
    results = []

    if "items" not in data:
        return results  # No results or quota exceeded

    for item in data["items"]:
        title = item.get("title")
        link = item.get("link")
        snippet = item.get("snippet")
        results.append((title, link, snippet))

    return results


#------------GUI METHODS PAGE BY PAGE----------------#
def on_search():
    result_box.delete("1.0", END)
#what this line does is actually clear the entire text box.
#What it means is at line 1 character 0 delete everything to the end
    query = entry.get().strip()
    if not query:
        messagebox.showinfo("Info", "Type something to search.")
        return
    results = search_recipes(query)
    if not results:
        result_box.insert(END, "No results found or API error. \n")
        return
    global last_results
    last_results = results
    for i, (title, link, snip) in enumerate(results, start=1): #enumerate iterates through everything and gives it a number
        result_box.insert(END, f"{i}. {title}\n{link}\n{snip}\n\n")


def on_save():
    try:
        # get the number from the entry
        index = int(sel_entry.get()) - 1
        
        # check if last_results exists and index is valid
        if index < 0 or index >= len(last_results):
            raise ValueError("Invalid number")
        
        # get the recipe and save
        title, link, snippet = last_results[index]
        save_recipe_to_database(title, link, snippet)
        messagebox.showinfo("Saved", f"Saved: {title}")
    
    except (ValueError, NameError):
        messagebox.showerror("Error", "Enter a valid result number to save.")

def on_view_saved_():
    result_box.delete("1.0", END)
    cursor.execute("SELECT RecipeName, url FROM RecipeBook ORDER by RecipeNum DESC")
    rows= cursor.fetchall()

    if not rows:
        result_box.insert(END, "No saved recipes. \n")
        return
    for name, url in rows:
        result_box.insert(END, f"{name}\n{url}\n\n")
        
#-----------------GUI-----------------#

#I had ChatGPT help me make a cool looking GUI using tkinter
#Everything works as it should and each button works fine too

root = tkinter.Tk()
root.title("Recipe Finder")
root.geometry("600x500")

tkinter.Label(root, text="Search Recipes:").pack()
entry = tkinter.Entry(root, width=50)
entry.pack()

search_button = tkinter.Button(root, text="Search", command=on_search)
search_button.pack()

tkinter.Label(root, text="Results:").pack()
result_box = tkinter.Text(root, width=70, height=20)
result_box.pack()

tkinter.Label(root, text="Enter number to save:").pack()
sel_entry = tkinter.Entry(root, width=10)
sel_entry.pack()

save_button = tkinter.Button(root, text="Save Recipe", command=on_save)
save_button.pack()

view_button = tkinter.Button(root, text="View Saved Recipes", command=on_view_saved_)
view_button.pack()

root.mainloop()

