<p align="center">
   <a href="https://github.com/2ib/TgMusic">
   <img src="https://github.com/2ib/TgMusic/blob/master/logo.png" width="400px" alt="TgMusic">
   </a>
   <br>
   <b>Easy, Sample and Powerful userbot</b>
   <br>
   <a href="https://github.com/AYMENJD/TgMusic#features">
   Features
   </a>
   ~
   <a href="https://github.com/AYMENJD/TgMusic#installation">
   Installation
   </a>
   ~
   <a href="https://t.me/YYYYF">
   Channel
   </a>
   ~
   <a href="https://t.me/K6KKK">
   Author
   </a>
</p>

# TgMusic

Easy and Simple Telegram UserBot focused to play music in Groups, based on [tgcalls](https://github.com/MarshalX/tgcalls)

### Features

- Support multi group calls
- Support audio, video, voice formats
- Storage optmized
- Get current played duration `/music`
- Chat music playlist `/playlist`
- Edit call title to played audio file title
- Easy to translate bot texts

### Requirements

- python3.6+
- Telegram [api keys](https://docs.pyrogram.org/intro/setup#api-keys)
- pyrogram (github version)
- tgcalls
- ffmpeg-python

### Installation

- Clone the repository with git:

```bash
git clone https://github.com/AYMENJD/TgMusic && cd TgMusic
```

- Install requirements with pip:

```bash
pip install -r requirements.txt
```

- After installing successful fill [config.py](https://github.com/2ib/TgMusic/blob/master/config.py) file with your information

Then run the bot:

```bash
python3 music.py
```

### Languages

- [AYMENJD/TgMusic](https://github.com/AYMENJD/TgMusic) ~ Arabic

If you want your language listed here feel free to fork this repo and translate [lang.py](https://github.com/2ib/TgMusic/blob/master/lang.py) to your language

### Commands

Available commands:
| Command | Descrption |
| ------- | ---------- |
| `/join` | Join group call |
| `/leave` | Leave group call |
| `/play` | Play replyed music |
| `/stop` | Stop music and delete all playlist |
| `/playlist` | Shows current chat playlist |
| `/skip` | Skips current music if playlist not empty |
| `/replay` | Replays current music |
| `/pause` | Pause current music |
| `/resume` | Resume current music |
| `/music` | :) |
| `/mute` | Mute the bot, use `/pause` instead |
| `/ummute` | Unmute the bot |
| `/volume` | Sets bot volume 1 ~ 200, bot must be admin |
| `/add` | Add the replyed user to `contacts` list (SUDO) |
| `/remove` | Remove the replyed user from `contacts` list (SUDO) |

Commands only works for SUDO and account contacts.

### Thanks to

- [Dan](https://github.com/delivrance) For Amaizing MTProto library [pyrogram](https://github.com/pyrogram/pyrogram)
- [Il'ya](https://github.com/MarshalX) For Amaizing python Telegram calls library [tgcalls](https://github.com/MarshalX/tgcalls)
- You for using this repo

# License

MIT [License](https://github.com/2ib/TgMusic/blob/master/LICENSE)
