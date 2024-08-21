import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

Base = declarative_base()


class Publisher(Base):
    __tablename__ = 'publisher'
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=255), nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return f'{self.id}: {self.name}'


class Shop(Base):
    __tablename__ = 'shop'
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=255), nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return f'{self.id}: {self.name}'


class Book(Base):
    __tablename__ = 'book'
    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String(length=255), nullable=False)
    id_publisher = sq.Column(sq.Integer, sq.ForeignKey('publisher.id'), nullable=False)

    def __init__(self, id, title, id_publisher):
        self.id = id
        self.title = title
        self.id_publisher = id_publisher

    def __str__(self):
        return f'{self.id}: {self.title}'


class Stock(Base):
    __tablename__ = 'stock'
    id = sq.Column(sq.Integer, primary_key=True)
    id_book = sq.Column(sq.Integer, sq.ForeignKey('book.id'), nullable=False)
    id_shop = sq.Column(sq.Integer, sq.ForeignKey('shop.id'), nullable=False)
    count = sq.Column(sq.Integer, nullable=False)

    def __init__(self, id, id_book, id_shop, count):
        self.id = id
        self.id_book = id_book
        self.id_shop = id_shop
        self.count = count

    def __str__(self):
        return f'{self.id}: {self.count}'


class Sale(Base):
    __tablename__ = 'sale'
    id = sq.Column(sq.Integer, primary_key=True)
    price = sq.Column(sq.Integer, nullable=False)
    date_sale = sq.Column(sq.DateTime, nullable=False)
    id_stock = sq.Column(sq.Integer, sq.ForeignKey('stock.id'), nullable=False)
    count = sq.Column(sq.Integer, nullable=False)
    stock = relationship('Stock')

    def __init__(self, id, price, date_sale, id_stock, count):
        self.id = id
        self.price = price
        self.date_sale = date_sale
        self.id_stock = id_stock
        self.count = count

    def __str__(self):
        return f'{self.id}: {self.price}'


def get_shops(session, publisher_info):
    qr = session.query(
        Book.title,
        Shop.name,
        Sale.price,
        Sale.date_sale
    ).join(Stock, Stock.id_book == Book.id)\
    .join(Shop, Shop.id == Stock.id_shop)\
    .join(Sale, Stock.id == Sale.id_stock)\
    .join(Publisher, Publisher.id == Book.id_publisher)\

    if publisher_info.isdigit():
        result = qr.filter(Publisher.id == int(publisher_info)).all()
    else:
        result = qr.filter(Publisher.name == publisher_info).all()
    for title, shop_name, price, date in result:
        print(f'{title: <40} | {shop_name: <10} | {price: <8} | {date.strftime('%d-%m-%Y')}')


def main():
    engine = sq.create_engine('postgresql://postgres:root@localhost:5432/netology_db')
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    publisher1 = Publisher(1, 'Бродский')
    publisher2 = Publisher(2, 'Пушкин')
    publisher3 = Publisher(3, 'Платонов')
    session.add(publisher1)
    session.add(publisher2)
    session.add(publisher3)
    session.commit()

    shop1 = Shop(1, 'Буквоед')
    shop2 = Shop(2, 'Лабиринт')
    shop3 = Shop(3, 'Книжный дом')
    session.add(shop1)
    session.add(shop2)
    session.add(shop3)
    session.commit()

    book1 = Book(1, 'Капитанская дочка', 1)
    book2 = Book(2, 'Руслан и Людмила', 2)
    book3 = Book(3, 'Евгений Онегин', 3)
    session.add(book1)
    session.add(book2)
    session.add(book3)
    session.commit()

    stock1 = Stock(1, 1, 1, 1)
    stock2 = Stock(2, 2, 2, 6)
    stock3 = Stock(3, 3, 3, 4)
    stock4 = Stock(4, 3, 3, 2)
    session.add(stock1)
    session.add(stock2)
    session.add(stock3)
    session.add(stock4)
    session.commit()

    sale1 = Sale(1, 300, '21.06.2020', 1, 1)
    sale2 = Sale(2, 500, '22.06.2021', 2, 1)
    sale3 = Sale(3, 700, '18.05.2022', 3, 1)
    sale4 = Sale(4, 200, '11.03.2015', 4, 1)
    session.add(sale1)
    session.add(sale2)
    session.add(sale3)
    session.add(sale4)
    session.commit()

    publisher_info = input('Введите имя или идентификатор издателя:')
    get_shops(session, publisher_info)

    session.close()

if __name__ == '__main__':
    main()
