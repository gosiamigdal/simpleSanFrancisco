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


    // ...
    // val cssClass = $(".plan-buttons .toggled").attr("class");
    // cssClass = cssClass.split("button-")[1];
    // /select/2pm/dining
});