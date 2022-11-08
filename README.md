# Scoro
Hello everyone! Scoro is a Python library for handling data by their file titles.
Scoro handles and creates files based on user defined attributes while tracking those with similar attributes.

If you had a recipe folder, you could track the recipes based on type of dish, main ingredient, rating, etc.
If you were working with a folder of books, you could track the author, title, year, rating, if you have read, etc. 
There would then be a text file log that contains each entry of that type. 

Following our dessert recipe library example:
A log would track each dish, main ingredient, and rating. 
If we were bakers, a log of dishes might look like this:
```
;cake
;custard
;parfait
pie
;syrup
tarte
```

Each dessert recipe stored would look have this format and look like this:
```
dessert-type_main-ingredient_rating.ext
pie_blueberry_3.txt
## a three start blueberry pie recipe
```

Notice in the log example above, some entries have a ``;`` check in front while some do not.
Those that are checked with a ``;`` are not selected and those that do not have a check are selected.
This is a handy feature of Scoro in that you could select all recipes of only a type, ingredient, and rating.
If you wanted only the highest stars; you could set your ratings log up to look like:
```
;1
;2
3
```

This would only gather 3 / 3 star recipes.
To gather the recipes, you would need to use the pull command. 
Pulling will return the file locations for each recipe or transfer all the files to an desired output location.


## Installation
Use the package manager pip to install Scoro.
```
pip install Scoro
```

## Usage
For usage within your own programs, here is a quick usage:
```
# Creates the object
p1 = scoro.Scoro()

# Adds logs
p1.add_log("dessert_type", "main_ingredient", "stars")

# Making a bunch of dishes. Content could be what you want!
desserts = ["cake", "pie"]
main_ingredient = ["blueberry", "apple", "Strawberry"]
stars = [1, 2, 3]

for entry in zip(desserts, main_ingredients, stars):
    recipe = "Recipe"
    p1.create(entry, content=recipe)
    
# Unchecks all three stars
p1.uncheck("3", log="stars")

# Pulls all the three star recipes 
p1.pull()

# Prints all recipes found
p1.post()


```


But, if you want to get creative, then here is the full docs:
```
import Scoro

# Initializes scoro
scoro_example = scoro.Scoro()

## Or with all possible options
## Storage - Path of Storage
## logs - Path of logs folder
## output - Path of output folder
## titles - Adds logs from title of string or list of strings
## reset - Reset all logs
## close - Autosettles (leave on)
## send - Sets pull to auto move files to output folder
scoro_example = scoro.Scoro(storage="./storage/", logs="./logs/", output="./output/",
                 titles=None, reset=False, close=True, send=False)


# Adds a log(s)
## title - string or list of strings for logs to add
scoro_example.add_log(title)

# Deletes a log
## title - string or list of strings for logs to delete
scoro_example.delete_log(title)

# Returns a dictionary of the log content
## title - string for log to return
scoro_example.get_log_content(title)

# Prints the contents of all logs
scoro_example.post()

# Creates a new file in storage based on your inputs
## Attributes - a list of terms for the filename (term1_term2_term-n)
## Content - The text within the document
## Extension - Default .txt
scoro_example.create(attributes, content, extention="txt")

# Pulls
## match - If you want the pull content to match only exactly what is unchecked
## send - If you want to pull content to your output folder
## output - Path of alternative output folder
scoro_example.pull(match=False, send=False, output="")

# Check / Unchecks a term
## Terms - String or list of strings to (un)check
## log - Optional specified log
scoro_example.check(terms, log="")
scoro_example.uncheck(terms, log="")

# Reset all logs
scoro_example.reset()
```

