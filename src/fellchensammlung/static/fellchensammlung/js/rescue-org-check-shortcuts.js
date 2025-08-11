function mark_checked(index) {
    document.getElementById('mark_checked_'+index).submit();
}

function open_information(index) {
    let link = document.getElementById('species_url_'+index+'_1');
    if (!link) {
        link = document.getElementById('rescue_org_website_'+index);
    }
    window.open(link.href);
}

Mousetrap.bind('c', function() { mark_checked(1); });

Mousetrap.bind('o', function() { open_information(1); });