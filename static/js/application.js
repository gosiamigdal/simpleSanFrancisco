$(function() {
    $(".alert").alert();
    $(".plan-buttons .btn").click( function (event) {

        var cssClass = $(this).attr("class");
        cssClass = cssClass.split("button-")[1];

        $(".plan-buttons .btn").removeClass("toggled");
        $(this).addClass("toggled");
        
        $(".plan-categories").hide();
        $(this).parent().parent().children(".plan-categories").show();

    }); 

    $(".plan-categories .btn").click(function (event) {
        $(".plan-buttons .btn").removeClass("toggled");
        $(".plan-categories .btn").removeClass("toggled");
        $(this).addClass("toggled");
    });

    $(".turn_green").mousedown(function (event) {
        $(".turn_green").removeClass("mouse_down");
        $(this).addClass("mouse_down");
    });
    $(".turn_green").mouseout(function (event) {
        $(".turn_green").removeClass("mouse_down");
    });

    $(".logout").click(function (event) {
        console.log("logout!!");
        FB.logout();
    });
    function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}(document, 'script', 'twitter-wjs')
});



