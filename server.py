# ==============================================
# server_fastapi.py
# FastAPI implementation for Music DNA
# ==============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.import_tidal import (
    get_album_tracks,
    get_albums,
    get_artist,
    get_artist_byalbum,
    get_artist_bytrack,
    get_favorites,
    get_top_tracks,
    get_tracks,
)


# ==============================================
# FASTAPI APPLICATION
# ==============================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================
# HELPERS
# ==============================================

def parameter_splitter(value):
    """
    Convert a comma-separated query value into a list.

    Examples:
        None                    -> []
        "Radiohead"             -> ["Radiohead"]
        "Radiohead,Portishead"  -> ["Radiohead", "Portishead"]

    A list is also accepted so this remains compatible with older code.
    """
    if not value:
        return []

    if isinstance(value, str):
        value = [value]

    parameters = []

    for item in value:
        parameters.extend(
            parameter.strip()
            for parameter in item.split(",")
            if parameter.strip()
        )

    return parameters



# ==============================================
# ROOT ROUTES
# ==============================================

@app.get("/")
async def root():
    return {"message": "Server is running"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return {}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "music_dna_api",
    }


# ==============================================
# FAVORITES
# ==============================================

@app.get("/getfavorites")
async def favorites_handler(
    artist=None,
    album=None,
    top=False,
):
    artist = parameter_splitter(artist)
    album = parameter_splitter(album)

    print(f"GET FAVORITES | artist={artist} | album={album} | top={top}")

    data = await get_favorites(
        artist or None,
        album or None,
        collections=True,
    )

    return {
        "id": "getfavorites",
        "data": data,
    }


# ==============================================
# TRACKS
# ==============================================

@app.get("/gettracks")
async def track_handler(
    artist=None,
    album=None,
    track=None,
    top=False,
    limit=None,
):
    artist = parameter_splitter(artist)
    album = parameter_splitter(album)
    track = parameter_splitter(track)

    top = str(top).lower() == "true"
    limit = int(limit) if limit else (50 if top else 100)

    print(f"GET TRACKS | artist={artist} | album={album} | track={track} | top={top} | limit={limit}")

    if top:
        data = await get_top_tracks(
            artist,
            album,
            limit,
        )

    elif album and not artist:
        data = await get_album_tracks(album)

    elif artist:
        data = await get_tracks(
            artist,
            True,
            limit,
        )

    elif track:
        data = await get_tracks(
            track,
            False,
            limit,
        )

    else:
        data = []

    return {
        "id": "gettracks",
        "data": data,
    }


# ==============================================
# ALBUMS
# ==============================================

@app.get("/getalbums")
async def album_handler(
    artist=None,
    album=None,
    tracks=None,
    top=False,
):
    artist = parameter_splitter(artist)
    album = parameter_splitter(album)
    tracks = parameter_splitter(tracks)

    print(f"GET ALBUMS | artist={artist} | album={album} | tracks={tracks} | top={top}")

    if artist:
        data = await get_albums(artist)

    elif tracks:
        data = await get_albums(tracks)

    elif album:
        data = await get_albums(album)

    else:
        data = []

    return {
        "id": "getalbums",
        "data": data,
    }


# ==============================================
# ARTISTS
# ==============================================

@app.get("/getartist")
async def artist_handler(
    artist=None,
    album=None,
    track=None,
):
    artist = parameter_splitter(artist)
    album = parameter_splitter(album)
    track = parameter_splitter(track)

    print(f"GET ARTIST | artist={artist} | album={album} | track={track}")

    if album:
        data = await get_artist_byalbum(album)

    elif track:
        data = await get_artist_bytrack(track)

    elif artist:
        data = await get_artist(artist)

    else:
        data = []

    return {
        "id": "getartist",
        "data": data,
    }


# ==============================================
# LOCAL DEVELOPMENT
# ==============================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server_fastapi:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
