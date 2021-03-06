import csv
import isbnlib

def get(list, index):
    return list[index] if len(list) > index else None

def join_authors(book):
    authors = book['author_1']

    author_2 = book['author_2']
    author_3 = book['author_3']

    if author_2:
        authors = '{}, {}'.format(authors, author_2)

    if author_3:
        authors = '{}, {}'.format(authors, author_3)

    return authors



class CsvHandler:
    def __init__(self, filename='library-pi.csv'):
        self.fieldnames = ['isbn', 'title', 'publisher', 'year', 'author_1', 'author_2', 'author_3']
        self.filename = filename
        self.isbns = set()
        self.book_data = {}
        self.new_books = {}
        self.get_cache_from_csv()
        self.qr_codes = {}

    def get_cache_from_csv(self):
        try:
            with open(self.filename) as csv_file:
                print('[INFO] Reading File - {}'.format(self.filename))
                reader = csv.DictReader(csv_file)

                for row in reader:
                    isbn = row['isbn']
                    self.isbns.add(isbn)
                    self.book_data[isbn] = row

        except Exception as e:
            print('[INFO] Creating File - {}'.format(self.filename))
            with open(self.filename, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
                writer.writeheader()

    def add_book(self, isbn, qr_code, add_book_to_db):
        new_book = False
        original_isbn = isbn

        if isbn not in self.isbns:
            new_book = True
            try:
                book = isbnlib.meta(isbn)
                self.isbns.add(original_isbn)
            except Exception as e:
                # this catches errors that originate from isbnlib
                return None

            if qr_code:
                self.qr_codes[isbn] = book['ISBN-13']
                isbn = book['ISBN-13']
                if isbn in self.isbns:
                    new_book = False
                else:
                    self.isbns.add(isbn)

            book = {
                'isbn': isbn,
                'title': book['Title'],
                'author_1': get(book['Authors'], 0),
                'author_2': get(book['Authors'], 1),
                'author_3': get(book['Authors'], 2),
                'publisher': book['Publisher'],
                'year': book['Year']
            }

        if new_book:
            add_book_to_db(book)
            self.book_data[isbn] = book
            self.new_books[isbn] = book

        return {
            'display_name': self.get_display_data(original_isbn, qr_code),
            **self.get_book_data(original_isbn, qr_code)
        }

    def get_display_data(self, isbn, qr_code=False):
        if qr_code:
            isbn = self.qr_codes[isbn]

        book = self.book_data.get(isbn)

        if book is None or book.get('title') is None:
            return isbn

        return '{} - {}'.format(book['title'], join_authors(book))

    def get_book_data(self, isbn, qr_code):
        if qr_code:
            isbn = self.qr_codes[isbn]

        book = self.book_data.get(isbn)

        if book is None or book.get('title') is None:
            return None

        return {**book, 'authors': join_authors(book)}

    def write_new_to_csv(self):
        with open(self.filename, 'a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)

            for isbn, meta in self.new_books.items():
                writer.writerow(meta)
