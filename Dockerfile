FROM python:3.7-buster
# installing necessary tools
RUN apt-get update; apt-get install -y curl wget git subversion gzip sudo apt-utils
# adding user track
RUN adduser --disabled-password --gecos "" track; \
cd /home/track;git clone https://github.com/padtrack/track.git; \
cd /home/track/track/track; \
svn checkout https://github.com/Monstrofil/replays_unpack/trunk/replay_unpack
# Installing all python dependencies
RUN python3 -m pip install -r /home/track/track/requirements.txt; python3 -m pip install git+https://github.com/Rapptz/discord-ext-menus
# debugging
#RUN echo $(ls /home/track/track/track) 
WORKDIR /home/track/track 
# copy over contents of data directory
COPY data/GameParams.data /home/track/track/track/scripts/gameparams/
COPY data/ship_bars/ /home/track/track/track/assets/private/
COPY data/spaces/ /home/track/track/track/assets/private/
COPY data/big/ /home/track/track/track/assets/private/
COPY data/battle_controller.py /home/track/track/track/utils/
COPY data/global.mo /home/track/track/track/assets/private/
COPY data/*.ttf /usr/local/share/fonts/
COPY config.py /home/track/track/track/
# allow replay_unpack to work with this by replacing the battle_controller with padtrack's modified one.
RUN cd /home/track/track/track/; for d in $(ls -d replay_unpack/clients/wows/versions); do cp utils/battle_controller.py $d/battle_controller.py; done
# get rush.txt.gz and extract it
RUN wget https://www.michaelfogleman.com/static/rush/rush.txt.gz -O /home/track/track/track/scripts/rush/rush.txt.gz; \
gzip -d /home/track/track/track/scripts/rush/rush.txt.gz 
# run the necessary scripts to create the databases
RUN cd /home/track/track/track/scripts/gameparams; python3 /home/track/track/track/scripts/gameparams/dump.py; \ 
cd /home/track/track/track/scripts/rush/; python3 /home/track/track/track/scripts/rush/dump.py; \
cd /home/track/track/track/scripts/; python3 /home/track/track/track/scripts/setup.py
# Start the bot
COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python3", "/home/track/track/track/bot.py"]
