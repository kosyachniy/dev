FROM python:3.10

# -slim-buster
# RUN apt-get update && apt-get install gcc g++ make -y

RUN apt-get update
RUN yes | apt-get install texlive-latex-base
RUN yes | apt-get install texlive-fonts-recommended
RUN yes | apt-get install texlive-fonts-extra
RUN yes | apt-get install texlive-latex-extra
RUN yes | apt -y install texlive-lang-cyrillic
RUN yes | wget https://www.tug.org/fonts/getnonfreefonts/install-getnonfreefonts
RUN yes | texlua install-getnonfreefonts

COPY . /app
