workon pylisp

for i in $(find . -name '*.pyl'); do
    python src/main.py $i
done
