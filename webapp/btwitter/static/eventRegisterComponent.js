function registerGeneralButtonToggleEvents() {

    $('.btn-toggle').click(function() {

        $(this).find('.btn').toggleClass('active');

        if ($(this).find('.btn-primary').size()>0) {
            $(this).find('.btn').toggleClass('btn-primary');
        }
        if ($(this).find('.btn-danger').size()>0) {
            $(this).find('.btn').toggleClass('btn-danger');
        }
        if ($(this).find('.btn-success').size()>0) {
            $(this).find('.btn').toggleClass('btn-success');
        }
        if ($(this).find('.btn-info').size()>0) {
            $(this).find('.btn').toggleClass('btn-info');
        }

        $(this).find('.btn').toggleClass('btn-default');
    });
}

function registerAdvancedModeToggleButtonEvents() {
    $('#advanced_mode_on').add('#advanced_mode_off').click(function() {
        var mode = $(this).attr('id');

        //Slide menu up or down depending on the toggle state of the button
        if(mode == 'advanced_mode_on') {
            $('#advanced_control').hide().removeClass('hide').slideDown('fast')
        }
        else if(mode == 'advanced_mode_off') {
            $('#advanced_control').hide().addClass('hide').slideUp('fast')
        }
    });
}

function registerParameterEvents() {

    $('.btn.add').on('click', function () {
        if($('#keyword_form_second').length <= 0) {
            var id = 'keyword_form_second';

            $('.controls .form-control').clone().insertBefore($(this)).attr('id', id);
            $('#' + id).val('').css('margin-top', '5px');
            registerTypeaHeadWords(id);
        }
    });

    $('.btn.rem').on('click', function () {
        if($('#keyword_form_second').length >= 1) {
            $('#keyword_form_second').remove();
        }
    });

    $('#keyword_form_button').on('click',  function(){
        resend([])
    })

    $('#measures_form').on('change', function() { resend([]) });
    //$("#display_limit_form").add("#edge_weight_form").add("#overlap_limit_form").on('input', function() { resend([]) });

    //Events for the part of speech options, as well as for other options
    $('.c-opts[type=checkbox]').on('change', function() { resend([]) });
    $('.c-pos[type=checkbox]').on('change', function() { resend([]) });
    $('.control-group.data').on('input', 'input', function() { resend([]) });
}

function registerRemoveWordFromDiagramEvent() {
    $('#edit_save_button').click(function(){
        var allVals = [];
        $('#edit_modal input:checkbox').each(function() {
            if($(this).is(':checked')) {
                allVals.push($(this).attr('id'));
            }
        });
        resend(allVals);
    })
}

function registerTypeaHeadWords(id) {
    // instantiate the bloodhound suggestion engine
    var numbers = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        local:  ["gernot erler" , "florian pronold" , "eva hoegl" , "frank-walter steinmeier" , "carsten sieling" , "aydan oezoguz" , "michael roth" , "sonja steffen" , "sigmar gabriel" , "peer steinbrueck" , "andrea nahles" , "elke ferner" , "thomas jurk" , "christian schmidt" , "alexander dobrindt" , "burkhard lischka" , "barbara hendricks" , "ernst dieter rossmann" , "carsten schneider" , "wolfgang schaeuble" , "gerda gasselfeldt" , "monika gruetters" , "michael stuebgen" , "elisabeth motschmann" , "marcus weinberg" , "hans-peter friedrich" , "franz josef jung" , "angela merkel" , "ursula von der leyen" , "heiko maas" , "gerd mueller" , "hermann groehe" , "johanna wanka" , "manuela schwesig" , "norbert lammert" , "maria boehmer" , "peter altmaier" , "thomas de maizière" , "heike brehmer" , "ronald pofalla" , "volker bouffier" , "johann wadephul" , "manfred grund" , "jochim stoltenberg" , "rainer bruederle" , "christine lieberknecht" , "dirk niebel" , "sabine leutheusser-schnarrenberger" , "martin lindner" , "martin neumann" , "torsten staffeldt" , "burkhardt mueller-soenksen" , "joerg-uwe hahn" , "hagen reinhold" , "daniel bahr" , "philipp roesler" , "guido westerwelle" , "peter ramsauer" , "volker wissing" , "oliver luksic" , "jan muecke" , "cornelia pieper" , "wolfgang kubicki" , "patrick kurth" , "caren lay" , "nicole gohlke" , "michael schlecht" , "klaus ernst" , "gregor gysi" , "diana golze" , "agnes alpers" , "jan van aken" , "sabine leidig" , "dietmar bartsch" , "diether dehm" , "sahra wagenknecht" , "alexander ulrich" , "thomas lutze" , "katja kipping" , "petra sitte" , "cornelia moehring" , "kersten steinke" , "juergen trittin" , "kerstin andreae" , "claudia roth" , "renate kuenast" , "annalena baerbock" , "marieluise beck" , "anja hajduk" , "priska hinz" , "harald terpe" , "katja keul" , "baerbel hoehn" , "joachim gauck" , "tabea roeßner" , "markus tressel" , "monika lazar" , "steffi lemke" , "luise amtsberg" , "katrin goering-eckardt" , "horst seehofer" , "winfried kretschmann"]
    });

    // initialize the bloodhound suggestion engine
    numbers.initialize();

    $('#' + id).typeahead({
        items: 102,
        source:numbers.ttAdapter()
    });
}

function registerExamplePage() {
    $('.example').on('click', function() {
        $('#myTab a:first').tab('show');
    });
}