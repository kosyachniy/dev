#!/bin/bash

while read i
do
    IKEY=$(echo ${i} | cut -d '=' -f 1)
    IVALUE=$(echo ${i} | cut -d '=' -f 2)
    export "REACT_APP_${IKEY}"="${IVALUE}"
done < <(env)

npm start
