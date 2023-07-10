django.jQuery(function($) {
    $( "#id_marca" ).autocomplete({
        source: function( request, response ) {
            $.ajax({
                url: "https://vpic.nhtsa.dot.gov/api/vehicles/GetMakesForVehicleType/car?format=json",
                dataType: "json",
                data: {
                    term: request.term
                },
                success: function( data ) {
                    response( data.Results.map(function(item) {
                        return {
                            label: item.Make_Name,
                            value: item.Make_Name
                        };
                    }));
                }
            });
        },
        minLength: 2,
        select: function( event, ui ) {
            $( "#id_marca" ).val( ui.item.value );
        }
    });

    $( "#id_modelo" ).autocomplete({
        source: function( request, response ) {
            $.ajax({
                url: "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/make/" + $( "#id_marca" ).val() + "/modelyear/" + $( "#id_año" ).val() + "?format=json",
                dataType: "json",
                data: {
                    term: request.term
                },
                success: function( data ) {
                    response( data.Results.map(function(item) {
                        return {
                            label: item.Model_Name,
                            value: item.Model_Name
                        };
                    }));
                }
            });
        },
        minLength: 2,
        select: function( event, ui ) {
            $( "#id_modelo" ).val( ui.item.value );
        }
    });
});
