
from gimpfu import *
import gimpfu
import json

base_headers = [
    {"header": 'POS', "driverKey": 'position'},
    {"header": 'DRIVER', "driverKey": 'driver'},
    {"header": 'TIME', "driverKey": 'time'},
    {"header": 'GAP', "driverKey": 'gap'},
    {"header": 'LAP', "driverKey": 'lap'},
]
base_col_offset = [75, 75, 300, 400, 500]

base_scoreboard_config = {
    "width": 1920,
    "height": 1080,
    "background_width": 1200,
    "background_height": 800,
    "header": "TROPHY RESULTS",
    "header_prefix": "",
    "headers": base_headers,
    "col_offsets": base_col_offset
}

points_headers = [
    {"header": 'POS', "driverKey": 'position'},
    {"header": 'DRIVER', "driverKey": 'driver'},
    {"header": 'POINTS', "driverKey": 'points'},
]
points_col_offset = [25, 25, 325]

points_scoreboard_config = {
    "width": 1920,
    "height": 1080,
    "background_width": 700,
    "background_height": 800,
    "header": "POINT STANDINGS",
    "header_prefix": "",
    "headers": points_headers,
    "col_offsets": points_col_offset
}

qualification_headers = [
    {"header": 'POS', "driverKey": 'position'},
    {"header": 'DRIVER', "driverKey": 'driver'},
    {"header": 'LAP', "driverKey": 'lap'},
    {"header": 'GAP', "driverKey": 'gap'},
]
qualification_col_offset = [50, 100, 400, 600]

qualification_scoreboard_config = {
    "width": 1920,
    "height": 1080,
    "background_width": 1200,
    "background_height": 800,
    "header": "QUALIFICATION RESULTS",
    "header_prefix": "",
    "headers": qualification_headers,
    "col_offsets": qualification_col_offset
}

configs = {
    "base": base_scoreboard_config,
    "points": points_scoreboard_config,
    "qualification": qualification_scoreboard_config,
}

title_offset = 110
row_offset = 70
row_multiplier_offset = 45
row_background_offset = 45
global currentConfig

rows = {}
cols = {}


def calculateRows(img, layer, data):
    rows['header'] = (img.height / 2 - layer.height / 2) + (row_offset + 10)
    for position in range(len(data)):
        rows[position] = (img.height / 2 - layer.height / 2) + \
            (title_offset + 15 + (row_multiplier_offset * (position)))


def calculateCols(img, currentConfig):
    index = 0
    print(currentConfig)
    for header in currentConfig["headers"]:
        print(index)
        print(currentConfig['col_offsets'])
        cols[header['driverKey']] = img.width / 2 - currentConfig['background_width'] / \
            2 + (title_offset * (index)) + currentConfig['col_offsets'][index]
        index += 1


def getCorrectConfig(configKey, header_prefix, data):
    currentConfig = configs[configKey]
    currentConfig['header_prefix'] = header_prefix
    currentConfig['background_height'] = row_background_offset * \
        len(data) + (title_offset + 15)
    return currentConfig


def execPlugin(img, layer, dataFile, headerPrefix, configKey):
    f = open(dataFile)
    data = json.load(f)
    currentConfig = getCorrectConfig(configKey, headerPrefix, data)
    print(currentConfig)

    for driver in data:
        driver['driver'] = driver['driver'].strip()

    # create the image

    img = pdb.gimp_image_new(
        currentConfig['width'], currentConfig['height'], gimpfu.RGB)
    background_layer = pdb.gimp_layer_new_from_visible(
        img, img, "new transparent image size layer")

    # add layer with 100% of opacity
    scoreboard_background_layer = create_scoreboard_background(
        img, currentConfig)

    calculateCols(img, currentConfig)
    calculateRows(img, scoreboard_background_layer, data)

    create_scoreboard_header(img, scoreboard_background_layer, currentConfig)
    create_line(img, scoreboard_background_layer, background_layer)
    createHeaders(img, currentConfig['headers'])
    createContent(img, data, currentConfig['headers'])

    # #remove any selection
    pdb.gimp_selection_none(img)

    # and display the image
    pdb.gimp_display_new(img)


def create_line(img, scoreboard_background_layer, background_layer):
    pdb.gimp_selection_none(img)
    pdb.gimp_image_add_layer(img, background_layer, 0)

    pdb.gimp_context_set_brush("2. Hardness 100")
    pdb.gimp_context_set_brush_size(2.0)
    pdb.gimp_context_set_opacity(100)

    point1 = [img.width / 2 - scoreboard_background_layer.width / 2 + 10,
              (img.height / 2 - scoreboard_background_layer.height / 2) + row_offset]
    point2 = [((img.width / 2 - scoreboard_background_layer.width / 2) + scoreboard_background_layer.width) -
              10, (img.height / 2 - scoreboard_background_layer.height / 2) + row_offset]
    points = point1 + point2
    pdb.gimp_context_set_foreground((255, 255, 255))
    pdb.gimp_pencil(background_layer, 4, points)


def create_scoreboard_header(img, scoreboard_background_layer, currentConfig):
    pdb.gimp_context_set_foreground((255, 255, 255))
    titleTextLayer = pdb.gimp_text_layer_new(
        img, currentConfig['header_prefix'] + ' ' + currentConfig['header'], 'Exo Ultra-Bold Italic', 40.0, 0)
    pdb.gimp_layer_set_offsets(titleTextLayer, img.width / 2 - titleTextLayer.width / 2,
                               (img.height / 2 - scoreboard_background_layer.height / 2) + 15)

    pdb.gimp_image_add_layer(img, titleTextLayer, 0)


def create_scoreboard_background(img, currentConfig):
    scoreboard_background_layer = pdb.gimp_layer_new(
        img, currentConfig['background_width'], currentConfig['background_height'], gimpfu.RGB_IMAGE, "base", 70, gimpfu.NORMAL_MODE)
    top_left_layer_x = img.width / 2 - scoreboard_background_layer.width / 2
    top_left_layer_y = img.height / 2 - scoreboard_background_layer.height / 2

    pdb.gimp_layer_set_offsets(
        scoreboard_background_layer, top_left_layer_x, top_left_layer_y)
    pdb.gimp_image_add_layer(img, scoreboard_background_layer, 0)
    return scoreboard_background_layer


def get_visible(parent, outputList):
    for layer in parent.layers:
        if pdb.gimp_layer_get_visible(layer):
            outputList.append(layer)
            if pdb.gimp_item_is_group(layer):
                get_visible(layer, outputList)


def createHeaders(img, headers):
    for header in headers:
        headerLayer = pdb.gimp_text_layer_new(
            img, header['header'], 'Exo Ultra-Bold Italic', 30.0, 0)
        pdb.gimp_layer_set_offsets(
            headerLayer, cols[header['driverKey']], rows['header'])
        pdb.gimp_image_add_layer(img, headerLayer, 0)


def createContent(img, data, headers):
    for position in range(len(data)):
        driver = data[position]
        for i in range(len(driver)):
            newLayer = pdb.gimp_text_layer_new(
                img, driver[headers[i]['driverKey'].lower()], 'Exo Ultra-Bold Italic', 30.0, 0)
            pdb.gimp_layer_set_offsets(
                newLayer, cols[headers[i]['driverKey']], rows[position])
            pdb.gimp_image_add_layer(img, newLayer, 0)


gimpfu.register(
    "DrawScoreboard",
    "Show message",
    "Show message",
    "CJ Meeks",
    "CJ Meeks",
    "2022",
    "<Image>/MyFunctions/DrawScoreboard",
    "",
    [
        (gimpfu.PF_STRING, "DataFile", "DataFile", "C:\Users\cjmeeks\dev\scoreboard-vision\data\ICSTC\\rd1team.json"),
        (gimpfu.PF_STRING, "HeaderPrefix", "HeaderPrefix", "Superlights"),
        (gimpfu.PF_STRING, "ConfigKey", "ConfigKey", "points"),
    ],
    [],
    execPlugin)


gimpfu.main()
