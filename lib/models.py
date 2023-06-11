from sqlalchemy import ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    founding_year = Column(Integer)

    def __repr__(self):
        return f'<Company {self.name}>'

    @property
    def freebies(self):
        return [freebie for dev in self.devs for freebie in dev.freebies if freebie.company == self]

    @property
    def devs(self):
        return [freebie.dev for freebie in self.freebies]

    def give_freebie(self, dev, item_name, value):
        freebie = Freebie.create_freebie(dev, self, item_name, value)
        return freebie

    @classmethod
    def oldest_company(cls):
        return session.query(cls).order_by(cls.founding_year).first()


class Dev(Base):
    __tablename__ = 'devs'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return f'<Dev {self.name}>'

    @property
    def freebies(self):
        return session.query(Freebie).filter_by(dev=self).all()

    @property
    def companies(self):
        return [freebie.company for freebie in self.freebies]

    def received_one(self, item_name):
        return any(freebie.item_name == item_name for freebie in self.freebies)

    def give_away(self, other_dev, freebie):
        if freebie.dev == self:
            freebie.dev = other_dev


class Freebie(Base):
    __tablename__ = 'freebies'

    id = Column(Integer, primary_key=True)
    item_name = Column(String)
    value = Column(Integer)
    dev_id = Column(Integer, ForeignKey('devs.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    dev = relationship("Dev", backref=backref("freebies", cascade="all, delete-orphan"))
    company = relationship("Company", backref=backref("freebies", cascade="all, delete-orphan"))

    def print_details(self):
        return f"{self.dev.name} owns a {self.item_name} from {self.company.name}"

    @classmethod
    def create_freebie(cls, dev, company, item_name, value):
        freebie = cls(dev=dev, company=company, item_name=item_name, value=value)
        return freebie