from flask import Flask, request, send_from_directory, jsonify, make_response
from flask_cors import CORS, cross_origin

import json
import board
import neopixel
import threading
import queue
import time
import colorsys

app = Flask(__name__)
cors = CORS(app, resource={r"/update": {"origins": "http://lisica.lan/*"}})
app.config["CORS_HEADERS"] = "Content-Type"


# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory("client/build", "index.html")


# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory("client/build", path)


# For updating leds
@app.route("/update", methods=["POST"])
@cross_origin()
def update():
    request.get_json(force=True)
    content = request.json
    color_queue.put(content["colors"])
    return make_response(jsonify({}), 201)


color_queue = queue.Queue()


def blend_hsv_colors(hsv1, hsv2, blend_factor):
    # Calculate the shortest angular difference between hues
    hue1, hue2 = hsv1[0], hsv2[0]
    if abs(hue1 - hue2) > 0.5:  # Check if it's shorter to go the other way around
        if hue1 < hue2:
            hue1 += 1.0
        else:
            hue2 += 1.0

    # Interpolate the HSV values
    h = (1 - blend_factor) * hue1 + blend_factor * hue2
    s = (1 - blend_factor) * hsv1[1] + blend_factor * hsv2[1]
    v = (1 - blend_factor) * hsv1[2] + blend_factor * hsv2[2]

    # Ensure hue is within the [0, 1) range
    h %= 1.0

    return (h, s, v)


state_stay = 0
state_transition = 1


def background_thread():
    pixel_pin = board.D18
    num_pixels = 180
    ORDER = neopixel.GRB

    state = state_stay
    colors = []
    color_index = 0
    color_index2 = 1
    color_transition_seconds = 1.0
    color_stay_seconds = 10.0
    color_transition_elapsed_seconds = 0.0

    fps = 60
    delta_t = 1.0 / fps

    pixels = neopixel.NeoPixel(
        pixel_pin, num_pixels, brightness=0.8, auto_write=False, pixel_order=ORDER
    )

    f = open("layout.json")
    layout = json.load(f)

    while True:
        try:
            colors = color_queue.get(block=False)
            for i in range(0, len(colors)):
                colors[i] = colorsys.rgb_to_hsv(
                    colors[i][0] / 255.0, colors[i][1] / 255.0, colors[i][2] / 255.0
                )
            color_index = 0

        except queue.Empty:
            pass

        if len(colors) < 2:
            continue

        if state == state_stay:
            blend_factor = color_transition_elapsed_seconds / color_stay_seconds

            if blend_factor >= 1:
                color_transition_elapsed_seconds = 0.0
                state = state_transition
                print("state transition")

        elif state == state_transition:
            hsv1 = colors[color_index]
            hsv2 = colors[color_index2]

            blend_factor = color_transition_elapsed_seconds / color_transition_seconds

            if blend_factor >= 1:
                color_index = (color_index + 1) % len(colors)
                color_index2 = (color_index + 1) % len(colors)
                color_transition_elapsed_seconds = 0.0
                state = state_stay
                print("state stay")

            hsv = blend_hsv_colors(hsv1, hsv2, blend_factor)
            r, g, b = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])

            for i, leds in enumerate(layout["leds"]):
                pixels[i] = (int(r * 255), int(g * 255), int(b * 255))
            pixels.show()

        color_transition_elapsed_seconds += delta_t

        time.sleep(delta_t)


background_thread = threading.Thread(target=background_thread)
background_thread.daemon = True
background_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
