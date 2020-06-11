FROM oillibrary

RUN yum install -y gcc
RUN conda install pip    
COPY ./ /oillibraryapi/
RUN cd /oillibraryapi/ && conda install --file conda_requirements.txt
RUN cd /oillibraryapi/ && pip install -e .
 
RUN mkdir /config
RUN cp /oillibraryapi/config-example.ini /config/config.ini
RUN ln -s /config/config.ini /oillibraryapi/config.ini

EXPOSE 9898
VOLUME /config
ENTRYPOINT ["/oillibraryapi/docker_start.sh"]
