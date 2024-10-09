var flag = false;


/**
 * Function changes size of board image and position of area pins on it.
 */
function change_size() {
    if (flag)
        return;

    flag = true;
    const WIDTH = 800;
    const board_images = ["board", "board_clear"]
    let natural_width = null;
    for (let i = 0; i < board_images.length; i++) {
        let board_image = board_images[i];
        natural_width = change_size_of_board_image(board_image, WIDTH);
    }

    if (natural_width == null)
        return;

    let pin_areas = document.getElementsByTagName("area");
    for (let i = 0; i < pin_areas.length; i++) {
        let pin = pin_areas[i];
        let coords = pin.getAttribute("coords").split(",");
        let x = coords[0] * WIDTH / natural_width;
        let y = coords[1] * WIDTH / natural_width;
        let r = coords[2] * WIDTH / natural_width / 5;
        pin.setAttribute("coords", x + "," + y + "," + r);
    }

    draw_pins();
}


/**
 * The function resizes the board image.
 * @param image_name: ID of the board image to be resized;
 * @param new_width: size to be specified.
 */
function change_size_of_board_image(image_name, new_width) {
    let board_img = document.getElementById(image_name);
    if (board_img == null)
        return null;

    let natural_width = board_img.naturalWidth;
    board_img.width = new_width;
    return natural_width;
}


/**
 * Function draws a pin on the board image in canvas.
 */
function draw_pins() {
    let board_img = document.getElementById("board_clear");
    let pin_canvases = document.getElementsByTagName("canvas");
    for (let i = 0; i < pin_canvases.length; i++) {
        let pin_canvas = pin_canvases[i];
        pin_canvas.height = PIN_IMAGE_SIZE;
        pin_canvas.width = PIN_IMAGE_SIZE;
        let context = pin_canvas.getContext("2d");
        let pin_data = pin_canvas.dataset.pinData.split(",");
        let pin_x = pin_data[0];
        let pin_y = pin_data[1];
        let pin_type = pin_data[2];
        let sx = pin_x - PIN_IMAGE_SIZE / 2;
        let sy = pin_y - PIN_IMAGE_SIZE / 2;
        context.drawImage(board_img, sx, sy, PIN_IMAGE_SIZE, PIN_IMAGE_SIZE, 0, 0, PIN_IMAGE_SIZE, PIN_IMAGE_SIZE);

        context.beginPath();
        context.lineWidth = 2;
        let center = PIN_IMAGE_SIZE / 2;
        context.arc(center, center, 4, 0, 2 * Math.PI, false);
        context.fillStyle = PIN_COLORS[pin_type];
        context.fill();
        context.strokeStyle = "#003300";
        context.stroke();
    }
}


/**
 * Function handles click on button.
 * @param button: button.
 */
function handle_click(button) {
    button.classList.toggle("active");
    let content = button.nextElementSibling;
    if (content.style.display === "block")
        content.style.display = "none";
    else
        content.style.display = "block";
}
