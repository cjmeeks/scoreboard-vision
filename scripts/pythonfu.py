import gimpfu #access constants



#!/usr/bin/env python

# GIMP Python plug-in template.


def do_stuff(img, layer, howmuch) :
    SIZE=240
    RADIO=24

    #create the image
    img=pdb.gimp_image_new(SIZE, SIZE, gimpfu.RGB)

    #add layer with 100% of opacity
    layer=pdb.gimp_layer_new(img, SIZE, SIZE, gimpfu.RGB_IMAGE, "base", 100, gimpfu.NORMAL_MODE)
    pdb.gimp_image_add_layer(img, layer, 0)

    #we need it with alpha channel
    pdb.gimp_layer_add_alpha(layer)

    #access its drawable
    drw = pdb.gimp_image_active_drawable(img)

    #set background to black, and foreground to white
    pdb.gimp_context_set_background((0,0,0))
    pdb.gimp_context_set_foreground((255, 255, 255))

    #fill the background - black
    pdb.gimp_drawable_fill(drw, gimpfu.BACKGROUND_FILL)

    #to set the brush, check first for available brushes using  pdb.gimp_brushes_get_list("")
    #Exanples of brush with width 3 is '1. Pixel', and with width 1, 'Pixel (1x1 square)'

    #set brush to simple pixel (width: 1)
    pdb.gimp_context_set_brush('Circle (01)')

    #draw a square around the image
    ctrlPoints = [RADIO, RADIO, SIZE-RADIO, RADIO, SIZE-RADIO, 
                SIZE-RADIO, RADIO, SIZE-RADIO, RADIO, RADIO]
    pdb.gimp_paintbrush_default(drw,len(ctrlPoints),ctrlPoints)

    #now we draw 9 transparent circles (3 rows x 3 columns)
    #a transparent circle means -with an alpha layer-, to select the area and cut it
    for x in (0, SIZE/2-RADIO, SIZE-2*RADIO):
        for y in (0, SIZE/2-RADIO, SIZE-2*RADIO):
            #next call was available on 2.6, not on 2.8
            #pdb.gimp_image_select_ellipse(img, gimpfu.CHANNEL_OP_REPLACE, 
            #                              x, y, RADIO*2, RADIO*2)
            pdb.gimp_ellipse_select(img, x, y, RADIO*2, RADIO*2, 
                                    gimpfu.CHANNEL_OP_REPLACE, True, False, 0)
            pdb.gimp_edit_cut(drw)

    #remove any selection
    pdb.gimp_selection_none(img)

    #and display the image
    display=pdb.gimp_display_new(img)

register(
    "python_fu_do_stuff",
    "Do stuff",
    "Longer description of doing stuff",
    "Your Name",
    "Your Name",
    "2010",
    "Do Stuff...",
    "*",      # Alternately use RGB, RGB*, GRAY*, INDEXED etc.
    [
        (PF_INT, "howmuch", "How much stuff?", 50)
    ],
    [],
    do_stuff, menu="<Image>/Filters/Enhance")

main()