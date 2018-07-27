$( function() {
    $("#js-searchFormExpandedStartDate").datepicker({
        
        minDate:0
        });
    $("#js-searchFormExpandedStartDate[value='']").datepicker("setDate", "+1d");
    $( "#js-searchFormExpandedStartDate" ).datepicker( "option", "defaultDate", +1 );
    $("#js-searchFormExpandedEndDate").datepicker({minDate:0});

  } );
