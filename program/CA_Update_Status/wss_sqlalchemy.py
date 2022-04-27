from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.orm import defer, undefer
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy import (Column, Integer, Numeric, String, DateTime, ForeignKey)
import urllib
import yaml

with open(r'config/config.yaml', encoding='utf8') as f:
    config = yaml.safe_load(f)

# ----- Way 1 -------
# params = urllib.parse.quote_plus("DRIVER={SQL Server Native Client 11.0};"
#                                  "SERVER=;"
#                                  "DATABASE=;"
#                                  "Trusted_Connection=yes;"
#                                  )
# engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))
# ----- END Way 1 -------


# ------- Way 2 --------
servername =  config['work_db']['server']
db_name = config['work_db']['db_prime']
auth = ''  # '<username>:<password>@'
port = ''
option = '?DRIVER={SQL Server Native Client 11.0}&Trusted_Connection=yes’'

engine = create_engine(f'mssql+pyodbc://{auth}{servername}/{db_name}{option}')
# ------- END Way 2 --------

# sqlalchemy CORE connection
# connection = engine.connect()
# print(engine.table_names())

# sqlalchemy ORM connection
Session = sessionmaker(bind=engine)
session = Session()

# Declaration of metadata and base class
metadata = MetaData()
Base = declarative_base()

# Declaration Class of table (with autoload)
# table = Table('CA_AIS_K_06_20', metadata, autoload=True, autoload_with=engine)
# This Work
# table = Table('_list_dms__ContractsAIS_869_from_report', metadata, autoload=True, autoload_with=engine)

# -------------------------------start---------------------------------
# This block Create class for table ant execute query for it (Work)
# class Contracts(Base):
#     __tablename__ = '_list_dms__ContractsAIS_869_from_report'

#     id = Column('ContractsID', Integer, primary_key=True)
#     con_num = Column('ContractNumber', String(50))

#     def __repr__(self):
#         return 'Contracts:(id={self.id}, ' \
#                 'con_num = {self.con_num})'.format(self=self)

# for row in session.query(Contracts).filter(Contracts.id == 78383).all():
#     print(row)
# -------------------------------end---------------------------------


# ----------------------------------------------------------------
# Automating Column Naming Schemes from Reflected Tables
# # ! Don't work
# class Contracts(Base):
#     __table__ = Table("_list_dms__ContractsAIS_869_from_report", Base.metadata,
#                 autoload_with=engine)

#     def __repr__(self):
#         return 'Contracts:(id={self.id}, ' \
#                 'con_num = {self.con_num})'.format(self=self)

# for row in session.query(Contracts).filter(Contracts.attr_ContractsID == 78383).all():
#     print(row)
# ----------------------------------------------------------------


# ----------------------------------------------------------------
# Init class for tables
class ContrAgents(Base):
    __tablename__ = 'list_dms__Contragents_88'

    id = Column('id', Integer, primary_key=True)
    inn = Column('ИНН', String(20))
    status = Column('Статус ЕГРЮЛ', String)

class Contracts(Base):
    __tablename__ = 'list_dms_contracts__Contracts_120'

    id = Column('ID', Integer(), primary_key=True)
    reg_num = Column('Регистрационный номер', String(50))
    status = Column('Статус', Integer)
    contragents_id = Column('Контрагент',
                            Integer(),
                            ForeignKey('list_dms__Contragents_88.id'))

    contragents = relationship('ContrAgents',
                               backref=backref(
                                   'list_dms_contracts__Contracts_120',
                                   order_by=id)
                               )

    def __repr__(self):
        return 'Contracts:(id={self.id}, ' \
                'reg_num = {self.reg_num}), '\
                'ca = {self.contragents_id}'.format(self=self)


query = session.query(Contracts.contragents_id, ContrAgents.status)
query = query.join(ContrAgents)
result_sql = query.filter(Contracts.status == 17).all()
# print(f'{type(result)}: {result}')
# result = [r.contragents_id for r in result_sql]
print(result_sql)

# ----------------------------------------------------------------

# CORE query
# query = select([table])
# ResultProxy = connection.execute(query)
# ResultSet = ResultProxy.first()
# print(ResultSet)

# ORM query
# result_set = session.query(table).all() #! This Work don't touch it
# # Show Columns
# print(result_set.keys())

# ORM query TEST
# query = session.query(table)
# # query = query.options(defer('*'), undefer("summary"))
# query.first()
# print(query.keys())

# print(session.query(table.ИНН,).first())