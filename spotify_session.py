import threading
import spotify
import os
from configobj import ConfigObj

current_path = os.path.dirname(os.path.realpath(__file__))
config = ConfigObj(current_path + "/app.ini", write_empty_values=True)
override_config = ConfigObj(current_path + "/local.ini", write_empty_values=True)
config.merge(override_config)

logged_in_event = threading.Event()
end_of_track = threading.Event()
now_playing = None
playlist = []


def connection_state_listener(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in_event.set()


def on_end_of_track(session):
    global now_playing
    global playlist
    global is_playing
    if len(session.playlist) > 0:
        track = session.playlist.pop(0)
        if track == now_playing:
            return on_end_of_track(session)
        session.player.load(track)
        session.player.play()
        now_playing = track
    else:
        is_playing = False
        end_of_track.set()


def on_start_playback(session):
    global is_playing
    os.write(1, "Playback tsarted")
    is_playing = True

session = spotify.Session()
session.login(config["spotify_username"], config["spotify_password"], remember_me=True)
session.on(
    spotify.SessionEvent.CONNECTION_STATE_UPDATED,
    connection_state_listener)

session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)
audio = spotify.AlsaSink(session)
event_loop = spotify.EventLoop(session)
event_loop.start()

def add_to_playlist(track):
    global now_playing
    global playlist
    os.write(1, "Queue size is %s \n" % len(playlist))
    if len(playlist) == 0:
        session.player.load(track)
        session.player.play()
        now_playing = track
    if track not in playlist:
        playlist.append(track)
    session.playlist = playlist
