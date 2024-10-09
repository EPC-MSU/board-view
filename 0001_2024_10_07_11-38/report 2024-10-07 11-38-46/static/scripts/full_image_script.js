var mouse_x, mouse_y;
document.addEventListener("mousemove", handle_mouse_move_event);


/**
 * Function changes position of image of IV-curve for pin.
 * @param pin_iv_img: image of IV-curve for pin.
 */
function change_position(pin_iv_img) {
    pin_iv_img.style.top = "60%";
}


/**
 * Function checks if mouse is inside image of IV-curve.
 * @param object: image of IV-curve.
 * @return: true if mouse is inside image of IV-curve.
 */
function check_point_inside(object) {
    const PERCENT = 0.2;
    let body = document.getElementsByTagName("body")[0];
    let body_width = body.getBoundingClientRect().width;
    let img_width = PERCENT * body_width;
    let img_height = object.naturalHeight * img_width / object.naturalWidth;
    if (0 <= mouse_x && mouse_x <= img_width && 0 <= mouse_y && mouse_y <= img_height)
        return true;
    return false;
}


/**
 * Function handles the mouse movement event.
 * @param event: mouse movement event.
 */
function handle_mouse_move_event(event) {
    mouse_x = event.clientX;
    mouse_y = event.clientY;
}


/**
 * Function hides or shows image of IV-curve for pin.
 * @param pin: area on big image of board that represents pin;
 * @param show: if false image is hidden.
 */
function hide_or_show_img(pin, show) {
    let coords = pin.getAttribute("coords");
    let pin_iv_img = document.getElementById("img" + coords);
    let board_x = document.getElementById("board_img").getBoundingClientRect().x;
    if (board_x < 0)
        board_x = 0;
    if (show) {
        if (check_point_inside(pin_iv_img))
            change_position(pin_iv_img);
        pin_iv_img.style.display = "block";
    }
    else {
        pin_iv_img.style.display = "none";
        pin_iv_img.style.top = "50px";
    }
}


window.onresize = function() {
    let imgs = document.getElementsByTagName("figure");
    for (let i = 0; i < imgs.length; i++) {
        let pin_iv_img = imgs[i];
        pin_iv_img.style.width = "20%";
    }
}
