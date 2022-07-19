import scoro

def main():
    p1 = scoro.Scoro()
    p1.add_index(["first", "secon", "theird"])
    p1.refresh_indexes_list()
    p1.post()

if __name__ == '__main__':
    main()
    