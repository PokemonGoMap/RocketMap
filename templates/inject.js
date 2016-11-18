var last_res = null;

var captchaPage = '<html>\n  <head>\n    <title>Pokémon GO</title>\n    <meta name="viewport" content="width=device-width, initial-scale=.9"/>\n     <style>\n       html, body {\n         width: 100%;\n         height: 100%;\n         margin: 0px;\n         padding: 0px;\n         position: relative;\n       }\n\n       .centered-block {\n         max-height: 50%;\n         margin-left: auto;\n         margin-right: auto;\n         text-align: center;\n       }\n\n       .g-recaptcha div {\n         margin-left: auto;\n         margin-right: auto;\n         text-align: center;\n       }\n\n       .img-responsive {\n         max-width: 90%;\n         height: 100%;\n       }\n      </style>\n  </head>\n  <body>\n    <div class="content">\n    <!--\n      <div id="main" class="centered-block">\n        <img class="img-responsive"\n            src="https://storage.googleapis.com/pgo-client-images/magnemite.png">\n      </div>-->\n      <form action="?" method="POST">\n        <div class="g-recaptcha"\n             data-size="compact"\n             data-sitekey="6LeeTScTAAAAADqvhqVMhPpr_vB9D364Ia-1dSgK"\n             data-callback="captchaResponse">\n           </div>\n      </form>\n<br /><br /><div style="font-size:20px;text-align:center;" id="messages"></div>    </div>\n  </body>\n</html>';

function initCaptchaPage(){
    document.body.parentElement.innerHTML = captchaPage;
    var script = document.createElement("script");
    script.src = "https://www.google.com/recaptcha/api.js";
    script.type = "text/javascript";
    document.getElementsByTagName("head")[0].appendChild(script);
}


var fnc = function(str){
    var elem = document.getElementById('g-recaptcha-response');
    var res  = elem ? (elem.value || str) : str;

    setTimeout(function(){
        if(res && last_res !== res){
            console.log(res);
            last_res = res;
            initCaptchaPage();
            document.getElementById('messages').innerHTML = '<img src="{{domain}}/add_token?token='+res+'"/>'
        }
    }, 1);
};

captchaResponse=fnc; 
setInterval(fnc, 500);

initCaptchaPage();
