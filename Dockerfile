# in case something's wrong with this script, mention @funkyfuture
# in issues and poll requests

FROM funkyfuture/nest-of-serpents

ENTRYPOINT tox
WORKDIR /src

RUN apt-get -q update \
 && apt-get install -qy --no-install-recommends nodejs-legacy npm ruby \
 && pip2.7 install LinkChecker \
 && pip3.6 install coverage flake8 nose mock tox \
 && pip3.6 install click Jinja2 livereload Markdown PyYAML tornado \
 && mkdir /home/tox \
 && mv /root/.cache /home/tox/ \
 && gem install -N mdl \
 && npm install -g csslint jshint \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ARG uid
RUN useradd --uid=$uid -m tox \
 && chown -R tox.tox /home/tox/.cache

ADD . .
RUN chown -R tox.tox .

USER tox
