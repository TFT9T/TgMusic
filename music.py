# Author: https://github.com/AYMENJD (AYMEN Mohammed telegram.me/K6KKK).

from time import time, sleep
from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.utils import MAX_CHANNEL_ID
from stopwatch import Stopwatch
from os import remove
from lang import lang
import pytgcalls, asyncio, concurrent.futures, functools, ffmpeg, config, signal

bot = Client("Music", api_id=config.API_ID, api_hash=config.API_HASH)
calls = {}
files = {}

message_filter = filters.group & filters.text & ~filters.edited & ~filters.via_bot

is_sudo = filters.create(
    lambda _, __, message: (message.from_user and message.from_user.id == config.SUDO)
)


async def is_allowed_filter(_, __, event):
    if event.from_user:
        if (
            event.from_user.is_contact
            or event.from_user.id == config.SUDO
            or event.outgoing
        ):
            return True
    return False


async def is_connected_filter(_, __, event):
    if event.chat.id in files:
        if files[event.chat.id].is_connected:
            return True
    return False


is_allowed = filters.create(is_allowed_filter)
is_connected = filters.create(is_connected_filter)


async def progress(current, total, res, chat_id):
    percent = int(current * 100 / total)
    if percent != 100:
        text = lang["downloading"].format(percent)
    else:
        text = lang["downloaded"].format(percent)
    try:
        await res.edit_text(text)
    except Exception as e:
        print(e)


async def set_call_title(title, call):
    try:
        await bot.send(
            functions.phone.EditGroupCallTitle(
                call=call.full_chat.call,
                title=title,
            )
        )
    except:
        pass


def removeMarkdown(text):
    chars = ["[", "]", "_", "`", "*"]
    for char in chars:
        text = text.replace(char, "")
    return text


# def on_played(_, leng):
#     pass


class Player(object):
    def __init__(self, client, chat_id) -> None:
        self.call = pytgcalls.GroupCallFactory(client)
        self.chat_id = chat_id
        self.is_playing = False
        self.playlist = []
        self.unique_ids = []
        self.ffmpeg = None
        self.current = Stopwatch()

    async def connection(self, group_call, is_connected):
        if is_connected:
            await bot.send_message(self.chat_id, lang["joined"])
        else:
            if self.ffmpeg:
                self.ffmpeg.send_signal(signal.SIGTERM)
            for msg in self.playlist:
                try:
                    remove(msg["path"])
                    remove(msg["rawPath"])
                except Exception as e:
                    print("Exception while removing:", str(e))
            self.current.stop()
            del calls[self.chat_id]
            del files[self.chat_id]
            await bot.send_message(self.chat_id, lang["leving"])

    async def playout_ended(self, group_call, input_file, from_outside=False):
        if len(self.playlist) == 1 and from_outside == False:
            self.current.reset()
            return False
        else:
            old = self.playlist[0]
            remove(old["path"])
            remove(old["rawPath"])
            self.unique_ids.remove(old["unique"])
            self.playlist.pop(0)
            new = self.playlist[0]
            if new.reply_to_message.audio:
                title = new.reply_to_message.audio.title
            else:
                title = "@YYYYF"
            self.ffmpeg = (
                ffmpeg.input(new["path"])
                .output(
                    new["rawPath"], format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
                )
                .overwrite_output()
                .run_async(quiet=True)
            )
            await asyncio.sleep(1)
            files[self.chat_id].input_filename = new["rawPath"]
            await set_call_title(title, files[self.chat_id])
            self.current.reset()
            await new.reply_to_message.reply_text(
                "{} [{}](t.me/YYYYF)".format(lang["playing"], removeMarkdown(title))
            )
            await self.myplaylist()
        self.is_playing = True
        return True

    async def myplaylist(self, send=True):
        playlist = lang["playlist"]["empty"]
        if len(self.playlist) != 0:
            playlist = "{}\n\n".format(lang["playlist"]["playlist"])
            count = 1
            peer = await bot.resolve_peer(self.chat_id)
            for msg in self.playlist:
                link = await bot.send(
                    functions.channels.ExportMessageLink(
                        channel=peer, id=msg.reply_to_message.message_id
                    )
                )
                if msg["is_audio"]:
                    playlist += "{}) [{}]({})\n".format(
                        count, removeMarkdown(msg["title"]), link["link"]
                    )
                else:
                    playlist += "{}) [{}]({})\n".format(
                        count, msg["title"], link["link"]
                    )
                count += 1
            playlist += "\n\n[Made with 💜](https://github.com/2ib/TgMusic)."
        if send:
            return await bot.send_message(self.chat_id, playlist)
        return playlist


# -----


@bot.on_message(message_filter & is_allowed & filters.regex("^(\\/|.)help$"))
async def _help(client, event):
    await event.reply_text(lang["help"])


@bot.on_message(
    message_filter & is_connected & is_allowed & filters.regex("^(\\/|.)mute$")
)
async def mute(client, event):
    await files[event.chat.id].set_is_mute(True)
    calls[event.chat.id].current.pause()
    await event.reply_text(lang["mute"])


@bot.on_message(
    message_filter & is_connected & is_allowed & filters.regex("^(\\/|.)unmute$")
)
async def unmute(client, event):
    await files[event.chat.id].set_is_mute(False)
    await event.reply_text(lang["unmute"])


@bot.on_message(
    message_filter & is_connected & is_allowed & filters.regex("^(\\/|.)pause$")
)
async def pause(client, event):
    if calls[event.chat.id].is_playing:
        files[event.chat.id].pause_playout()
        calls[event.chat.id].current.pause()
        message = calls[event.chat.id].playlist[0].reply_to_message
        await message.reply_text(lang["pause"])
    else:
        await event.reply_text(lang["no_music"])


@bot.on_message(
    message_filter & is_connected & is_allowed & filters.regex("^(\\/|.)stop$")
)
async def stop(client, event):
    files[event.chat.id].input_filename = ""
    call = calls[event.chat.id]
    if call.ffmpeg:
        call.ffmpeg.send_signal(signal.SIGINT)
    for playlist in call.playlist:
        remove(playlist["path"])
        remove(playlist["rawPath"])

    call.playlist = []
    call.unique_ids = []
    call.is_playing = False
    call.ffmpeg = None
    await event.reply_text(lang["stop"])


@bot.on_message(
    message_filter & is_connected & is_allowed & filters.regex("^(\\/|.)leave$")
)
async def leave(client, event):
    await files[event.chat.id].stop()


@bot.on_message(message_filter & is_allowed & filters.regex("^(\\/|.)total$"))
async def total(client, event):
    length = len(files)
    if length > 0:
        await event.reply_text(lang["total"].format(length))
    else:
        await event.reply_text(lang["no_total"])


@bot.on_message(
    message_filter & is_sudo & filters.reply & filters.regex("^(\\/|.)add$")
)
async def add(client, event):
    if event.reply_to_message.from_user:
        if event.reply_to_message.from_user.is_contact:
            await event.reply_text(lang["already_add_contact"])
        else:
            await client.add_contact(
                event.reply_to_message.from_user.id,
                event.reply_to_message.from_user.first_name,
            )
            await event.reply_text(lang["add_contact"])


@bot.on_message(
    message_filter & is_sudo & filters.reply & filters.regex("^(\\/|.)remove$")
)
async def cremove(client, event):
    if event.reply_to_message.from_user:
        if event.reply_to_message.from_user.is_contact:
            await client.delete_contacts(event.reply_to_message.from_user.id)
            await event.reply_text(lang["delete_contact"])
        else:
            await event.reply_text(lang["already_delete_contact"])


@bot.on_message(
    message_filter & is_connected & is_allowed & filters.regex("^(\\/|.)resume$")
)
async def resume(client, event):
    if calls[event.chat.id].is_playing:
        files[event.chat.id].resume_playout()
        calls[event.chat.id].current.start()
        message = calls[event.chat.id].playlist[0].reply_to_message
        await message.reply_text(lang["resume"])
    else:
        await event.reply_text(lang["no_music"])


@bot.on_message(
    message_filter & is_connected & is_allowed & filters.regex("^(\\/|.)replay$")
)
async def replay(client, event):
    if calls[event.chat.id].is_playing:
        files[event.chat.id].restart_playout()
        calls[event.chat.id].current.reset()
        message = calls[event.chat.id].playlist[0].reply_to_message
        await message.reply_text(lang["replay"])
    else:
        await event.reply_text(lang["no_music"])


@bot.on_message(
    message_filter & is_connected & is_allowed & filters.command("volume", prefixes="/")
)
async def volume(client, event):
    if len(event.command) == 2:
        volume = int(event.command[1])
        if volume > 200 or volume < 1:
            return await event.reply_text(lang["volume_warning"])
        await files[event.chat.id].set_my_volume(int(event.command[1]))
        await event.reply_text(lang["volume"].format(event.command[1]))


@bot.on_message(
    message_filter & is_connected & is_allowed & filters.regex("^(\\/|.)music$")
)
async def music(client, event):
    call = calls[event.chat.id]
    if call.is_playing:
        msg = call.playlist[0].reply_to_message
        await msg.reply_text(
            "{} {}/{}".format(
                lang["duration"],
                call.current.format(),
                call.current.format(call.playlist[0]["duration"]),
            )
        )
    else:
        await event.reply_text(lang["no_music_"])


@bot.on_message(message_filter & is_allowed & filters.regex("^(\\/|.)join$"))
async def join(client, event):
    global files, calls
    chat_id = event.chat.id
    if chat_id in calls:
        await event.reply_text(lang["already_joined"])
    else:
        if event.from_user:
            if (
                len(calls) > config.limits["calls"]
                and event.from_user.id != config.SUDO
            ):
                return await event.reply_text(lang["calls_limit"])
            calls[chat_id] = Player(client, chat_id)
            # await call[chat_id].call.get_raw_group_call(on_played_data=on_played).start(
            #     chat_id
            # )
            file = calls[chat_id].call.get_file_group_call()
            file.add_handler(
                calls[chat_id].connection,
                pytgcalls.GroupCallFileAction.NETWORK_STATUS_CHANGED,
            )
            file.add_handler(
                calls[chat_id].playout_ended,
                pytgcalls.GroupCallFileAction.PLAYOUT_ENDED,
            )
            files[chat_id] = file
            await file.start(chat_id)


@bot.on_message(
    message_filter
    & is_connected
    & is_allowed
    & filters.reply
    & filters.regex("^(\\/|.)play$")
)
async def play(client, event):
    chat_id = event.chat.id
    reply = event.reply_to_message
    call = calls[chat_id]
    title = "@YYYYF"
    duration = None
    file_unique_id = None
    file_size = 0
    is_audio = False

    if reply.audio:
        title = reply.audio.title
        duration = reply.audio.duration
        file_unique_id = reply.audio.file_unique_id
        file_size = reply.audio.file_size
        is_audio = True
    elif reply.video:
        duration = reply.video.duration
        file_unique_id = reply.video.file_unique_id
        file_size = reply.video.file_size
    elif reply.voice:
        duration = reply.voice.duration
        file_size = reply.voice.file_size
        file_unique_id = reply.voice.file_unique_id

    if duration == 0 or file_size == 0 or file_unique_id == None:
        return await event.reply_text(lang["unsupported"])
    elif len(call.playlist) > config.limits["playlist"]:
        return await event.reply_text(lang["playlist"]["full"])
    elif file_size > config.limits["filesize"]:
        return event.reply_text(
            lang["file_size_limit"].format(int(config.limits["file_size"] / (1 << 20)))
        )
    elif duration > config.limits["duration"]:
        min = call.current.format(config.limits["duration"], "%M")
        return await event.reply_text(lang["duration_limit"].format(min))
    elif file_unique_id in call.unique_ids:
        return await event.reply_text(lang["playlist"]["exists"])
    else:
        res = await event.reply_text(lang["download"])
        try:
            path = await reply.download(progress=progress, progress_args=(res, chat_id))
        except Exception:
            return await res.edit_text(lang["download_error"])
        rawPath = "downloads/raw" + str(chat_id) + ".raw"
        event["path"] = path
        event["title"] = title
        event["rawPath"] = rawPath
        event["unique"] = file_unique_id
        event["duration"] = duration
        event["is_audio"] = is_audio
        if len(call.playlist) == 0:
            call.ffmpeg = (
                ffmpeg.input(path)
                .output(rawPath, format="s16le", acodec="pcm_s16le", ac=2, ar="48k")
                .overwrite_output()
                .run_async(quiet=True)
            )
            await asyncio.sleep(1)
            files[chat_id].input_filename = rawPath
            call.current.start()
            call.is_playing = True
            await set_call_title(title, files[chat_id])

        call.playlist.append(event)
        call.unique_ids.append(file_unique_id)
        await res.edit_text(lang["playlist"]["added"])


@bot.on_message(
    message_filter & is_connected & is_allowed & filters.regex("^(\\/|.)skip$")
)
async def skip(client, event):
    call = calls[event.chat.id]
    if call.is_playing:
        res = await call.playout_ended(
            files[event.chat.id], files[event.chat.id].input_filename, True
        )
        if not res:
            return await event.reply_text(lang["playlist"]["only_one"])
    else:
        return await event.reply_text(lang["skip"])


@bot.on_message(
    message_filter & is_connected & is_allowed & filters.regex("^(\\/|.)playlist$")
)
async def playlist(client, event):
    call = calls[event.chat.id]
    await event.reply_text(await call.myplaylist(send=False))


def _stop_handler():
    print("OwO bye bye")
    for _, call in calls.items():
        if call.ffmpeg:
            call.ffmpeg.send_signal(signal.SIGTERM)
        for msg in call.playlist:
            try:
                remove(msg["rawPath"])
                remove(msg["path"])
            except Exception as e:
                print(e)
    quit()


loop = asyncio.get_event_loop()
for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGABRT, signal.SIGQUIT]:
    loop.add_signal_handler(sig, _stop_handler)

bot.run()
