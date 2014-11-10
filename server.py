from flask import Flask, render_template, request
import spotify_session

app = Flask(__name__)


@app.route("/")
def index():
    cover = None
    playlist = []
    is_playing = False
    if spotify_session.now_playing:
        cover = spotify_session.now_playing.album.load().cover().load()
        is_playing = True
        playlist = [a.load() for a in spotify_session.session.playlist]
    return render_template('index.html', is_playing=is_playing, current_track=spotify_session.now_playing,
                           cover=cover, playlist=playlist)


@app.route("/search")
def search():
    query = request.args.get('q')
    search = spotify_session.session.search(query).load()
    artists = [a.load() for a in search.artists[:10]]
    tracks = [t.load() for t in search.tracks[:10]]
    return render_template('search.html', artists=artists, tracks=tracks)

@app.route("/play")
def play():
    is_playing = True
    track_uri = request.args.get("l")
    track = spotify_session.session.get_track(track_uri).load()
    spotify_session.add_to_playlist(track)
    now_playing = spotify_session.now_playing
    cover = now_playing.album.load().cover().load()
    playlist = [a.load() for a in spotify_session.session.playlist]
    return render_template('index.html', current_track=now_playing, cover=cover, is_playing=is_playing,
                           playlist=playlist)

@app.route("/pause")
def pause():
    spotify_session.session.player.pause()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
