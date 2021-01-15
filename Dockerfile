FROM python:3.7-buster
RUN apt-get update
RUN apt-get install -y curl wget git subversion
RUN mkdir -p /home/track \
    cd /home/track \
    git clone https://github.com/padtrack/track.git \
    cd track/track \
    svn checkout https://github.com/Monstrofil/replays_unpack/trunk/replay_unpack
WORKDIR /home/track/track 
COPY data/GameParams.data /home/track/track/track/scripts/gameparams/
COPY data/ship_bars/ /home/track/track/track/assets/private/
COPY data/spaces/ /home/track/track/track/assets/private/
COPY data/big/ /home/track/track/track/assets/private/
COPY data/battle_controller.py /home/track/track/track/
COPY data/global.mo /home/track/track/track/assets/private/
COPY config.py /home/track/track/track/
RUN cd /home/track/track
RUN for d in $(ls -d replay_unpack/clients/wows/versions); do cp utils/battle_controller.py $d/battle_controller.py; done
RUN wget https://www.michaelfogleman.com/static/rush/rush.txt.gz -O /home/track/track/track/scripts/rush/
RUN tar -xvzf /home/track/track/track/scripts/rush/rush.txt.gz 
RUN python -m pip install -r /home/track/track/requirements.txt
RUN python -m pip install git+https://github.com/Rapptz/discord-ext-menus
RUN python /home/track/track/track/scripts/gameparams/dump.py /home/track/track/track/scripts/gameparams/GameParams.data
RUN python /home/track/track/track/scripts/rush/dump.py /home/track/track/track/scripts/rush/rush.txt
RUN su track
# Start the bot
RUN python /home/track/track/track/bot.py