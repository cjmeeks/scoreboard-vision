#!/Applications/GIMP-2.10.app/Contents/MacOS/python
from gimpfu import *
import gimpfu
import json

positions=[1,2,3,4,5,6,7,8,9,10,11,12]

headers_finish=['POS','DRIVER','TIME','GAP','LAP']


# GIMP Python plug-in template. /Users/cliffordmeeks/dev/csup-scoreboard/data/image.json

def do_stuff(img, layer, data_file) :
    SIZE_W=1920
    SIZE_H=1080
    sc_w=940
    sc_h=540
    RADIO=24

    f = open(data_file)
    data = json.load(f)
    print(data[0])


    #create the image
    img=pdb.gimp_image_new(SIZE_W, SIZE_H, gimpfu.RGB)
    layer_one = pdb.gimp_layer_new_from_visible(img,img,"new transparent image size layer")

    #add layer with 100% of opacity
    layer=pdb.gimp_layer_new(img, sc_w, sc_h, gimpfu.RGB_IMAGE, "base", 70, gimpfu.NORMAL_MODE)
    pdb.gimp_layer_set_offsets(layer, img.width / 2 - layer.width / 2, img.height / 2 - layer.height / 2)
    pdb.gimp_image_add_layer(img, layer, 0)

    pdb.gimp_context_set_foreground((255, 255, 255))
    titleTextLayer = pdb.gimp_text_layer_new(img,'SUPERLIGHTS TROPHY RESULTS','Sans',30.0,0)
    pdb.gimp_layer_set_offsets(titleTextLayer, img.width / 2 - titleTextLayer.width / 2, (img.height / 2 - layer.height / 2) + 15)

    pdb.gimp_image_add_layer(img, titleTextLayer, 0)
    backgroundLayer = img.layers[0]


    #drawing lines practice

    pdb.gimp_selection_none(img)
    pdb.gimp_image_add_layer(img, layer_one, 0)

    pdb.gimp_context_set_brush("2. Hardness 100")
    pdb.gimp_context_set_brush_size(2.0)
    pdb.gimp_context_set_opacity(100)

    point1 = [img.width / 2 - layer.width / 2 + 10, (img.height / 2 - layer.height / 2) + 60]
    point2 = [((img.width / 2 - layer.width / 2) + layer.width) - 10, (img.height / 2 - layer.height / 2) + 60]
    points = point1 + point2
    pdb.gimp_context_set_foreground((255, 255, 255))
    pdb.gimp_pencil(layer_one,4,points)

    for position in positions:
        positionLayer = pdb.gimp_text_layer_new(img, str(position), 'Sans', 20.0, 0)
        pdb.gimp_layer_set_offsets(positionLayer, img.width / 2 - sc_w / 2 + 20, (img.height / 2 - layer.height / 2) + (100 + (35 * (position - 1))))
        pdb.gimp_image_add_layer(img, positionLayer, 0)
    index=0
    for header in headers_finish:
        index += 1
        headerLayer = pdb.gimp_text_layer_new(img, header, 'Sans', 20.0, 0)
        pdb.gimp_layer_set_offsets(headerLayer, img.width / 2 - sc_w / 2 + (100 * (index - 1)), (img.height / 2 - layer.height / 2) + (70))
        pdb.gimp_image_add_layer(img, headerLayer, 0)

    #we need it with alpha channel
    # pdb.gimp_layer_add_alpha(layer)

    # #access its drawable
    # drw = pdb.gimp_image_active_drawable(img)

    # #set background to black, and foreground to white
    # pdb.gimp_context_set_background((0,0,0))
    # pdb.gimp_context_set_foreground((255, 255, 255))

    # #fill the background - black
    # pdb.gimp_drawable_fill(drw, gimpfu.BACKGROUND_FILL)

    # #to set the brush, check first for available brushes using  pdb.gimp_brushes_get_list("")
    # #Exanples of brush with width 3 is '1. Pixel', and with width 1, 'Pixel (1x1 square)'

    # #set brush to simple pixel (width: 1)
    # pdb.gimp_context_set_brush('Circle (01)')

    # #draw a square around the image
    # ctrlPoints = [RADIO, RADIO, SIZE_W-RADIO, RADIO, SIZE_W-RADIO, 
    #             SIZE_W-RADIO, RADIO, SIZE_W-RADIO, RADIO, RADIO]
    # pdb.gimp_paintbrush_default(drw,len(ctrlPoints),ctrlPoints)

    # #now we draw 9 transparent circles (3 rows x 3 columns)
    # #a transparent circle means -with an alpha layer-, to select the area and cut it
    # for x in (0, SIZE_W/2-RADIO, SIZE_W-2*RADIO):
    #     for y in (0, SIZE_W/2-RADIO, SIZE_W-2*RADIO):
    #         #next call was available on 2.6, not on 2.8
    #         #pdb.gimp_image_select_ellipse(img, gimpfu.CHANNEL_OP_REPLACE, 
    #         #                              x, y, RADIO*2, RADIO*2)
    #         pdb.gimp_ellipse_select(img, x, y, RADIO*2, RADIO*2, 
    #                                 gimpfu.CHANNEL_OP_REPLACE, True, False, 0)
    #         pdb.gimp_edit_cut(drw)

    # #remove any selection
    pdb.gimp_selection_none(img)

    #and display the image
    pdb.gimp_display_new(img)


def get_visible(parent, outputList):
    for layer in parent.layers:
        if pdb.gimp_layer_get_visible(layer):
            outputList.append(layer)
            if pdb.gimp_item_is_group(layer):
                get_visible(layer, outputList)


register(
        "python_fu_message",
        "Show message",
        "Show message",
        "Pin-Chou Liu",
        "Pin-Chou Liu",
        "2019",
        "<Image>/MyFunctions/DrawSomething",
        "",
        [ (PF_STRING, "DataFile", "DataFile", "/Users/cliffordmeeks/dev/csup-scoreboard/data/image.json"),
        ],
        [],
        do_stuff)

main()