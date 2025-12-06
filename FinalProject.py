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

API_KEY = "AIzaSyCvLlt5kR9WAVm_8Lal7NvvPxcvI7O7yzo" #This creates an agreement between googleAPI and me and like it knows that im the one using it
SEARCH_ENGINE_ID = "97dd7e609628d4593" #This is my own personally made google search engine that I will do the searching on. Well it's more like a copy of the google search engine you can make using CustomSearchEngine by google



#THIS PART IS STRICTLY FOR THE TABLE OF DATA
#-----------DATABASE-----------------

def initialize_database():
    global connect, cursor
    # Connect to the database
    connect = sqlite3.connect('recipes.db')
    cursor = connect.cursor()

    # SUCCESSFULLY CONNECTED AND CREATED THE DATABASE
    print("DATABASE HAS BEEN CONNECTED")

    # Create the table for RecipeBook
    #this table takes a recipe number, a name, a link to the website, and the ingredients list
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
        "INSERT INTO RecipeBook (RecipeName, url, ingredients_summary) VALUES (?, ?, ?)", #saves recipe in the back end by uploading it into database
        (name, url, summary) #the parameters take a name url and summary
    )
    connect.commit()

    
initialize_database()

def view_saved_recipe(): #method to view my saved recipes
    result_box.delete("1.0", END) #from the start to the end we want to wipe the result box and start fresh
    cursor.execute("SELECT RecipeName, url FROM RecipeBook")#this takes all the names and url from the recipebook database that i had stored earlier using save recipe
    saved = cursor.fetchall()#fetch all as it's name suggests literally grabs everything

#-----------Search For Recipes Using API---------------------#

def search_recipes(query):
    url = "https://www.googleapis.com/customsearch/v1" #this is the search engine im using
    params = { #this parameter dictionary is needed to tie everything back to my search engine
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query + " recipe" #especially the query this is what is being searched
    }

    response = requests.get(url, params)
    data = response.json() #this .json() line what it does is it creates a network request
    results = [] #empty result list during the creation of the search we will wipe this everytime

    if "items" not in data: #exceptions or if something doesnt exist
        return results  # No results or quota exceeded

    for item in data["items"]: #this is the important part. This extracts the title, url, and a short text snippet from the website
        title = item.get("title")
        link = item.get("link")
        snippet = item.get("snippet")
        results.append((title, link, snippet)) #appends it to the list of results

    return results


#------------GUI METHODS PAGE BY PAGE----------------#
def on_search():
    result_box.delete("1.0", END)
#what this line does is actually clear the entire text box.
#What it means is at line 1 character 0 delete everything to the end
    query = entry.get().strip()
    if not query:
        messagebox.showinfo("Info", "Type something to search.") #this will pop up saying type something to search
        return
    results = search_recipes(query)
    if not results:
        result_box.insert(END, "No results found or API error. \n")#this is shown inside the result box saying that nothing matches the search
        return
    global last_results
    last_results = results
    for i, (title, link, snip) in enumerate(results, start=1): #enumerate iterates through everything and gives it a number
        result_box.insert(END, f"{i}. {title}\n{link}\n{snip}\n\n")


def on_save():
    try: #error exceptions
        # get the number from the entry
        index = int(sel_entry.get()) - 1
        
        # check if last_results exists and index is valid
        if index < 0 or index >= len(last_results):
            raise ValueError("Invalid number")#This triggers a ValueError exception which is like invalid input or if it expects a positive and gets a negative 
        
        # get the recipe and save
        title, link, snippet = last_results[index]
        save_recipe_to_database(title, link, snippet)
        messagebox.showinfo("Saved", f"Saved: {title}")
    
    except (ValueError, NameError):
        messagebox.showerror("Error", "Enter a valid result number to save.") #this is an exception where if the number isnt valid like in this case it's not 1-10

def on_view_saved_():
    result_box.delete("1.0", END)# wipes the result box to put in new text
    cursor.execute("SELECT RecipeName, url FROM RecipeBook ORDER by RecipeNum DESC")#Selects from the recipes i have saved and once the button is clicked it will show them
    rows= cursor.fetchall()

    if not rows: 
        result_box.insert(END, "No saved recipes. \n")
        return
    for name, url in rows:
        result_box.insert(END, f"{name}\n{url}\n\n")#format for the thing we are inserting into the result box. Name and URL
        
#-----------------GUI-----------------#

#I had ChatGPT help me make a cool looking GUI using tkinter
#Everything works as it should and each button works fine too

root = tkinter.Tk()
root.title("Recipe Finder")#creates the name of the window
root.geometry("600x500")

tkinter.Label(root, text="Search Recipes:").pack()#search recipes text
entry = tkinter.Entry(root, width=50)#entry box below it
entry.pack()

search_button = tkinter.Button(root, text="Search", command=on_search)#search button
search_button.pack()

tkinter.Label(root, text="Results:").pack()#results text below search button
result_box = tkinter.Text(root, width=70, height=20)#result box 
result_box.pack()

tkinter.Label(root, text="Enter number to save:").pack()#save text
sel_entry = tkinter.Entry(root, width=10)
sel_entry.pack()

save_button = tkinter.Button(root, text="Save Recipe", command=on_save)#save button
save_button.pack()

view_button = tkinter.Button(root, text="View Saved Recipes", command=on_view_saved_)#view the saved recipes button
view_button.pack()

root.mainloop()

