FROM nginx
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev curl libbz2-dev git
RUN apt-get install -y python3-pip ufw
RUN apt-get install -y graphviz

ENV PYTHONPATH=/usr/lib/python3.7/dist-packages
RUN pip3 install uwsgi

RUN git clone https://github.com/rdchar/Hora.git ./hypernetworks
RUN cd ./hypernetworks
WORKDIR ./hypernetworks
RUN pip3 install .

RUN ln -sf /usr/bin/python3 /usr/bin/python

ENV PATH="/usr/local/lib/python3.7/dist-packages/hypernetworks/bin:${PATH}"

EXPOSE 5000

CMD ["ufw", "allow", "5000"]

ENTRYPOINT ["uwsgi"]
CMD ["--socket", "0.0.0.0:5000", "--protocol=http", "-w", "wsgi:app"]
