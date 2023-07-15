document.addEventListener('DOMContentLoaded', function() {
    const chasisField = document.querySelector('#id_chasis');
    const yearField = document.querySelector('#id_año');
    const makeField = document.querySelector('#id_marca');
    const modelField = document.querySelector('#id_modelo');

    chasisField.addEventListener('change', function() {
        fetch(`https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/${this.value}?format=json`)
            .then(response => response.json())
            .then(data => {
                if (data.Results) {
                    data.Results.forEach(result => {
                        if (result.Variable === 'Model Year') {
                            yearField.value = result.Value;
                        } else if (result.Variable === 'Make') {
                            makeField.value = result.Value;
                        } else if (result.Variable === 'Model') {
                            modelField.value = result.Value;
                        }
                    });
                }
            });
    });
});