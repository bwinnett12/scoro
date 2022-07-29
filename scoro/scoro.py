import glob
import operator
import os
import shutil
from pathlib import Path


class Scoro:
    def __init__(self, storage="./storage/", logs="./logs/", output="./output/",
                 initialized_titles=None, reset=True, close=True):
        """
        Scoro is a system for tracking of text based logs. Each log is a text file that contains multiple entries
        storing details about the file name.
        Each Log entry is marked with ';' that can be removed manually or through command.
        Each unchecked entry can be pulled to a remote location.

        :param storage: [Optional] Location of all stored files used
        :param logs: [Optional] Location of all stored logs
        :param output: [Optional] Location of output files moved upon pull_to
        :param initialized_titles: [Optional] If you want to create any new logs
        :param reset: [Optional] If you want to reset the log contents on startup (Does not delete any files)
        :param close: [Optional] Upon closing of the program, will autoset unless told not to
        """
        self.logs = {}
        self.close = close

        if storage:
            self.storage = storage.rstrip("/") + "/"
        else:
            self.storage = "./storage/"

        if logs:
            self.location = logs.rstrip("/") + "/"
        else:
            self.location = "./logs/"

        if output:
            self.output = output.rstrip("/") + "/"
        else:
            self.output = "./output/"

        Path(self.location).mkdir(parents=True, exist_ok=True)
        Path(self.storage).mkdir(parents=True, exist_ok=True)
        Path(self.output).mkdir(parents=True, exist_ok=True)

        if initialized_titles:
            self.add_log(initialized_titles)

        if reset:
            self.refresh_logs_list()
            self.settle()
        else:
            self.renew()

    def __del__(self):
        if self.close:
            self.settle()

    def settle(self):
        """
        Method for writing all contents to their folder.
        If scoro was deliberately called with settle=False, this method should be called before the last line of your program
        """
        for indx in [*self.logs.values()]:
            indx.write_contents()

    def add_log(self, title, order=-1):
        """
        Adds a log and creates a file to be filled with contents
        :param str or list[str] title: The title of the new log
        :param int order: [Optional] specifies what rank to assign to the Log. Unspecified will use the first possible
        """
        # If not empty...
        if not title:
            return False

        # If the order wasn't manually specified
        if order == -1:
            order = self.get_open_order()

        # If a single record...
        if type(title) == str:
            if title not in self.logs:
                self.logs[title] = Index(title, self.location, order)

        # Else a list of titles to add
        elif type(title) == list:
            for ind in title:
                if ind not in self.logs:
                    self.add_log(ind, order=-1)

        else:
            print("Did not add Index - Make sure the title is a string or list of strings")

    def delete_log(self, title):
        """
        Deletes the log. This can also be done manually.

        :param str or list(str) title: The Title of the log you wish to delete
        """
        if not title:
            print("While attempting to delete log: title left blank")
            return False

        if type(title) == str:
            # title = title.split("_")[0]
            if title in self.logs:
                indx = self.logs[title]
                self.logs.pop(title, None)

                if os.path.exists(indx.path()):
                    os.remove(indx.path())
            else:
                print("While attempting to delete log: log name \"{}\" not found".format(title))
                return False

        if type(title) == list:
            for entry in title:
                self.delete_log(entry)

    def get_logs_dict(self):
        """
        Returns a dictionary of all logs, the titles and the log object

        :rtype: dict
        """
        return self.logs

    def get_logs_names(self):
        """
        Returns a list of the names of each logs

        :rtype: list[str]
        """
        return list(self.logs.keys())

    def get_open_order(self):
        """
        Returns first available open order

        :rtype: int
        """
        taken_orders = []
        for indx in self.logs.values():
            taken_orders.append(indx.get_order())

        taken_orders.sort()
        for i in range(1, len(taken_orders)):
            if i not in taken_orders:
                return i
        else:
            return len(taken_orders) + 1

    def refresh_logs_list(self):
        """
        Refreshes the logs based on what is currently in the storage
        """
        # Renews (again) each log based on what was stored in the text file
        self.renew()

        # Local storage - Retrieving all files in the local files
        local_files_dict = {int(self.logs[x].get_order()): [] for x in self.logs}

        for file in glob.glob(self.storage + "*"):
            full_term = Path(file).stem.split("_")

            for log, value in enumerate(full_term):
                if not value:
                    continue
                try:
                    local_files_dict[log + 1].append(value)
                except KeyError:
                    continue

        for ord, terms in local_files_dict.items():
            self.get_log_by_order(ord).add(terms, checked=True)

        for ind in self.logs.values():
            ind.sort_contents()

    def get_log_by_order(self, order):
        """
        Returns the log for an order
        :param order:
        :return: Log belonging to param order
        """
        for indx in self.logs.values():
            if order == indx.get_order():
                return indx
        return None

    def get_contents(self, log="", checked=False, unchecked=False):
        """
        Retrieves a dictionary with content from each log

        :rtype mapping: dict[str, Term]
        """

        logs_to_get = {}
        if log:
            if not type(log) is list:
                log = [log]

            for logg in log:
                try:
                    logg = self.logs[logg]

                    logs_to_get = {logg.title: logg}
                except KeyError:
                    continue
        else:
            logs_to_get = self.logs

        content_to_return = {}
        for title, indx in logs_to_get.items():
            if title not in content_to_return:
                content_to_return[title] = indx.get_contents(checked=checked, unchecked=unchecked)
        return content_to_return

    def get_log_content(self, title):
        """
        Returns the content of an log

        :param str title: The Name of the index you wish to get the content of
        :rtype list[Terms]
        """
        return self.logs[title].get_contents()

    def is_index(self, title):
        """
        Returns a bool of whether the potential new index is already found
        :returns if the index exists
        """
        return title in self.logs

    def post(self):
        """
        Prints all contents of all indexes
        """
        print("Each file and its contents")
        i = 0

        # Calls post method of each index
        for indx in sorted(self.logs.values(), key=operator.attrgetter('order')):
            indx.post()
            i += 1
            if i != len(self.logs):
                print("")

    def pull(self, match=False, send=False, output=""):
        """
        Retrieves each file that is unmarked
        :param output:
        :param match: If the output needs to fit each marked index
        :returns List of all unchecked files
        """
        terms_to_get = {int(x.get_order()): [] for x in self.logs.values()}

        for indx in self.logs.values():
            for trm in indx.scape_contents():
                if not trm.is_checked():
                    terms_to_get[indx.order].append(trm.get_word())

        files_of_interest = []
        for file in glob.glob(self.storage + "*"):
            split_term = Path(file).stem.split("_")

            # If match, the output will be specific to only what's in the matching
            if match:
                for i in range(len(split_term)):
                    try:
                        if not terms_to_get[i+1]:
                            continue

                        if split_term[i] not in terms_to_get[i+1]:
                            break
                    except KeyError:
                        pass
                else:
                    files_of_interest.append(file)

            # If not match, if the term contains any of the identifiers, then its accepted
            else:
                for i in range(len(split_term)):
                    try:
                        if split_term[i] in terms_to_get[i+1]:
                            files_of_interest.append(file)
                    except KeyError:
                        pass
        if send:
            if not output:
                output = self.output

            for file in files_of_interest:
                new_dest = output.rstrip("/") + "/" + Path(file).name
                shutil.copy(file, new_dest)
        return files_of_interest

    def pull_to(self, output="", match=False):
        if not output:
            output = self.output

        files = self.pull(match)
        for file in files:
            new_dest = output.rstrip("/") + "/" + Path(file).name
            shutil.copy(file, new_dest)

    def uncheck(self, terms, index="", pattern=False):
        """
        Marks each term as unchecked for the purposes of pulling.
        Can specify index or leave open for every index
        :param pattern:
        :param terms: String or list of strings to uncheck in indexes
        :param index: Index to check. Default is all indexes
        """

        if not index:
            index = self.get_logs_names()

        elif type(index) is not list:
            index = [index]

        if type(terms) is not list:
            terms = [terms]

        for indx in index:
            try:
                _indx = self.logs[indx]
                for trm in _indx.scape_contents():
                    if trm in terms:
                        trm.uncheck()

            except KeyError:
                continue

    def check(self, terms, index=""):
        """
        Checks all terms passed in for given index.
        If index is blank, then checks it for all

        :param terms:
        :param index:
        :return:
        """
        if not index:
            index = self.get_logs_names()

        elif type(index) is not list:
            index = [index]

        if type(terms) is not list:
            terms = [terms]

        for indx in index:
            try:
                _indx = self.logs[indx]
                for trm in _indx.scape_contents():
                    if trm in terms:
                        trm.check()

            except KeyError:
                continue

    def create(self, attributes, content, extension="txt"):
        if type(attributes) is not list:
            attributes = [attributes]

        attributes = [str(x) for x in attributes]

        file_stem = "_".join(attributes) if len(attributes) > 1 else ''.join(attributes)
        extension = "." + extension.lstrip(".")
        pathh = self.storage + file_stem

        if os.path.exists(pathh + extension):
            found = False
            i = 2
            pathh = pathh + f"-{i}"
            while found is False:
                r = os.path.exists(pathh + extension)
                if os.path.exists(pathh + extension):
                    i += 1
                else:
                    found = True
        pathh += extension

        file = open(pathh, "w")
        file.write(str(content))

    def clear(self):
        """
        Resets each index so that each term has been marked
        """
        for index in self.logs.values():
            index.clear_contents()

    def reset(self):
        """
        Resets each index to having no terms checked
        """
        for indx in self.logs.values():
            indx.reset_contents()

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

        current_index_addresses = [o.address for o in self.get_logs_dict()]

        for addre in all_index_addresses:
            if addre not in current_index_addresses:
                split_addr = Path(addre).stem.split("_")
                self.add_log(split_addr[0], order=int(split_addr[1]))

        # After getting each index registered, iterates through each index and then adds each term
        for index in self.logs.values():
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
        if not term:
            print("Failed to add term: Term left blank")

        if type(term) == str:
            self.contents.append(Term(term, checked))

        elif type(term) == list:
            for trm in term:
                self.add(trm, checked)

        else:
            print("Term wasn't added. It should be a string or list of strings")

    def get_order(self):
        """
        Returns what number of the order the log is
        """
        return self.order

    def get_contents(self, checked=False, unchecked=False):
        """
        Returns the contents of log
        :param checked: True if you want only checked
        :param unchecked: True if you only want unchecked
        :return: contents of log
        :rtype: list of Term
        """
        checked_bias = True if ((checked or unchecked) and (checked is not unchecked)) else False
        all_terms = []

        if checked_bias:
            bias = True if checked else False

            for trm in self.contents:
                if trm.is_checked() == bias:
                    all_terms.append(trm.get_word())

        else:
            for trm in self.contents:
                all_terms.append(trm.get_word())
        return all_terms

    def clear_contents(self):
        """
        Deletes everything in the log
        """
        filee = open(self.address, "w")
        self.contents = []

    def reset_contents(self):
        """
        Resets the log so that every term is checked
        """
        for trm in self.contents:
            trm.check()

    def renew_contents(self):
        """
        Sets up log contents with what is currently stored in that log's text file
        """
        contents = []
        filee = open(self.address, "r")
        for line in filee.readlines():
            appended_line = line.replace("\n", "")

            contents.append(Term(word=appended_line.lstrip(";"), checked=line[0] == ';'))

        contents.sort(key=lambda x: x.word)
        self.contents = contents

    def scape_contents(self):
        """
        Grabs the contents of a log
        :returns: List(str)
        """
        contents = []
        filee = open(self.address, "r")
        for line in filee.readlines():
            appended_line = line.replace("\n", "")

            if appended_line.lstrip(";"):
                contents.append(Term(word=appended_line, checked=line[0] == ';'))

        contents.sort(key=lambda x: x.word)
        return contents

    def sort_contents(self):
        """
        Sorts the content of the log
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
        Done on settle
        """
        self.sort_contents()
        filee = open(self.address, "w")
        for line in self.contents:
            line_to_write = ''.join([';' if line.is_checked() else '', line.get_word(), '\n'])
            filee.write(line_to_write)

    def post(self):
        """
        Prints the contents of a single log
        """
        line = []
        for term in self.contents:

            line.append(term.get_word())
            if len(line) == 4:
                print(" ".join(line))
                line = []

        if line:
            print(f"Log {self.title}, number {self.order} in order and contains {len(self.contents)}:")
            print(" ".join(line))

    def in_log(self, term):
        """
        Determines if the param term is in log
        :param term: String of term
        :return: boolean if term is in log
        """
        for trm in self.contents:
            if term == trm.get_word():
                return True

        return False


class Term:
    def __init__(self, word, checked=True):
        """
        Term: Tracks each entry stored within the log

        :param word: The string itself describing the vocabulary
        :param checked: If the term is unchecked
        """
        self.word = word
        self.checked = checked

    def get_word(self):
        """
        Returns the word itself
        :return: the word itself
        :rtype : str
        """
        return self.word

    def is_checked(self):
        """
        Returns if the term has been checked or not
        :return: If the term itself is checked
        :rtype: bool
        """
        return self.checked

    def check(self):
        """
        Checks the term. In the log, represented by a prefixed ";"
        """
        self.checked = True

    def uncheck(self):
        """
        Unchecks the term. In the log, represented by no prefixed ";"
        """
        self.checked = False

# 1TODO - Set up duplicates