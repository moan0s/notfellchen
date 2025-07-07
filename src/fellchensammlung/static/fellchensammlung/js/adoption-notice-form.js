function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function () {
    // ------------------------------------------------ functions
    var show = function (elem) {
        // Get the natural height of the element
        var getHeight = function () {
            elem.style.display = 'block'; // Make it visible
            var height = elem.scrollHeight + 'px'; // Get its height
            elem.style.display = ''; //  Hide it again
            return height;
        };
        var height = getHeight(); // Get the natural height
        elem.classList.remove('closed');
        elem.classList.add('open'); // Make the element visible
        elem.setAttribute('aria-hidden', 'false');
        elem.style.height = height; // Update the max-height
        // Once the transition is complete, remove the inline max-height so the content can scale responsively
        window.setTimeout(function () {
            elem.style.height = '';
        }, 500);
    };

    var hide = function (elem) {
        // Give the element a height to change from
        elem.style.height = elem.scrollHeight + 'px';
        // Set the height back to 0
        window.setTimeout(function () {
            elem.style.height = '0';
        }, 1);
        // When the transition is complete, hide it
        window.setTimeout(function () {
            elem.classList.remove('open');
            elem.classList.add('closed');
            elem.setAttribute('aria-hidden', 'true');
        }, 500);
    };

    var toggle = function (elem, timing) {
        // If the element is visible, hide it
        if (elem.classList.contains('open')) {
            hide(elem);
            return;
        }
        // Otherwise, show it
        show(elem);
    };


    // ------------------------------------------------ build form
    let orig_form = document.querySelector('form');
    orig_form.style.display = 'none';

    let an_max = 6;

    let an_fieldset = document.createElement('fieldset');
    an_fieldset.classList.add('cell');
    let an_fieldset_legend = document.createElement('legend');
    an_fieldset_legend.innerHTML = "Allgemeines";
    an_fieldset.appendChild(an_fieldset_legend);

    let an_name = document.createElement('input');
    an_name.setAttribute('type', 'text');
    an_name.setAttribute('name', 'name');
    an_name.setAttribute('class', 'input');
    an_name.setAttribute('maxlength', 200);
    an_name.setAttribute('required', 'required');
    let an_name_label = document.createElement('label');
    an_name_label.setAttribute('class', 'label');
    an_name_label.innerHTML = 'Titel der Vermittlung';
    an_name_label.appendChild(an_name);

    let an_location_string = document.createElement('input');
    an_location_string.setAttribute('type', 'text');
    an_location_string.setAttribute('name', 'location_string');
    an_location_string.setAttribute('class', 'input');
    an_location_string.setAttribute('maxlength', 200);
    an_location_string.setAttribute('required', 'required');
    let an_location_string_label = document.createElement('label');
    an_location_string_label.setAttribute('class', 'label');
    an_location_string_label.innerHTML = 'Ortsangabe';
    an_location_string_label.appendChild(an_location_string);

    let an_further_information = document.createElement('input');
    an_further_information.setAttribute('type', 'url');
    an_further_information.setAttribute('name', 'further_information');
    an_further_information.setAttribute('class', 'input');
    an_further_information.setAttribute('maxlength', 200);
    let an_further_information_label = document.createElement('label');
    an_further_information_label.setAttribute('class', 'label');
    an_further_information_label.innerHTML = 'Link zu mehr Informationen';
    an_further_information_label.appendChild(an_further_information);

    let an_species = document.createElement('select');
    let an_species_rat = document.createElement('option');
    an_species_rat.value = 1;
    an_species_rat.innerHTML = "Farbratte";
    an_species.appendChild(an_species_rat);
    an_species.setAttribute('name', 'species');
    an_species.setAttribute('class', 'input');
    an_species.setAttribute('required', 'required');
    let an_species_label = document.createElement('label');
    an_species_label.setAttribute('class', 'label');
    an_species_label.innerHTML = 'Tierart';
    an_species_label.appendChild(an_species);

    let an_number = document.createElement('input');
    an_number.setAttribute('type', 'number');
    an_number.setAttribute('name', 'number');
    an_number.setAttribute('class', 'input');
    an_number.setAttribute('min', 1);
    an_number.setAttribute('max', an_max);
    an_number.setAttribute('required', 'required');
    let an_number_label = document.createElement('label');
    an_number_label.setAttribute('class', 'label');
    an_number_label.innerHTML = 'Anzahl Tiere';
    an_number_label.appendChild(an_number);

    let an_dateofbirth = document.createElement('input');
    an_dateofbirth.setAttribute('type', 'date');
    an_dateofbirth.setAttribute('name', 'dateofbirth');
    an_dateofbirth.setAttribute('class', 'input');
    an_dateofbirth.setAttribute('maxlength', 200);
    an_dateofbirth.setAttribute('required', 'required');
    let an_dateofbirth_label = document.createElement('label');
    an_dateofbirth_label.setAttribute('class', 'label');
    an_dateofbirth_label.innerHTML = 'Geburtsdatum';
    an_dateofbirth_label.appendChild(an_dateofbirth);

    let an_sex = document.createElement('select');
    let an_sex_F = document.createElement('option');
    an_sex_F.value = 'F';
    an_sex_F.innerHTML = "Weiblich";
    an_sex.appendChild(an_sex_F);
    let an_sex_M = document.createElement('option');
    an_sex_M.value = 'M';
    an_sex_M.innerHTML = "Männlich";
    an_sex.appendChild(an_sex_M);
    let an_sex_F_N = document.createElement('option');
    an_sex_F_N.value = 'F_N';
    an_sex_F_N.innerHTML = "Weiblich, kastriert";
    an_sex.appendChild(an_sex_F_N);
    let an_sex_M_N = document.createElement('option');
    an_sex_M_N.value = 'M_N';
    an_sex_M_N.innerHTML = "Männlich, kastriert";
    an_sex.appendChild(an_sex_M_N);
    let an_sex_I = document.createElement('option');
    an_sex_I.value = 'I';
    an_sex_I.innerHTML = "Intergeschlechtlich";
    an_sex.appendChild(an_sex_I);
    an_sex.setAttribute('name', 'sex');
    an_sex.setAttribute('class', 'input');
    an_sex.setAttribute('required', 'required');
    let an_sex_label = document.createElement('label');
    an_sex_label.setAttribute('class', 'label');
    an_sex_label.innerHTML = 'Geschlecht';
    an_sex_label.appendChild(an_sex);

    let an_searching_since = document.createElement('input');
    an_searching_since.setAttribute('type', 'date');
    an_searching_since.setAttribute('name', 'searching_since');
    an_searching_since.setAttribute('class', 'input');
    an_searching_since.setAttribute('maxlength', 200);
    an_searching_since.setAttribute('required', 'required');
    let an_searching_since_label = document.createElement('label');
    an_searching_since_label.setAttribute('class', 'label');
    an_searching_since_label.innerHTML = 'neues Zuhause gesucht seit';
    an_searching_since_label.appendChild(an_searching_since);

    let an_group_only = document.createElement('select');
    let an_group_only_yes = document.createElement('option');
    an_group_only_yes.value = 1;
    an_group_only_yes.innerHTML = "nur zusammen";
    let an_group_only_no = document.createElement('option');
    an_group_only_no.value = 0;
    an_group_only_no.innerHTML = "auch einzeln";
    an_group_only.appendChild(an_group_only_yes);
    an_group_only.appendChild(an_group_only_no);
    an_group_only.setAttribute('name', 'group_only');
    an_group_only.setAttribute('class', 'input');
    an_group_only.setAttribute('required', 'required');
    let an_group_only_label = document.createElement('label');
    an_group_only_label.setAttribute('class', 'label');
    an_group_only_label.innerHTML = 'Gruppenvermittlung';
    an_group_only_label.appendChild(an_group_only);


    let animals = document.createElement('fieldset');
    animals.classList.add('cell', 'is-col-span-2');
    let animals_legend = document.createElement('legend');
    animals_legend.innerHTML = 'Angaben zu den Tieren';
    animals.appendChild(animals_legend);
    let noteNumber = document.createElement('p');
    noteNumber.setAttribute('id', 'noteNumber');
    noteNumber.innerHTML = 'Bitte Anzahl Tiere angeben';
    animals.appendChild(noteNumber);

    let an_description = document.createElement('textarea');
    an_description.setAttribute('name', 'an_description');
    an_description.classList.add('input', 'textarea');
    let an_description_label = document.createElement('label');
    an_description_label.innerHTML = 'Beschreibung der Gruppe';
    an_description_label.classList.add('label');
    an_description_label.appendChild(an_description);
    animals.appendChild(an_group_only_label);
    animals.appendChild(an_description_label);

    for (let i = 0; i < an_max; i++) {
        let an_fieldset_$i = document.createElement('fieldset');
        an_fieldset_$i.classList.add('animal-' + i, 'animal');
        an_fieldset_$i.appendChild(document.createElement('legend'));
        an_fieldset_$i.querySelector('legend').innerHTML = 'Tier ' + parseInt(i + 1);
        let an_name_$i = document.createElement('input');
        an_name_$i.setAttribute('type', 'text');
        an_name_$i.setAttribute('name', 'name-' + i);
        an_name_$i.setAttribute('class', 'input');
        an_name_$i.setAttribute('maxlength', 200);
        an_name_$i.setAttribute('required', 'required');
        let an_name_$i_label = document.createElement('label');
        an_name_$i_label.setAttribute('class', 'label');
        an_name_$i_label.innerHTML = 'Name';
        an_name_$i_label.appendChild(an_name_$i);

        let an_dateofbirth_$i = document.createElement('input');
        an_dateofbirth_$i.setAttribute('type', 'date');
        an_dateofbirth_$i.setAttribute('name', 'dateofbirth');
        an_dateofbirth_$i.setAttribute('class', 'input');
        an_dateofbirth_$i.setAttribute('maxlength', 200);
        an_dateofbirth_$i.setAttribute('required', 'required');
        let an_dateofbirth_$i_label = document.createElement('label');
        an_dateofbirth_$i_label.setAttribute('class', 'label');
        an_dateofbirth_$i_label.innerHTML = 'Geburtsdatum';
        an_dateofbirth_$i_label.appendChild(an_dateofbirth_$i);

        let an_sex_$i = document.createElement('select');
        let an_sex_F = document.createElement('option');
        an_sex_F.value = 'F';
        an_sex_F.innerHTML = "Weiblich";
        an_sex_$i.appendChild(an_sex_F);
        let an_sex_M = document.createElement('option');
        an_sex_M.value = 'M';
        an_sex_M.innerHTML = "Männlich";
        an_sex_$i.appendChild(an_sex_M);
        let an_sex_F_N = document.createElement('option');
        an_sex_F_N.value = 'F_N';
        an_sex_F_N.innerHTML = "Weiblich, kastriert";
        an_sex_$i.appendChild(an_sex_F_N);
        let an_sex_M_N = document.createElement('option');
        an_sex_M_N.value = 'M_N';
        an_sex_M_N.innerHTML = "Männlich, kastriert";
        an_sex_$i.appendChild(an_sex_M_N);
        let an_sex_I = document.createElement('option');
        an_sex_I.value = 'I';
        an_sex_I.innerHTML = "Intergeschlechtlich";
        an_sex_$i.appendChild(an_sex_I);
        an_sex_$i.setAttribute('name', 'sex');
        an_sex_$i.setAttribute('class', 'input');
        an_sex_$i.setAttribute('required', 'required');
        let an_sex_$i_label = document.createElement('label');
        an_sex_$i_label.setAttribute('class', 'label');
        an_sex_$i_label.innerHTML = 'Geschlecht';
        an_sex_$i_label.appendChild(an_sex_$i);

        let an_description_$i = document.createElement('textarea');
        an_description_$i.setAttribute('name', 'an_description');
        an_description_$i.classList.add('input', 'textarea');
        let an_description_$i_label = document.createElement('label');
        an_description_$i_label.innerHTML = 'Beschreibung';
        an_description_$i_label.classList.add('label');
        an_description_$i_label.appendChild(an_description_$i);

        an_fieldset_$i.appendChild(an_description_$i_label);
        an_fieldset_$i.appendChild(an_name_$i_label);
        an_fieldset_$i.appendChild(an_dateofbirth_$i_label);
        an_fieldset_$i.appendChild(an_sex_$i_label);
        an_fieldset_$i.appendChild(an_description_$i_label);
        animals.appendChild(an_fieldset_$i);
    }


    an_fieldset.appendChild(an_name_label);
    an_fieldset.appendChild(an_location_string_label);
    an_fieldset.appendChild(an_further_information_label);
    an_fieldset.appendChild(an_species_label);
    an_fieldset.appendChild(an_number_label);
    an_fieldset.appendChild(an_dateofbirth_label);
    an_fieldset.appendChild(an_sex_label);
    an_fieldset.appendChild(an_searching_since_label);

    let new_form = document.createElement('form');
    new_form.classList.add('new-animal-ad', 'fixed-grid', 'has-3-cols', 'has-1-cols-mobile');
    let div = document.createElement('div');
    div.classList.add('grid');
    let sButton = document.createElement('button');
    sButton.classList.add('button');
    sButton.innerHTML = "Abschicken";

    div.appendChild(an_fieldset);
    div.appendChild(animals);
    div.appendChild(sButton);
    new_form.appendChild(div);
    document.querySelector('.main-content').appendChild(new_form);

    // ------------------------------------------------ listeners
    // number of animals
    let tmpAnimal;
    an_number.addEventListener('change', function () {
        if (an_number.value > 0) {
            hide(noteNumber);
        } else {
            show(noteNumber);
        }
        if (an_number.value < 2) {
            hide(an_description_label);
            hide(an_group_only_label);
            an_group_only.selectedIndex = 1;
        } else {
            show(an_description_label);
            show(an_group_only_label);
            an_group_only.selectedIndex = 0;
        }
        for (let i = 0; i < an_max; i++) {
            tmpAnimal = document.querySelector('.animal-' + i);
            if (i < an_number.value) {
                tmpAnimal.removeAttribute('disabled');
                show(tmpAnimal);
            } else {
                tmpAnimal.setAttribute('disabled', 'true');
                hide(tmpAnimal);
            }
        }
    });

    // sex
    an_sex.addEventListener('change', function () {
        for (let i = 0; i < an_max; i++) {
            let selList = document.querySelector('.animal-' + i).querySelector('[name="sex"]');
            for (let j = 0; j < selList.options.length; j++) {
                if (selList.options[j].value == an_sex.value) {
                    selList.selectedIndex = j;
                    break;
                }
            }
        }
    });

    // date of birth
    an_dateofbirth.addEventListener('change', function () {
        for (let i = 0; i < an_max; i++) {
            document.querySelector('.animal-' + i).querySelector('[name="dateofbirth"]').value = an_dateofbirth.value;
        }
    });

    // ------------------------------------------------ initialise
    show(noteNumber);
    hide(an_description_label);
    hide(an_group_only_label);
    for (let i = 0; i < an_max; i++) {
        hide(document.querySelector('.animal-' + i));
    }

    // ---------------------------------------------------- submit
    new_form.addEventListener('submit', function (event) {
        event.preventDefault();
        let date = new Date();
        let postDate = date.toISOString().slice(0, 10);
        const path = '';

        let elResultsBd = document.createElement('div');
        elResultsBd.classList.add('feedback-backdrop');
        let elResults = document.createElement('div');
        elResults.classList.add('feedback-add-new');
        elResultsBd.appendChild(elResults);
        document.querySelector('body').appendChild(elResultsBd);

        let data = JSON.stringify({
            "created_at": postDate,
            "searching_since": an_searching_since.value,
            "name": an_name.value,
            "description": an_description.value,
            "further_information": an_further_information.value,
            "group_only": an_group_only.value,
            "location_string": an_location_string.value,
        });

        async function submitAN() {
            const csrftoken = getCookie('csrftoken');
            let response = await fetch('http://localhost:8000/api/adoption_notice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json;charset=utf-8',
                    'X-CSRFToken': csrftoken,
                },
                body: data,
            });
            console.log(response.status);
            if (response.status === 201) {
                let result = await response.json();
                elResults.textContent = result.message + '<br>neue Id: ' + result.id;
                elResults.classList.add('success');
            } else {
                elResults.textContent = 'Fehler! Status Code: ' + response.status;
                elResults.classList.add('error');
            }
        }

        submitAN();
    });
});
