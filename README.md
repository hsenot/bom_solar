bom_solar
=========

Processing of BOM solar data files


Setup
-----

git clone git@github.com:hsenot/bom_solar.git

cd bom_solar

mkvirtualenv bom_solar

pip install psycopg2


Use
---
* Load BOM solar data as vector

Adjust DB connection details in txt2pg.py
python txt2pg.py -d <source_directory_of_raster_files> -x <lon> -y <lat>

* Load BOM solar data as raster

1 raster at a time (1 file = 1 record):
raster2pgsql -I -C -s 4283 <raster_file> | sudo -u postgres psql -d <database_name>







