import copy
import glob
import operator
import os
import shutil
from enum import Enum
from pathlib import Path


class Scoro:
    def __init__(self, storage="./storage/", logs="./logs/", output="./output/",
                 initialized_titles=None, reset=False, close=True, send=False):
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
        :param send: [Optional] Upon pull, send all files to the 'output' folder
        """
        self.logs = {}
        self.close = close
        self.send = send

        if storage:
            self.location_storage = storage.rstrip("/") + "/"
        else:
            self.location_storage = "./storage/"

        if logs:
            self.location_logs = logs.rstrip("/") + "/"
        else:
            self.location_logs = "./logs/"

        if output:
            self.location_output = output.rstrip("/") + "/"
        else:
            self.location_output = "./output/"

        Path(self.location_logs).mkdir(parents=True, exist_ok=True)
        Path(self.location_storage).mkdir(parents=True, exist_ok=True)
        Path(self.location_output).mkdir(parents=True, exist_ok=True)

        # Creates logs for any titles you want
        if initialized_titles:
            self.add_log(initialized_titles)

        # Sets up logs by default, also resets storage upon reset
        self.renew(storage=reset, logs=True)
        if reset:
            self.reset()

    # Settles contents to each log upon close
    def __del__(self):
        if self.close:
            self.settle()

    def get_storage_path(self) -> str:
        """
        Returns path of folder for storage

        :return: Path of folder for storage
        """
        return self.location_storage

    def get_logs_path(self) -> str:
        """
        Returns path of folder for logs

        :return: Path of folder for logs
        """
        return self.location_logs

    def get_output_path(self) -> str:
        """
        Returns path of folder for outputted / pulled files

        :return: Path of folder for outputted / pulled files
        """
        return self.location_output

    def settle(self):
        """
        Method for writing all contents to their folder.
        If src was deliberately called with settle=False, this method should be called before the last line of your program
        """
        for indx in [*self.logs.values()]:
            indx.write_contents()

    def add_log(self, title, order=-1, generate=True):
        """
        Adds a log and creates a file to be filled with contents
        :param boolean generate: If you want to generate contents
        :param str or list[str] title: The title of the new log
        :param int order: [Optional] specifies what rank to assign to the Log. Unspecified will use the first possible
        :param boolean generate: [Optional] Generates the log from storage content
        """
        # If not empty...
        if not title:
            return False

        if type(title) == str:
            title = [title]

        if type(order) == int:
            order = [order]

        # Fill in gaps with negative -1
        order = order + [-1] * ((len(title) - len(order)) * (len(title) - len(order) > 0))

        # For each in list of titles
        for i in range(len(title)):
            if title[i] not in self.logs.keys():
                # If the order wasn't manually specified
                if order[i] == -1:
                    order[i] = self.get_open_order()

                # Creates the log then adds
                log_to_add = Log(title[i], self.location_logs, order[i])
                self.logs[title[i]] = log_to_add

                # Refresh this log only
                if generate:
                    self.renew(storage=False, logs=False, log_by_name=title)

    def delete_log(self, title="", all=False):
        """
        Deletes the log. This can also be done manually.

        :param all: Deletes all logs
        :param str or list(str) title: The Title of the log you wish to delete
        """
        if not title and not all:
            print("Please specify a log or add \"all=True\" to parameters to delete all logs")
            return False

        # Deletes all logs found
        if all:
            title = self.get_logs_names()

        if type(title) != list:
            title = [title]

        # For each in list of titles to delete
        for ttitl in title:
            if ttitl in self.logs.keys():
                os.remove(self.logs[ttitl].address)
                del self.logs[ttitl]

            else:
                print("While attempting to delete log: log name \"{}\" not found".format(title))
                return False

    def get_logs_dict(self) -> dict:
        """
        Returns a dictionary of all logs, the titles and the log object

        :return: Dictionary containing each log
        :rtype: dict
        """
        return self.logs

    def get_logs_names(self):
        """
        Returns a list of the names of each logs

        :return: list of names
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

        if len(taken_orders) == 0 or 1 not in taken_orders:
            return 1

        taken_orders.sort()
        for i in range(1, len(taken_orders) + 1):
            if i not in taken_orders:
                return i
        else:
            return len(taken_orders) + 1

    def renew(self, storage=True, logs=False, log_by_name=""):
        """
        Load or reloads logs from files and opens logs
        :param log_by_name: A specific log that you want to renew
        :param logs: Log(s) to fill
        :param storage: Fill log(s) or all logs with storage contents
        """

        def load_logs(self, generate=True):
            """
            Refreshes the logs based on what is currently in the storage
            """
            # Renews (again) each log based on what was stored in the text file
            # First section registers all logs found locally
            all_log_addresses = []
            all_abridged_addresses = []
            current_log_addresses = [o.address for o in self.get_logs_dict().values()]

            # Get all logs currently in the file
            for file in glob.glob(self.location_logs + "*.lst"):
                abridged = Path(file).stem.split("_")[0]
                if abridged not in all_abridged_addresses:
                    all_abridged_addresses.append(abridged)
                    all_log_addresses.append(file)

            # If there isn't an address associated with any log, then make a new one
            for addre in all_log_addresses:
                if addre not in current_log_addresses:
                    split_addr = Path(addre).stem.split("_")
                    self.add_log(split_addr[0], order=int(split_addr[1]), generate=generate)

        def fill_logs(self, logs=""):
            """
            Loads the storage onto the log
            Rewrites the contents
            :param self: The Scoro object
            :param logs: str or list[str]
            """
            # Local storage - Retrieving all files in the local files
            # Loads only a logs
            if not logs:
                local_files_dict = {int(self.logs[x].get_order()): {} for x in self.logs}
            else:
                local_files_dict = {}
                if type(logs) != list:
                    logs = [logs]

                # Gets the orders from each log
                log_orders = []
                for log in logs:
                    if log in self.logs:
                        log_orders.append(self.logs[log].get_order())
                local_files_dict = {int(x): {} for x in log_orders}

            # Accumulation of all files for storage
            for file in glob.glob(self.location_storage + "*"):

                stripped_files = Path(file).stem.split("__", 1)[0]
                full_term = stripped_files.split("_")

                # Adds each occurrence of a term to a dictionary
                for log_num, value in enumerate(full_term):
                    if not value:
                        continue
                    if log_num + 1 in local_files_dict:
                        local_files_dict[log_num + 1][value] = Term.checked

            # Gets all contents of currently in logs
            log_dict = {}
            dict_of_all_log_contents = {}
            for log in self.logs.values():
                log_dict[log.get_order()] = log.grab_contents()

            for orde, grabbed_contents in local_files_dict.items():
                dict_of_all_log_contents[orde] = {}
                for term in grabbed_contents.keys():

                    if orde in log_dict and term in log_dict[orde]:
                        dict_of_all_log_contents[orde][term] = log_dict[orde][term]
                    else:
                        dict_of_all_log_contents[orde][term] = Term.checked

            # Add terms to order
            for orde, sub_log_dict in dict_of_all_log_contents.items():

                unchecked_items = list(set([k for k, v in sub_log_dict.items() if v == Term.unchecked]))
                checked_items = list(set([k for k, v in sub_log_dict.items() if v == Term.checked]))

                log_to_add = self.get_log_by_order(orde)
                if checked_items:
                    log_to_add.add(checked_items, checked=True)
                if unchecked_items:
                    log_to_add.add(unchecked_items, checked=False)

            if self.close:
                self.settle()

        if logs:
            load_logs(self, not storage)
        if storage or log_by_name:
            fill_logs(self, log_by_name)

    def get_log_by_order(self, order):
        """
        Returns the log for an order
        :param order:
        :return: Log belonging to param order
        :rtype: Log
        """
        for indx in self.logs.values():
            if order == indx.get_order():
                return indx
        return None

    def get_log_content(self, title) -> dict:
        """
        Returns the content of an log
        If the log doesn't exist, returns an empty dictionary

        :param str title: The Name of the log you wish to get the content of
        :rtype dict
        """
        if title in self.logs:
            return self.logs[title].get_contents()
        else:
            return {}

    def is_log(self, title) -> bool:
        """
        Returns a bool of whether the potential new log is already found
        :return: if the log exists
        """
        return title in self.logs.keys()

    def post(self):
        """
        Prints all contents of all logs
        """
        # Calls post method of each log
        for indx in sorted(self.logs.values(), key=operator.attrgetter('order')):
            indx.post()

    def pull(self, match=False, send=False, output=""):
        """
        Retrieves each file that is unmarked
        :param send: Sends all files to output
        :param output: path of folder for pulling to. Default is in folder
        :param match: If the output needs to fit each marked log
        :returns List of all unchecked files
        """
        terms_to_get = {int(x.get_order()): [] for x in self.logs.values()}

        # Fills dictionary by order: [terms to get]
        for indx in self.logs.values():
            for term, czeched in indx.get_contents().items():
                if czeched == Term.unchecked:
                    terms_to_get[indx.order].append(term)

        # Goes through each file in storage
        files_of_interest = []
        for file in glob.glob(self.location_storage + "*"):
            split_term = Path(file).stem.split("_")

            # If matched, the output will be specific to only what's in the matching
            if match:
                for i in range(len(split_term)):
                    try:
                        if not terms_to_get[i + 1]:
                            continue

                        # Every term is specific in match
                        if split_term[i] not in terms_to_get[i + 1]:
                            break
                    except KeyError:
                        pass
                else:
                    files_of_interest.append(file)

            # If not match, if the term contains any of the identifiers, then its accepted
            else:
                for i in range(len(split_term)):
                    try:
                        if split_term[i] in terms_to_get[i + 1]:
                            files_of_interest.append(file)
                    except KeyError:
                        pass

        # Outputs to folder
        if send or self.send:
            if not output:
                output = self.location_output

            for file in files_of_interest:
                new_dest = output.rstrip("/") + "/" + Path(file).name
                shutil.copy(file, new_dest)
        return files_of_interest

    def has_term(self, term, log=""):
        """
        Returns if term is found in any or all indexes.
        Accepts string or list of strings
        :param term: The term to find
        :param log: The log(s) to go through
        :return: bool
        """

        logs_to_check = {}
        if log:
            if type(log) == str:

                for log_find in self.get_logs_dict().items():
                    if log_find[0] == log:
                        logs_to_check = {log_find[0]: log_find[1]}
                        break
                else:
                    print(f"Log not found: {log}")

            elif type(log) == list:
                for ent in log:
                    for log_find in self.get_logs_dict().items():
                        if log_find[0] == ent:
                            logs_to_check = {log_find[0]: log_find[1]}
                            break
                    else:
                        print(f"Log not found: {ent}")
        else:
            logs_to_check = self.logs

        for elog in logs_to_check.values():
            if term in elog.get_contents():
                return True
        else:
            return False

    def uncheck(self, terms, log="", pattern=False):
        """
        Marks each term as unchecked for the purposes of pulling.
        Can specify logs or leave open for every log
        :param pattern: NOT IMPLEMENTED
        :param terms: String or list of strings to uncheck in Logs
        :param log: Log to check. Default is all Logs
        """

        if not log:
            log = self.get_logs_names()

        elif type(log) is not list:
            log = [log]

        if type(terms) is not list:
            terms = [terms]

        for indx in log:
            if indx in self.logs:
                _indx = self.logs[indx]
                _indx.uncheck(terms)

            else:
                continue

    def check(self, terms, log=""):
        """
        Checks all terms passed in for given log.
        If log is blank, then checks it for all

        :param terms: Term or terms that you want to look for
        :param log: If you want to specify a log
        :return:
        """
        if not log:
            log = self.get_logs_names()

        elif type(log) is not list:
            log = [log]

        if type(terms) is not list:
            terms = [terms]

        for indx in log:
            if indx in self.logs:
                _indx = self.logs[indx]
                _indx.check(terms)
            else:
                continue

    def create(self, attributes, content, extension=""):
        """
        Creates a file with attributes as a title, content for content, and an extension

        :param list attributes: A list of details to give to the file
        :param content: The content that you wish to write as the body of the file
        :param extension: Default txt. The extension of the file
        :return:
        """
        if type(attributes) is not list:
            attributes = [attributes]

        attributes = [str(x) for x in attributes]
        if not extension:
            extension = ".txt"
        else:
            extension = "." + extension.lstrip(".")

        found = False
        pathh = ""
        i = 0
        while not found:
            file_stem = "_".join(attributes) if len(attributes) > 1 else ''.join(attributes)
            if i > 0:
                file_stem += f"__{i}"

            pathh = self.location_storage + file_stem + extension
            if not os.path.exists(pathh):
                found = True

            else:
                if i == 0:
                    i = 2
                else:
                    i += 1

        file = open(pathh, "w")
        file.write(str(content))

        logs_by_order = [x for x in self.logs.values()]
        logs_by_order.sort(key=lambda f: f.order)

        # Adds each attribute to their logs
        for i in range(len(logs_by_order)):
            if i > len(attributes) - 1:
                break
            logs_by_order[i].add(attributes[i])

    def clear(self):
        """
        Deletes the content of each log
        """
        for log in self.logs.values():
            log.clear_contents()

    def reset(self):
        """
        Resets each log to having no terms unchecked
        """
        for indx in self.logs.values():
            indx.check_all_contents()


class Log:
    """
    Log: The files that are being tracked
    :param title: Title of the log
    :param root: The folder containing the log
    :param order: The order that is tracked from the attributes
    """

    def __init__(self, title, root, order):
        self.title = title
        self.order = order
        self.address = root.rstrip("/") + "/" + self.title + "_" + str(self.order) + ".lst"

        # Creates a new file
        Path(self.address).touch(exist_ok=True)

        # Initializes contents
        self.contents = {}

    def path(self) -> str:
        """
        Gets the address of the Log
        """
        return self.address

    def get_contents(self) -> dict:
        return self.contents

    def add(self, terms, checked=True):
        """
        Adds a term to the log
        """
        if not terms:
            print("Failed to add term: Term left blank")

        if type(terms) != list:
            terms = [terms]

        for _trm in terms:
            _trm = str(_trm)
            if _trm not in self.contents.keys():
                self.contents[_trm] = Term.checked if checked else Term.unchecked

    def get_order(self) -> int:
        """
        Returns what number of the order the log is
        """
        return self.order

    def get_to_pull(self, checked=False, unchecked=False) -> list:
        """
        Returns the contents of log
        :param checked: True if you want only checked
        :param unchecked: True if you only want unchecked
        :return: contents of log
        :rtype: list of Term
        """
        all_terms = []
        checked_bias = True if ((checked or unchecked) and (checked is not unchecked)) else False

        if checked_bias:
            bias = Term.checked if checked else Term.unchecked

            for term, czeched in self.contents.items():
                if czeched == bias:
                    all_terms.append(term)

        else:
            for trm in self.contents:
                all_terms.append(trm.get_word())
        return all_terms

    def clear_contents(self):
        """
        Deletes everything in the log
        """
        filee = open(self.address, "w")
        self.contents = {}

    def check_all_contents(self):
        """
        Resets the log so that every term is checked
        """
        contents_copy = copy.deepcopy(self.contents)
        for key, value in contents_copy.items():
            self.contents[key] = Term.checked

    def grab_contents(self):
        """
        Grabs the contents of a log from the file
        """
        contents = {}
        filee = open(self.address, "r")
        r = filee.readlines()
        for line in r:
            appended_line = line.replace("\n", "")

            if appended_line:
                contents[appended_line.lstrip(";")] = Term.checked if appended_line[0] == ';' else Term.unchecked

        filee.close()
        # self.contents = contents
        return contents

    def write_contents(self):
        """
        Write the contents to the file
        Done on settle
        """
        filee = open(self.address, "w")
        sorted_contents = []

        # Creates a tuple for each term (term, checked)
        for term, czeched in self.contents.items():
            sorted_contents.append((term, czeched))
        sorted_contents.sort()

        # Writes each term to the contents
        for trm in sorted_contents:
            line_to_write = ''.join([';' if trm[1] == Term.checked else '', trm[0], '\n'])
            filee.write(line_to_write)

    def post(self):
        """
        Prints the contents of a single log
        """
        line = []
        lines = []
        contents = sorted(list(self.contents.items()))
        for term in contents:
            term_to_post = "".join(["" if term[1] is Term.unchecked else ";", term[0]])
            line.append(term_to_post)
            if len(line) == 4:
                lines.append(" ".join(line))
                line = []

        if line:
            lines.append(" ".join(line))

        if lines:
            print(f"Log: {self.title}")
            print(f"Number: {self.order}")
            print(f"Contains {len(self.contents)} elements:")
            print("\n".join(lines))
            print(" ")

    def in_log(self, term):
        """
        Determines if the param term is in log
        :param term: String of term
        :return: boolean if term is in log
        """
        return term in self.contents

    def check(self, terms):
        """
        Checks a term or terms
        :param terms: The term or list of terms you wish to check
        """
        if type(terms) is not list:
            terms = [terms]

        for _entr in terms:
            if _entr in self.contents:
                self.contents[_entr] = Term.checked

    def uncheck(self, terms):
        """
        Unchecks a term or terms
        :param terms: The term or list of terms you wish to uncheck
        """
        if type(terms) is not list:
            terms = [terms]

        for _entr in terms:
            if _entr in self.contents:
                self.contents[_entr] = Term.unchecked

    def is_checked(self, term):
        """
        Returns if the term is checked or not
        :param term: The term to check if it is checked
        :return: boolean if in log
        """
        if term in self.contents:
            return self.contents[term] == Term.checked
        return False


class Term(Enum):
    checked = 1
    unchecked = 2
