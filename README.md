# Scoro

Hello~! Welcome to Scoro! Scoro is a framework for handling files by their name and retrieving groups of files based on selected names.
This package is great for storing a large amount of files as a database bound in a folder. 
The different attributes of each file is logged by variant of that name.

#### Quick guide
```
sco = scoro.Scoro(storage="./storage/", index_location="./indexes/", output="./output/",
                 initialized_titles=None, reset=True, close=True)  
# Initialize scoro
# Storage = location of files to be tracked. Defaults to "./storage/"
# logs = Location for registering each log of found attributes
# output = If there is anywhere you want to pull your files to
# initialized_titles = If you want to add a log for tracking upon initialization
# reset = If you want to reset the logs (to an untouched, all check state)
# close = autosettle upon each action. Don't tamper unless you know what you're doing

sco.add_log(title, order=-1):
# Adds a log
# order tracks which term in the file name to track for this log

sco.settle()
# Finalizes changes

sco.delete_log(title)
# Deletes a log

sco.get_logs_names()
# Returns names of all logs

sco.refresh_logs_list()
# Refreshes the logs based on what is in storage

sco.get_contents()
# Returns a dictionary of the contents of all logs
```


#### Case Study
Imagine you had a bunch of word documents containing dessert recipes.
You have cakes, pies, and tortes in a few different flavors including blueberry, carmel, apple, huckleberry, and cherry.
You tried these pies and devised a star system with 0 = untested, 1 = edible, 2 = very delicious.
Each recipe would be categorized with the system of type_flavor_stars.

Inside your folder of desserts, there would be a folder full of .lst files.
Each file would hold all of that type found in storage.
So... 'fruit_2.lst' would hold blueberry, huckleberry, etc.
'stars_3.lst' would hold all possible star values (0, 1, 2).
Each term would be prepositioned with a semi-colon (;).

You can initialize scoro by calling:
```
p1 = scoro.Scoro()
```

Now let's say that you wanted all pie recipes made of blueberry or cherry that were two stars or more.
With that, you could manually find the indexes and unmark the desired traits.
So, in the indexes you would see something like this for type of dessert:
```
;cake
pie
;tarte
```
Notice how 'pie' is unchecked. 
This signals to Scoro to pull any pies.
For flavors, we can do the same:
```
;apple
blueberry
;carmel
cherry
```
This will find any blueberry and cherry desserts.
You can do the same with two stars or more stars.
Alternatively, if you don't want to be working with editing text files or if there are many entries that you want to work with;
you can edit them by calling methods such as:
```
to_uncheck = ['blueberry', 'cherry', 'pie', '2']
p1.uncheck(to_uncheck)
```

If you changed your mind about having two stars only, you can easily re-check it.
Also, you can optionally select which index:
```
p1.check('2', 'stars')
```

Now from there, you can pull them. 
There are two ways to do it, 
you can either pull the files, or move the files somewhere.
With no matching, it pulls everything that meets one of the requirements.
```
p1.pull()
['./storage/pie_cherry_1.txt', './storage/pie_cherry_2.txt', './storage/pie_carmel_0.txt', './storage/pie_carmel_1.txt', './storage/cake_blueberry_1.txt', './storage/cake_blueberry_0.txt', './storage/pie_carmel_2.txt', './storage/pie_apple_1.txt', './storage/pie_apple_2.txt', './storage/pie_blueberry_2.txt', './storage/pie_blueberry_2.txt', './storage/pie_blueberry_0.txt', './storage/pie_blueberry_0.txt', './storage/pie_huckleberry_2.txt', './storage/tarte_blueberry_1.txt', './storage/tarte_blueberry_2.txt']
```

Too many recipes that aren't what we want. 
If we only wanted recipes that fit our parameters
AND we wanted to send that to our to-make folder somewhere on our machine:
```
to-make-folder = "~/to-make-example-folder/"
p1.pull(match=True, send=True, output=to-make-folder)
['./storage/pie_blueberry_2.txt'] sent to ~/to-make-example-folder/
```
There we go! One blueberry pie recipe!
You can repeat the whole process to pull anything you want anywhere you want.
If you set the indexes up in a way that you don't feel like fixing;
theres a fix for that!
Simply reset-indexes by calling:
```
p1.reset()
```
There ya go! A crash course on Scoro.
