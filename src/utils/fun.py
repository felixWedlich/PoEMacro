import ahkpy



def gem_swap():
    GEMS_SWAP_SPEED = 1
    print("gem swap")
    ahkpy.wait_key_released("RButton")
    ahkpy.wait_key_released("LButton")

    with ahkpy.block_input():
        ahkpy.sleep(0.1)
        ahkpy.send("i")
        ahkpy.mouse_move(1731, 1090, relative_to="screen", speed=GEMS_SWAP_SPEED)
        ahkpy.sleep(0.1)
        ahkpy.mouse_press("left")
        ahkpy.mouse_release("left")
        ahkpy.mouse_move(2080, 175, relative_to="screen", speed=GEMS_SWAP_SPEED)
        ahkpy.sleep(0.1)
        ahkpy.mouse_press("left")
        ahkpy.mouse_release("left")
        ahkpy.mouse_move(1731, 1090, relative_to="screen", speed=GEMS_SWAP_SPEED)
        ahkpy.sleep(0.1)
        ahkpy.mouse_press("left")
        ahkpy.mouse_release("left")
        ahkpy.sleep(0.1)
        ahkpy.send("i")
        ahkpy.sleep(0.2)
