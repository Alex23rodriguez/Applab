echo executing python scripts...
# cd to this directory
cd $(dirname $0)
python api.py && python join_table.py
