function check(){
  var search = $("#search").val();
   if(search == null || search == ""){
　　　 return false;
    }
　　　　return true;
}

function addCheck(){
    var title = $("#title").val();
    var description = $("#description").val();
    if(title == null || title == "" || description == null || description == ""){
        return false;
    }
        alert("submit sucessfully!");
        return true;
}

$(document).ready(function () {
    var path = window.location.href.toString();
    // check whether search for nothing
    $("#search_btn").click(function(){
        var search = $("#search").val();
        if(search.length==0){
            alert("Please enter search keyword!");
        }
    });

    $("#submit-task").click(function(){
        var title = $("#title").val();
        var description = $("#description").val();
        if(title == null || title == "" || description == null || description == ""){
            alert("Please enter title and description!");
        }
    });
    


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
});