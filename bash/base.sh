#!/bin/bash

echo "Name: "
read name
read -p "dir: " dir

word="Hello"
echo "$word, $name!"

if [ $name == "Alex" ] && [ 1 == 1 ]; then
  echo "Hi, Alex"
else
  echo "Who are you?"
fi

for i in {1..5}; do
  echo $i
done

i=0
while [ $i -le 5 ]; do
  echo $i
  ((i++))
done

function greet() {
  echo "Hello, $1"
}
greet "Alex"

while read line; do
  echo $line
done < file.txt

echo "Text" >> file.txt

array=(1 2 3 4 5)
for i in "${array[@]}"; do
  echo $i
done

count=1
until [ $count -gt 5 ]; do
  echo "Число: $count"
  ((count++))
done

ls > output.txt
ls nonexistent_file 2> error.txt
ls > output.txt 2>&1


# chmod +x script.sh
# ./script.sh
# ./script.sh &

# touch text.txt
