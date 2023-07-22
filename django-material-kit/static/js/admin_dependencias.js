document.addEventListener('DOMContentLoaded', function() {
    var inlines = Array.from(document.querySelectorAll('.subcircuito-inline'));
    inlines.forEach(function(inline) {
        var headers = inline.querySelectorAll('h2');
        headers.forEach(function(header) {
            var contents = Array.from(header.parentElement.querySelectorAll('.inline-related'));
            if (contents[0].querySelector('input').value) {  // Checks if the inline has data
                header.style.cursor = 'pointer';
                header.addEventListener('click', function() {
                    contents.forEach(function(content) {
                        content.style.display = content.style.display == 'none' ? 'block' : 'none';
                    });
                });
                contents.forEach(function(content) {
                    content.style.display = 'none';
                });
            }
        });
    });
});






