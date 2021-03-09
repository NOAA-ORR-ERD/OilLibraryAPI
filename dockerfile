FROM oillibrary

# nothing to compile here
# RUN yum install -y gcc
COPY ./ /oillibraryapi/
RUN cd /oillibraryapi/ && conda install --file conda_requirements_py3.txt
# should we be using develop mode? why not install?
RUN cd /oillibraryapi/ && python setup.py develop
 
RUN mkdir /config
RUN cp /oillibraryapi/config-example.ini /config/config.ini
RUN ln -s /config/config.ini /oillibraryapi/config.ini

EXPOSE 9898
VOLUME /config
ENTRYPOINT ["/oillibraryapi/docker_start.sh"]
