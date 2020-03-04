FROM python:3.8.2-alpine3.11

ARG BUILD_DATE
ARG SOURCE_BRANCH
ARG SOURCE_COMMIT

RUN pip install mkdocs=="${SOURCE_BRANCH}"

# Default exposed port by 'mkdocs serve' command
EXPOSE 8000

ENTRYPOINT [ "/usr/local/bin/mkdocs" ]
CMD [ "--help" ]

LABEL \
    org.label-schema.build-date="${BUILD_DATE}" \
    org.label-schema.name="mkdocs" \
    org.label-schema.description="Project documentation with Markdown." \
    org.label-schema.vcs-url="https://github.com/mkdocs/mkdocs" \
    org.label-schema.vcs-ref="${SOURCE_COMMIT}" \
    org.label-schema.version="${SOURCE_BRANCH}" \
    org.label-schema.schema-version="1.0"
