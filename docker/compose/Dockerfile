FROM alpine:3.15

COPY . .

# NOTE: We cannot delete files that are attached via Docker Volume
RUN rm -f test_inner.json
RUN echo '{ \n\
    "name": "'$PROJECT_NAME'", \n\
    "test": "'$TEST'" \n\
} \n\
' >> test_inner.json

# NOTE: By default, there are no launch rights
RUN chmod +x /entrypoint.sh

# NOTE: Only one CMD
CMD /entrypoint.sh
