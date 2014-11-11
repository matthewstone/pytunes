from flask import Flask, render_template, request, jsonify
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
    spotify_search = spotify_session.session.search(query).load()
    results = {}
    artists = []
    tracks = []
    for a in spotify_search.artists:
        a.load()
        artists.append({"name": a.name, "link": str(a.link)})
    results["artists"] = artists
    for t in spotify_search.tracks:
        t.load()
        tracks.append({"name": t.name, "artist": t.artists[0].load().name, "link": str(t.link)})
    results["tracks"] = tracks
    return jsonify(results)


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


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
