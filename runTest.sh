echo "All tests must print true, otherwise error"

for i in $(find . -name '*.pyl'); do
    echo $i
    ~/.virtualenvs/pylisp/bin/python src/main.py $i
done
