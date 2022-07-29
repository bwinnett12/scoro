import scoro

def main():
    p1 = scoro.Scoro()
    p1.add_index("fifth", order=5)
    # p1.refresh_indexes_list()
    p1.pull()
    print(p1.pull())

if __name__ == '__main__':
    main()
    