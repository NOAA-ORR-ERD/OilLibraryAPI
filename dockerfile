FROM oillibrary

COPY ./ /oillibraryapi/
RUN cd /oillibraryapi/ && pip install -r requirements.txt
RUN cd /oillibraryapi/ && pip install -e .
 
RUN mkdir /config
RUN cp /oillibraryapi/config-example.ini /config/config.ini
RUN ln -s /config/config.ini /oillibraryapi/config.ini

EXPOSE 9898
VOLUME /config
ENTRYPOINT ["/oillibraryapi/docker_start.sh"]
