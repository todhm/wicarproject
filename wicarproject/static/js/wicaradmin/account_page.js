$( function() {
     if(start_date && end_date){
         var startDateVar =new Date(start_date);
         var endDateVar=new Date(end_date);
     }
     else{
         var startDateVar="+1d"
         var endDateVar="+8d"
     }
     $("#start_date").datepicker({
         beforeShow: function() {
                setTimeout(function(){
                    $('.ui-datepicker').css('z-index', 99999999999999);
                }, 0);
            },

     }).datepicker("setDate",startDateVar);;

     $("#end_date").datepicker({
         beforeShow: function() {
                setTimeout(function(){
                    $('.ui-datepicker').css('z-index', 99999999999999);
                }, 0);
            }
        }).datepicker("setDate",endDateVar);
  } );
