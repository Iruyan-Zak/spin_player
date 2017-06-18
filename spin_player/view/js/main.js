/**
 * Copyright (c) 2017, Iruyan_Zak.
 * License: MIT (see LICENSE for details)
 */

$("#icon").click(function () {
    $(this).toggleClass('fa-spin');
    player = document.getElementById("player");
    if ($(this).hasClass('fa-spin')) {
        player.play();
    } else {
        player.pause();
    }
});

function transit() {
    screen_name = $('#screen-name').val();
    source_url = $('#sound-source').val();

    source_url = source_url.replace(/(.*)watch\?v=/, '');
    source_url = source_url.replace(/(.*)youtu\.be\//, '');

    location.href = '/' + screen_name + '/' + source_url;
}
