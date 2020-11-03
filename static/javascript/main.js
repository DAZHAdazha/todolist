$(document).ready(function () {
    var path = window.location.href.toString();

    // center the modal 
    var $modal_btn = $('#modalBtn');
    var $modal = $('#myModal');
    $modal_btn.on('click', function () {
        $modal.modal({
            backdrop: 'static'
        });
    });
    $modal.on('show.bs.modal', function () {
        var $this = $(this);
        var $modal_dialog = $this.find('.modal-dialog');
        $this.css('display', 'block');
        $modal_dialog.css({
            'margin-top': Math.max(0, ($(window).height() - $modal_dialog.height()) / 2)
        });
    });
    //log in validator
    function log_in(){
        var input_username = $("#input-username").val();
        var input_password = $("#input-password").val();
        var input_remember = $("#remember-me").is(":checked");

        var path = '/login';

        $.post(path,{username: input_username, password: input_password,remember: input_remember},
            function(data){
                if(data == '1'){
                     alert("Login successfully!");
                    var current_path = window.location.href.toString();
                    if(current_path.split('/')[3] != ''){
                            var href = "./" + "user.html";
                            window.location.replace(href);
                    }
                    else{
                        var href = "./HTML/" + "user.html";
                            window.location.replace(href);
                    }
                }
                else if(data == '2'){
                    alert("Wrong password!");
                }
                else if(data == '0'){
                    alert("Account is not existed!");
                }
            });  //post request {}内为传递的数据, function为请求成功运行的函数 重要！！！
    }

    $("#login").click(log_in);
    $('#input-password').bind('keypress', function (event) {
        if (event.keyCode == "13") {
            log_in();
        }
    }); 
    $('#input-username').bind('keypress', function (event) {
        if (event.keyCode == "13") {
            log_in();
        }
    }); 
    //responsive web for phones and tablets
    function size() {
        var width = $(window).width();
        if (width <= 991) {
            $(".col-md-2.responsive").each(function () {
                $(this).removeClass("col-md-2");
                $(this).addClass("col-md-6");
            });
        } else {
            $(".col-md-6.responsive").each(function () {
                $(this).removeClass("col-md-6");
                $(this).addClass("col-md-2");
            });
        }
    }
    size();
    window.onresize = size;

    //post
 
    var path_split = path.split("/");
    var path_split_length = path_split.length;
    var current = path_split[path_split_length - 1].replace(".html", "");
    current_star = current + "_star";

    
    $(".star").click(function () {
        $.post(path);  //post request
    });

    /*
    //star
    var path_split = path.split("/");
    var path_split_length = path_split.length;
    var current = path_split[path_split_length - 1].replace(".html", "");
    current_star = current + "_star";
    function star_toggle() {
        if (!localStorage.getItem(current_star) && localStorage.getItem(current_star) != 0) {
            localStorage.setItem(current_star, 1);
        } else {
            if (localStorage.getItem(current_star) == 1) {
                localStorage.setItem(current_star, 0);
            } else {
                localStorage.setItem(current_star, 1);
            }
        }
    }

    function check_status() {
        if (localStorage.getItem(current_star) == 1) {
            $(".star").attr("src", "../static/star.png");
        } else {
            $(".star").attr("src", "../static/unstar.png");
        }
    }
    check_status();
    $(".star").click(function () {
        star_toggle();
        check_status();
    });
    */
    //add to cart
    current_cart = current + "_cart";
    function cart_add(){
        localStorage.setItem(current_cart, 1);
    }
    function cart_remove(){
        localStorage.setItem(current_cart, 0);
    }
    $("#add_cart").click(function(){
        cart_add();
        alert("You had added the product to cart successfully!");
    });
    $("#remove_cart").click(function(){
        cart_remove();
        alert("You had removed the product to cart successfully!");
    });
});