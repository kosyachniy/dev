FROM alpine:3.15

COPY . .

# NOTE: We cannot delete files that are attached via Docker Volume
RUN rm -f test_inner.json
RUN echo '{ \n\
    "name": "'$PROJECT_NAME'", \n\
    "test": "'$TEST'" \n\
} \n\
' >> /test_inner.json

# NOTE: Only one CMD
RUN chmod +x /entrypoint.sh
CMD /entrypoint.sh
