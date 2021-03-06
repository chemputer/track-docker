# Instructions
1. Clone the repo into a location of your choice with docker installed.
2. Populate the `data` directory with the following files using the [WoWS unpacker tool](https://forum.worldofwarships.eu/topic/113847-all-wows-unpack-tool-unpack-game-client-resources/):
    - GameParams.data, located in `res/content`.
    - ship_bars, located in `res/gui`.
    - spaces, located in `res`.
    - big, located in `res/gui/crew_commander/skills`.
    - global.mo for the language you intend to use. This is found by going to the root folder of your World of Warships install, then from there, the `bin` directory, then the folder for your current build of WoWS (usually, but not always, the highest number), then `res/texts` then you need to find the appropriate folder for your language, for example, English is `en`, then `LC_MESSAGES`, and in that folder is `global.mo`. The directory for english in my case, for the current version as of 1/15/2021, is `E:\Games\World_of_Warships\bin\3245976\res\texts\en\LC_MESSAGES`.
    - `Trebuchet MS.ttf` if you would like the font to be installed. It will work without this, it just won't look as nice.

3. Create a config.py file using config_template.py as your template, put that in the root folder, where Dockerfile is.

4. With Docker installed, build and run the Dockerfile. To do so, `cd` to the directory where the dockerfile is, and run `docker build . -t track-docker:latest`, if it builds correctly, you can then run it with `docker run -it track-docker bot`.
