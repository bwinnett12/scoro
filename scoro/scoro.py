"""
Indexer - Creates the system itself for logging all files.
"""
import glob
import os
from pathlib import Path

"""
Indexer is a system for tracking of Index(s). Each system tracks multiple records with separate names
"""
class Scoro:
    def __init__(self, storage="./storage/", location="./indexes/", initialized_titles=None, reset=True):
        if storage:
            self.storage = storage.rstrip("/") + "/"
        else:
            self.storage = "./storage/"

        if location:
            self.location = location.rstrip("/") + "/"
        else:
            self.location = "./indexes/"

        Path(self.location).mkdir(parents=True, exist_ok=True)
        Path(self.storage).mkdir(parents=True, exist_ok=True)

        self.indexes = []
        if initialized_titles:
            self.add_index(initialized_titles)

        if reset:
            self.refresh_indexes_list()
            self.settle()

    """
    Method for adding a term to an index
    """

    def paste(self, index, term):
        index_to_add_to = None
        for item in self.indexes:
            if item.title.lower() == index.title.lower():
                index_to_add_to = item
                break
        else:
            print("While pasting: Index {} not found".format(index))
            return False

        index_to_add_to.add(Term(term))

    """
    Method for writing all contents to their folder
    """

    def settle(self):
        for ind in self.indexes:
            ind.write_contents()

    '''
    Adds an index, creates the file
    Takes either a string or an array
    '''

    def add_index(self, title, order=-1):
        # If not empty...
        if not title:
            return False

        # If the order wasn't manually specified
        if order == -1:
            order = self.get_open_order()

        # If a single record...
        if type(title) == str:
            if not self.is_index(title):
                self.indexes.append(Index(title, self.location, order))

        # Else a multiple
        elif type(title) == list:
            for ind in title:
                if not self.is_index(ind):
                    self.add_index(ind, order=-1)

        else:
            print("Did not add Index")

        self.refresh_indexes_list()

    """
    Remove an index. Deletes the file - Alternatively, manually delete
    """

    def delete_index(self, title):
        if not title:
            print("While attempting to delete Index: title left blank")
            return False

        if type(title) == str:
            self.refresh_indexes_list()
            r = self.get_indexes_names()

            for i, x in enumerate(self.indexes):
                if x.title.lower().split("_")[0] == title.lower():
                    doomed_index = self.indexes[i]
                    break
            else:
                print("While attempting to delete Index: Index name \"{}\" not found".format(title))
                return False

            if os.path.exists(doomed_index.path()):
                os.remove(doomed_index.path())

            self.indexes.remove(doomed_index)
        if type(title) == list:
            for entry in title:
                self.delete_index(entry)

    """
    Returns a list of the names of all indexes
    """

    def get_indexes_list(self):
        return self.indexes

    """
    Returns a list of the names of each index
    """

    def get_indexes_names(self):
        return [obj.title.split("_")[0] for obj in self.get_indexes_list()]

    """
    Returns first open order
    """

    def get_open_order(self):
        taken_orders = []
        for ind in self.get_indexes_list():
            taken_orders.append(ind.get_order())

        taken_orders.sort()
        for i in range(1, len(taken_orders)):
            if i not in taken_orders:
                return i
        else:
            return len(taken_orders) + 1

    """
    Refreshes the indexes to whatever is already added in the indexes folder
    """

    def refresh_indexes_list(self):
        ## First section registers all indexes found locally
        all_index_addresses = []
        all_abridged_addresses = []

        for file in glob.glob(self.location + "*.lst"):
            abridged = Path(file).stem.split("_")[0]
            if abridged not in all_abridged_addresses:
                all_abridged_addresses.append(abridged)
                all_index_addresses.append(file)

        current_index_addresses = [o.address for o in self.get_indexes_list()]
        for addre in all_index_addresses:
            if addre not in current_index_addresses:
                split_addr = Path(addre).stem.split("_")
                self.add_index(split_addr[0], order=int(split_addr[1]))

        # Sort list of indexes by order
        self.indexes.sort(key=lambda x: x.order)

        ## Local storage
        local_files_dict = {int(self.indexes[x].order): [] for x in range(len(self.indexes))}

        for file in glob.glob(self.storage + "*"):
            full_term = Path(file).stem.split("_")[:len(self.indexes)]

            for index, value in enumerate(full_term):
                try:
                    local_files_dict[index + 1].append(value)
                except KeyError:
                    break

        for ind, key in enumerate(local_files_dict):

            ind_to_add = list(set(local_files_dict[key]))
            for i in ind_to_add:
                self.paste(self.indexes[ind], i)

        for ind in self.indexes:
            ind.sort_contents()

    """
    Retrieves a dictionary with content from each index
    """
    def get_contents(self):
        content_to_return = {}
        for ind in self.indexes:
            if ind.title not in content_to_return:
                content_to_return[ind.title] = ind.contents
        return content_to_return

    """
    Returns the content of an index
    """
    def get_content_index(self, title):
        return self.indexes[self.get_indexes_names().index(title)].contents

    '''
    Returns a bool of whether the potential new index is already found
    @bool
    '''
    def is_index(self, title):
        for ent in self.indexes:
            if title.lower() == ent.title.lower():
                return True
        return False

    """
    Prints the contents of each index
    """
    def post(self):
        print("Each file and its contents")
        # Calls post method of each index
        for i in self.indexes:
            i.post()
            if i != self.indexes[-1]:
                print("")

    """
    Retrieves each file that is marked
    """
    def pull(self):
        terms_to_get = {int(self.indexes[x].order): [] for x in range(len(self.indexes))}

        for i, index in enumerate(self.indexes):
            for term in index.contents:
                terms_to_get[i].append(term)

        files_of_interest = []
        for file in glob.glob(self.storage):
            split_term = Path.stem.split("_")

            for i in range(len(split_term)):
                if split_term[i] in terms_to_get[i]:
                    files_of_interest.append(file)

        return files_of_interest


"""
Index: The files that are being tracked
"""


class Index:
    def __init__(self, title, root, order):
        self.title = title
        self.order = order
        self.address = root.rstrip("/") + "/" + self.title + "_" + str(self.order) + ".lst"

        # Creates a new file
        Path(self.address).touch(exist_ok=True)

        # Resets the files then leaves blank
        self.reset_contents()
        self.contents = []

    """
    Gets the address of the Index
    """

    def path(self):
        return self.address

    """
    Adds a term to the index
    """

    def add(self, term):
        self.contents.append(Term(term))

    """
    Returns what index the index is
    """

    def get_order(self):
        return self.order

    """
    
    """

    def reset_contents(self):
        filee = open(self.address, "w")
        self.contents = []

    def get_contents(self):
        contents = []
        filee = open(self.address, "r")
        for line in filee.readlines():
            appended_line = line.replace("\n", "")

            if appended_line.lstrip(";"):
                contents.append(Term(term=appended_line, unchecked=line[0] == ';'))

        contents.sort(key=lambda x: x.term)
        return contents

    """
    Sorts all contents
    """

    # TODO - SOrt this
    def sort_contents(self):
        self.contents = list(set(self.contents)).sort

    """
    Write the contents to the file
    """

    # TODO - SOrt this
    def write_contents(self):
        self.sort_contents()
        filee = open(self.address, "w")
        for line in self.contents:
            filee.write("".join([";", line, "\n"]))

    """
    Prints the contents of the all indexes
    """

    # TODO - SOrt this
    def post(self):
        line = []
        for term in self.contents:

            line.append(term)
            if len(line) == 4:
                print(" ".join(line))
                line = []

        if line:
            print(" ".join(line))

    def is_in_index(self, term):
        return term.lower() in self.contents


class Term:
    def __init__(self, term, unchecked=False):
        self.term = term
        self.unchecked = unchecked

    def get_term(self):
        return self.term

    def is_unchecked(self):
        return self.unchecked

    def check(self):
        self.unchecked = False

    def uncheck(self):
        self.unchecked = True


if __name__ == '__main__':
    p1 = Scoro(initialized_titles=["First", "Second"])
    p1.post()

# TODO
'''
Allow checking via python commands
    Allow different data formats
Comment Term
Comment Index
Comment Scoro
Hook up tests
Optional Settling


'''
