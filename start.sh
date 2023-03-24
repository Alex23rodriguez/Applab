echo "starting pipeline..."
/usr/local/bin/python /usr/src/app/python/api.py && /usr/local/bin/python /usr/src/app/python/join_tables.py
echo "done!"
