"""
Indexer - Creates the system itself for logging all files.
"""
import glob
import os
from pathlib import Path


class Scoro:
    """
    Scoro is a system for tracking of text based indexes. Each index is a text file that contains multiple entries
    storing details about the file name.
    Each index entry is marked with ';' that can be removed manually or through command.
    Each unchecked entry can be pulled to a remote location.
    """
    def __init__(self, storage="./storage/", location="./indexes/", initialized_titles=None, reset=True):
        self.indexes = []

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

        if initialized_titles:
            self.add_index(initialized_titles)

        if reset:
            self.refresh_indexes_list()
            self.settle()
        else:
            self.renew()

    def settle(self):
        """
        Method for writing all contents to their folder.
        If scoro was deliberately called with settle=False, this method should be called before the last line of your program
        """
        for ind in self.indexes:
            ind.write_contents()

    def add_index(self, title, order=-1):
        '''
        Adds an index and creates a file to be filled with contents
        :param str or list[str] title: The title of the new index
        :param int order: [Optional] specifies what rank to assign to the Index. Unspecified will use the first possible
        '''
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

        # self.refresh_indexes_list()

    def delete_index(self, title):
        """
        Deletes the index. This can also be done manually.

        :param str or list(str) title: The Title of the index you wish to delete
        """
        if not title:
            print("While attempting to delete Index: title left blank")
            return False

        if type(title) == str:
            title = title.split("_")[0]
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

    def get_indexes_list(self):
        """
        Returns a list of all indexes

        :rtype: list[indexes]
        """
        return self.indexes

    def get_indexes_names(self):
        """
        Returns a list of the names of each index

        :rtype: list[str]
        """
        return [obj.title.split("_")[0] for obj in self.get_indexes_list()]

    def get_open_order(self):
        """
        Returns first available open order

        :rtype: int
        """
        taken_orders = []
        for ind in self.get_indexes_list():
            taken_orders.append(ind.get_order())

        taken_orders.sort()
        for i in range(1, len(taken_orders)):
            if i not in taken_orders:
                return i
        else:
            return len(taken_orders) + 1

    def refresh_indexes_list(self):
        """
        Refreshes the indexes based on what is currently in the storage
        """
        # Renews (again) each index based on what was stored in the text file
        self.renew()

        ## Local storage - Retrieving all files in the local files
        local_files_dict = {int(self.indexes[x].order): [] for x in range(len(self.indexes))}

        for file in glob.glob(self.storage + "*"):
            full_term = Path(file).stem.split("_")

            for index, value in enumerate(full_term):
                if not value:
                    continue
                try:
                    local_files_dict[index + 1].append(value)
                except KeyError:
                    continue

        for ind, key in enumerate(local_files_dict):
            ind_to_add = list(set(local_files_dict[key]))
            for term in ind_to_add:
                self.indexes[ind].add(term, checked=True)

        for ind in self.indexes:
            ind.sort_contents()

    def get_contents(self):
        """
        Retrieves a dictionary with content from each index

        :rtype mapping: dict[str, Term]
        """
        content_to_return = {}
        for ind in self.indexes:
            if ind.title not in content_to_return:
                content_to_return[ind.title] = ind.contents
        return content_to_return

    def get_index_content(self, title):
        """
        Returns the content of an index

        :param str title: The Name of the index you wish to get the content of
        :rtype list[Terms]
        """
        return self.indexes[self.get_indexes_names().index(title)].contents

    def is_index(self, title):
        '''
        Returns a bool of whether the potential new index is already found
        :returns if the index exists
        '''
        for ent in self.indexes:
            if title.lower() == ent.title.lower():
                return True
        return False

    def post(self):
        """
        Prints all contents of all indexes
        """
        print("Each file and its contents")
        # Calls post method of each index
        for i in self.indexes:
            i.post()
            if i != self.indexes[-1]:
                print("")

    def pull(self):
        """
        Retrieves each file that is unmarked

        :returns List of all unchecked files
        """
        terms_to_get = {int(self.indexes[x].order): [] for x in range(len(self.indexes))}

        for indx in self.indexes:
            for trm in indx.contents:
                if not trm.is_checked():
                    terms_to_get[indx.order].append(trm.get_word())

        files_of_interest = []
        for file in glob.glob(self.storage + "*"):
            split_term = Path(file).stem.split("_")

            for i in range(len(split_term)):
                try:
                    if split_term[i] in terms_to_get[i+1]:
                        files_of_interest.append(file)
                except KeyError:
                    pass
        return files_of_interest

    def uncheck(self, terms, index=False):
        """
        Marks each term as unchecked for the purposes of pulling.
        Can specify index or leave open for every index
        :param terms:
        :param index:
        :return:
        """

        if type(terms) is list:
            for trm in terms:
                self.uncheck(trm, index)

        indexes_to_check = []
        if index:
            for indx in self.indexes:
                # TODO
                r = 2



    def reset(self):
        """
        Resets each index so that each term has been marked
        """
        for index in self.get_indexes_list():
            index.clear_contents()

    def renew(self):
        """
        Gathers all terms in each index and registers them to their respective index
        :return:
        """
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

        # After getting each index registered, iterates through each index and then adds each term
        for index in self.indexes:
            index.renew_contents()


class Index:
    """
    Index: The files that are being tracked
    """
    def __init__(self, title, root, order):
        self.title = title
        self.order = order
        self.address = root.rstrip("/") + "/" + self.title + "_" + str(self.order) + ".lst"

        # Creates a new file
        Path(self.address).touch(exist_ok=True)

        # Resets the files then leaves blank
        self.contents = []
        # self.reset_contents()

    def path(self):
        """
        Gets the address of the Index
        """
        return self.address

    def add(self, term, checked=False):
        """
        Adds a term to the index
        """
        self.contents.append(Term(term, checked))

    def get_order(self):
        """
        Returns what number of the order the index is
        """
        return self.order

    def clear_contents(self):
        """
        Deletes everything in the index
        """
        filee = open(self.address, "w")
        self.contents = []

    def reset_contents(self):
        """
        Resets the index so that every term is checked
        """
        for trm in self.contents:
            trm.check()

    def renew_contents(self):
        """
        Sets up Index contents with what is currently stored in that index's text file
        """
        contents = []
        filee = open(self.address, "r")
        for line in filee.readlines():
            appended_line = line.replace("\n", "")

            contents.append(Term(word=appended_line.lstrip(";"), unchecked=line[0] == ';'))

        contents.sort(key=lambda x: x.word)
        self.contents = contents

    def get_contents(self):
        """
        Grabs the contents of an index
        :returns: List(str)
        """
        contents = []
        filee = open(self.address, "r")
        for line in filee.readlines():
            appended_line = line.replace("\n", "")

            if appended_line.lstrip(";"):
                contents.append(Term(word=appended_line, unchecked=line[0] == ';'))

        contents.sort(key=lambda x: x.word)
        return contents

    def sort_contents(self):
        """
        Sorts the content of the index
        """
        def quicksort(R):
            if len(R) < 2:
                return R

            pivot = R[0]
            low = quicksort([i for i in R if i < pivot])
            high = quicksort([i for i in R if i > pivot])
            return low + [pivot] + high

        contents = self.contents
        if len(self.contents) > 0:

            only_terms = [y.get_word() for y in self.contents]
            only_terms = quicksort(only_terms)

            # Removes degenerate terms
            # next_spot = next((x for x in test_list if x.value == value), None)

            unused_term_obj = contents
            contents = []

            for term in only_terms:
                for unused in unused_term_obj:
                    if term == unused.get_word():
                        contents.append(unused)
                        unused_term_obj.remove(unused)
                        break
        self.contents = contents

    def write_contents(self):
        """
        Write the contents to the file
        """
        self.sort_contents()
        filee = open(self.address, "w")
        for line in self.contents:
            line_to_write = ''.join([';' if line.is_checked() else '', line.get_word(), '\n'])
            filee.write(line_to_write)

    # TODO - SOrt this
    def post(self):
        """
        Prints the contents of a single index
        """
        line = []
        for term in self.contents:

            line.append(term.get_word())
            if len(line) == 4:
                print(" ".join(line))
                line = []

        if line:
            print(f"Index {self.title}, number {self.order} in order and contains {len(self.contents)}:")
            print(" ".join(line))

    def is_in_index(self, term):
        """
        Determines if the param term is in index
        :param term:
        :return: boolean if index term is in index
        """
        for trm in self.contents:
            if term == trm.get_word():
                return True

        return False


class Term:
    """
    Term: Tracks each entry stored within the index
    """
    def __init__(self, word, unchecked=False):
        self.word = word
        self.checked = unchecked

    def get_word(self):
        return self.word

    def is_checked(self):
        return self.checked

    def check(self):
        self.checked = False

    def uncheck(self):
        self.checked = True


if __name__ == '__main__':
    p1 = Scoro(initialized_titles=["First", "Second"])
    p1.post()

# TODO
'''
WHY is that not showing up in contents twice>
Allow checking via python commands
    Allow different data formats
Is in index
Comment Term
Comment Index
Comment Scoro
Hook up tests
Optional Settling


'''
