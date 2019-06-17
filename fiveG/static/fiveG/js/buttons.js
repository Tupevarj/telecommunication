
 $(document).on("submit", "#controlPanel", function (e) {
     e.preventDefault();
     $.ajax({
         type: $(this).attr("method"),
         url: $(this).attr("action"),
         data: $(this).serialize(),
         success: function (data) {
             $("#alertWarning").addClass("invisible");
             $("#alertSuccess").html(data);
             $("#alertSuccess").removeClass("invisible");
         },
         failure: function (data) {
             $("#alertSuccess").addClass("invisible");
             $("#alertWarning").html(data);
             $("#alertWarning").removeClass("invisible");
         }
     });
 });