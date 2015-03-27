for i in $(find . -name '*.pyl'); do
    ~/.virtualenvs/pylisp/bin/python src/main.py $i
done
