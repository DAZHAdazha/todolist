$(document).ready(function () {

    function login(){
        console.log("here");
        if($("#name").val()!='' && $("#password").val()!=''){
            var path = '../login';
            $.post(path,{username: $("#name").val(), password: $("#password").val(),remember: $("#remember-me").is(":checked")},
            function(data){
                if(data == '1'){
                    alert("Log in successfully");
                    var href = "./user.html";
                    window.location.replace(href);
                }
                else{
                    alert("Wrong username of password, please try again.");
                }
            });  //post request {}内为传递的数据, function为请求成功运行的函数 重要！！！

        }
        else{
            alert("Some columns are empty or wrong, please try again.");
        }
    }
    
    $("#login-btn").click(login);
    $('#password').bind('keypress', function (event) {
        if (event.keyCode == "13") {
            login();
        }
    }); 
    $('#name').bind('keypress', function (event) {
        if (event.keyCode == "13") {
            login();
        }
    }); 
    
});


