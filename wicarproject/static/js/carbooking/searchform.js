$( function() {
    //caches a jQuery object containing the header element
    var header = $(".fixed-search");
    $(window).scroll(function() {
        var scroll = $(window).scrollTop();
        if (scroll > 100) {
            header.addClass("fixed-search-bar");
        } else {
            header.removeClass("fixed-search-bar");
        }
    });
    $('#js-searchFormExpanded').on('keyup keypress', function(e) {
        var keyCode = e.keyCode || e.which;
        if (keyCode === 13&& !$("#address").val()) {
            e.preventDefault();
            return false;
        }
    });
    let selectedAddressName = "";
    $( "#js-searchFormExpandedLocationInput" ).autocomplete({
             source: function (request, response) {
               ($("#address").val() != request.term)?
               $.ajax({
                   url: queryUrl,
                   headers:{
                       'Content-Type': 'application/json',
                       'Accept': 'application/json',
                       withCredentials:true
                   },
                   data: JSON.stringify({ address: request.term }),
                   delay:400,
                   method:"POST",
                   dataType: 'json',
                   success: function (data) {
                       response(data.map(
                           function(obj){
                               var rObj = {};
                               rObj['label'] = obj.address;
                               rObj['value'] = obj;
                               return rObj;
                           }));
                   },
                   error: function () {
                       response([]);
                   }
               }):null;
           },
           minLength: 2 ,
           select: function(event, ui) {
               $("#js-searchFormExpandedLocationInput").val(ui.item.label);
               $("#address").val(ui.item.label);
               let addressObj = ui.item.value;
               if(addressObj.hasOwnProperty('pointX') && addressObj.hasOwnProperty('pointY')){
                   $("#pointX").val(addressObj.pointX);
                   $("#pointY").val(addressObj.pointY);
               }
               else{
                   $("#pointX").val("");
                   $("#pointY").val("");
               }

               selectedAddressName=ui.item.label;
               event.preventDefault();
               return false;
           },

          focus: function (event, ui) {
              $("#js-searchFormExpandedLocationInput").val(ui.item.label);
              $("#address").val(ui.item.label);
              let addressObj = ui.item.value;
              if(addressObj.hasOwnProperty('pointX') && addressObj.hasOwnProperty('pointY')){
                  $("#pointX").val(addressObj.pointX);
                  $("#pointY").val(addressObj.pointY);
              }
              else{
                  $("#pointX").val("");
                  $("#pointY").val("");
              }

              selectedAddressName=ui.item.label;
              event.preventDefault();
                  event.preventDefault();
              }

         });

     $("#js-searchFormExpandedLocationInput").keydown(function(event){
        if(event.keyCode == 13) {
            var pointX = $("#pointX").val()
          if($("#js-searchFormExpandedLocationInput").val().length==0) {
              event.preventDefault();
              return false;
          }
        }
     });
     if(start_date && end_date){
         var startDateVar =new Date(start_date);
         var endDateVar=new Date(end_date);
     }
     else{
         var startDateVar="+1d"
         var endDateVar="+8d"
     }
     $("#js-searchFormExpandedStartDate").datepicker({
         beforeShow: function() {
                setTimeout(function(){
                    $('.ui-datepicker').css('z-index', 99999999999999);
                }, 0);
            },
         minDate:0,
         maxDate:90,
     }).datepicker("setDate",startDateVar);;

     $("#js-searchFormExpandedEndDate").datepicker({
         minDate:0,
         maxDate:90,
         beforeShow: function() {
                setTimeout(function(){
                    $('.ui-datepicker').css('z-index', 99999999999999);
                }, 0);
            }
        }).datepicker("setDate",endDateVar);
  } );
