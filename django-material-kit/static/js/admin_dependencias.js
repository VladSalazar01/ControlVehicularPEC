document.addEventListener('DOMContentLoaded', function() {
    var inlines = document.querySelectorAll('.subcircuito-inline');
    inlines.forEach(function(inline) {
        var header = inline.querySelector('h2');
        var contents = inline.querySelector('.inline-related');
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            contents.style.display = contents.style.display == 'none' ? 'block' : 'none';
        });
        contents.style.display = 'none';
    });
});