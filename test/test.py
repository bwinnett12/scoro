import unittest
import random

from scoro import Scoro
import os


def clean_storage(testscoro):
    # Removes all in storage folder
    for file in os.scandir(testscoro.scorotto.get_storage_path()):
        os.remove(file.path)


def clean_logs(testscoro):
    for file in os.scandir(testscoro.scorotto.location_logs):
        os.remove(file.path)


class TestScoro(unittest.TestCase):
    scorotto = Scoro(reset=True)
    scorotto.add_log(["type", "fruit", "stars"])

    def setup(self):
        # self.scorotto = Scoro(reset=True)
        clean_storage(self)

    def test_zadd_index(self):

        self.scorotto.delete_log(all=True)

        self.assertTrue([] == self.scorotto.get_logs_names())
        self.assertTrue({} == self.scorotto.get_logs_dict())

        self.scorotto.add_log("stars", 3)

        self.assertTrue(len(self.scorotto.get_logs_names()) == 1)
        self.assertTrue(len(self.scorotto.get_logs_dict()) == 1)
        self.assertFalse(os.stat(self.scorotto.location_logs).st_size == 0)
        self.assertTrue(self.scorotto.is_log("stars"))
        self.assertFalse(self.scorotto.is_log("starzzzz"))
        self.assertTrue(self.scorotto.get_log_by_order(3).title == "stars")

        self.scorotto.add_log(["type", "fruit"])

        self.assertTrue(len(self.scorotto.get_logs_names()) == 3)
        self.assertTrue(len(self.scorotto.get_logs_dict()) == 3)
        self.assertTrue(self.scorotto.is_log("fruit"))
        self.assertTrue(self.scorotto.is_log("type"))
        self.assertTrue(self.scorotto.get_log_by_order(1).title == "type")
        self.assertTrue(self.scorotto.get_log_by_order(2).title == "fruit")

    def test_create_db(self):
        clean_storage(self)

        test_types = ["cake", "pie", "custard", "tarte", "syrup", "parfait"]
        test_fruit = ["apple", "blueberry", "carmel", "huckleberry", "cherry", "salmonberry", "kiwi", "banana"]

        for ttype in test_types:
            type_stem = ttype + "_"

            for tfruit in test_fruit:
                r = random.randint(1, 6)

                if r % 2 == 1:
                    continue

                tscore = int(r / 2)
                path_stem = type_stem + "_".join([tfruit, str(tscore)])

                dessert_path = self.scorotto.get_storage_path() + path_stem + ".txt"

                if not os.path.exists(dessert_path):
                    f = open(dessert_path, "x")
                    f.close()

        self.scorotto.load_logs()

        self.assertTrue(self.scorotto.has_term("cake", "type"))
        self.assertTrue(not self.scorotto.has_term("cakee", "type"))
        self.assertTrue(not self.scorotto.has_term("cake", "stars"))
        self.assertTrue(not self.scorotto.has_term("cake", "starzz"))

    def test_delete(self):
        self.assertTrue(len(self.scorotto.get_logs_names()) == 3)
        self.assertTrue(len(self.scorotto.get_logs_dict()) == 3)
        self.assertFalse(self.scorotto.get_log_by_order(4))

        self.scorotto.add_log("test")

        self.assertTrue(len(self.scorotto.get_logs_names()) == 4)
        self.assertTrue(len(self.scorotto.get_logs_dict()) == 4)
        self.assertTrue(self.scorotto.get_log_by_order(4))
        self.assertTrue(self.scorotto.is_log("test"))
        self.assertFalse(self.scorotto.is_log("notfound"))

        self.scorotto.delete_log(all=True)
        self.assertTrue(len(self.scorotto.get_logs_names()) == 0)
        self.assertTrue(len(self.scorotto.get_logs_dict()) == 0)
        self.assertFalse(self.scorotto.get_log_by_order(4))
        self.assertFalse(self.scorotto.is_log("test"))

    def test_get_contents(self):
        self.scorotto.add_log(["type", "fruit", "stars"])
        self.assertTrue(len(self.scorotto.load_contents_from_file()) == 3)
        self.assertTrue("cake" in self.scorotto.load_contents_from_file()["type"])
        self.assertTrue("apple" in self.scorotto.load_contents_from_file()["fruit"])
        self.assertTrue("1" in self.scorotto.load_contents_from_file()["stars"])

        self.assertFalse("fake" in self.scorotto.load_contents_from_file()["type"])
        self.assertFalse("fake" in self.scorotto.load_contents_from_file()["fruit"])
        self.assertFalse("fake" in self.scorotto.load_contents_from_file()["stars"])

        self.scorotto.delete_log(all=True)
        self.assertTrue({} == self.scorotto.load_contents_from_file())
        self.assertTrue(len(self.scorotto.load_contents_from_file()) == 0)

        with self.assertRaises(KeyError):
            r = "cake" in self.scorotto.load_contents_from_file()["type"]
        with self.assertRaises(KeyError):
            r = "apple" in self.scorotto.load_contents_from_file()["type"]
        with self.assertRaises(KeyError):
            r = "1" in self.scorotto.load_contents_from_file()["type"]


    def test_pull(self):
        self.scorotto.delete_log(all=True)
        self.scorotto.add_log(["type", "fruit", "stars"])

        self.scorotto.uncheck("apple")
        self.scorotto.uncheck(["cake", "3"])

        test_pull = self.scorotto.pull()
        self.assertTrue(len(test_pull) > 0)




if __name__ == '__main__':
    unittest.setup()
    unittest.main()
