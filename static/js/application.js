$(function() {
    $(".alert").alert();
    $(".plan-buttons .btn").click( function (event) {

        var cssClass = $(this).attr("class");
        cssClass = cssClass.split("button-")[1];
        //alert("Button clicked!" + cssClass); // TODO

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

    $(".turn_green").click(function (event) {
        $(".turn_green").removeClass("green");
        $(this).addClass("green");
    });
});
