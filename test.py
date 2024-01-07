from sqlalchemy.dialects import mysql
from sqlalchemy.sql.ddl import CreateTable

from models import *

print(CreateTable(DeviceModel.__table__).compile(dialect=mysql.dialect()))
print(CreateTable(GardenModel.__table__).compile(dialect=mysql.dialect()))
print(CreateTable(DeviceTypeModel.__table__).compile(dialect=mysql.dialect()))
print(CreateTable(MeasureDataModel.__table__).compile(dialect=mysql.dialect()))
