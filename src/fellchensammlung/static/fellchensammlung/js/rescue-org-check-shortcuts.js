function mark_checked(index) {
    document.getElementById('mark_checked_'+index).submit();
}

Mousetrap.bind('c', function() { mark_checked(1); });
