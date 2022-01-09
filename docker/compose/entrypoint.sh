echo $PROJECT_NAME $TEST

:> test.json
echo '{
    "name": "'$PROJECT_NAME'",
    "test": "'$TEST'"
}' >> test.json

cat test.json
cat test_inner.json
