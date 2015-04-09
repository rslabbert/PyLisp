echo "All tests must print true, otherwise error"

for i in $(find . -name '*.pyl'); do
    res=$(~/.virtualenvs/pylisp/bin/python src/main.py $i)
    echo "$i -> $res"
done
