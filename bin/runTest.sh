echo "All tests must print true, otherwise error"

for i in $(find tests -name '*.pyl'); do
    res=$(/usr/local/bin/python3 src/main.py $i)
    echo "$i -> $res"
done
