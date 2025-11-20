# Orchestrator
Python script to verify music tag data before copying it to the proper location

Designed to be run in a docker container, example docker-compose.yml provided.

Please provide a .env with the following values:

```
FILESYSTEM_PATH=*path to root of media location (structure described below)*
WEBHOOK_URL=*discord webhook url to log to*
```

Folder Structure:

FILESYSTEM_PATH/
  ToBeApproved - location where media is placed to be checked, also the location where 'done' file is checked for before running to prevent attempting to check incomplete copies
  Rejected - location of log file & where rejected files are placed
  The Actual Playlist - location of where media files are stored/organized (album artist/album/tracknumber. title.flac)

Example webhook message:

<img width="436" height="253" alt="image" src="https://github.com/user-attachments/assets/a9ec9776-8eed-45c2-b774-25ed0c23b4d3" />

Example logfile message:
```
==========/pretend/this/is/a/filesystem/path/Kenshi Yonezu - IRIS OUT.flac==========
Title          | 🟢 | IRIS OUT
Artist         | 🟢 | Kenshi Yonezu
Album          | 🟢 | IRIS OUT
Album Artist   | 🟢 | Kenshi Yonezu
Genre          | 🟢 | Electronic; Anime; Soundtrack; Japan
Track Number   | 🟢 | 1/1
Year           | 🟢 | 2025
Artwork        | 🟢 | 1280 x 1280
```
