function resend(exclude) {
    var pos = {}, opts = {};

    //Part of speech checkboxes
    $('.c-pos').each(function() {
        var $this = $(this);
        pos[$this.attr('id').replace('c-', '')] = $this.is(":checked");
    });

    //Other options
    $('.c-opts').each(function() {
        var $this = $(this);
        opts[$this.attr('id').replace('c-', '')] = $this.is(":checked");
    });

    //TODO: Maybe save in dict as configParameter or something
    var keywords = []
    keywords.push($('#keyword_form_first').val());
    if($('#keyword_form_second').length > 0)
        keywords.push($('#keyword_form_second').val());

    var measure = $('#measures_form').val();
	var edge_weight = $('#edge_weight_form').val();
    var freq_a = $('#frequency_word_a_form').val();
    var freq_b = $('#frequency_word_b_form').val();
    var freq_ab = $('#frequency_word_ab_form').val();
    var overlap_limit = $('#overlap_limit_form').val();
	var limit = $('#display_limit_form').val();

    //Init value if resend is called without a parameter
    if(typeof exclude == 'undefined')
        exclude = []

    $.ajax({
        url: '/generate_chart',
        type: 'POST',
        data: {
            keywords: JSON.stringify(keywords),
            measure: measure,
            limit: limit,
            overlap_limit: overlap_limit,
			edge_weight: edge_weight,
            freq_a: freq_a,
            freq_b: freq_b,
            freq_ab: freq_ab,
            exclude: JSON.stringify(exclude),
            pos: JSON.stringify(pos),
            opts: JSON.stringify(opts)
        },
        headers: {
          Accept : "application/json"
        },
        dataType: 'json',
        traditional: true
    }).done(function (data) {
        $(document).ready(function() {
            renderChart(data);
        });

        //Delete only if nothing is excluded
        if(!data.exclude)
            $('.table-row').remove();

        var counter = 1;
        data.labels.forEach(function(name) {
            $('#edit_table').append('<tr class="table-row"> <td>' + counter + '</td> <td>' + name + '</td><td> <input type="checkbox" id="'+ name + '"> </td> </tr>');
            counter++;
        })

        $('.nav a').css({color: ''});
    }).fail(function () {
        $('.nav a').css({color: 'red'});
    });
}


function renderChart(data) {
    var chart = new Highcharts.Chart({
                //For thesis exports use 500 height sonst 800
                chart: { type: 'column', height: 500, zoomType: 'x', renderTo: 'graph' },
                title: data.title,
                xAxis: { "categories": data.labels, "labels": { "rotation": -45, "align": 'right', "style": {"fontSize": '13px', "fontFamily": 'Verdana, sans-serif'}}},
                yAxis: data.yAxis,
                series: data.series,
                plotOptions:  {
                    series: {
                        stacking: "normal", cursor: 'pointer', point: {
                            events: { click: function() { renderContext(this.category, this.series.name) }}
                        }
                    }
                },
                credits: { enabled: false },
                tooltip: {
                    //Maybe move to extra function
                    formatter: function() {
                        return '<span style="font-size:16px">' + this.x + '</span>' +
                                '<br>Likelihood Wert: <b>'+ Highcharts.numberFormat(Math.abs(this.point.org_y), 0) +
                                '</b><br>Kantengewicht: <b>' + data.info[this.series.name][this.x][1]['edge_weight'] +
                                '</b><br>Wortfrequenz: <b>' + data.info[this.series.name][this.x][0]['freq']  +
                                '</b><br>Wortklasse: <b>' + data.info[this.series.name][this.x][0]['word_class'] +
                                '</b><br>Namensentität: <b>' + data.info[this.series.name][this.x][0]['name_entity'] + '</b>';
                    }
                }
    });
}


function renderContext(cooccurrence, keyword) {
    var code = '<div class="progress progress-striped active"><div class="progress-bar"  role="progressbar" aria-valuenow="80" aria-valuemin="0" aria-valuemax="100" style="width: 80%"><span class="sr-only">80% Complete</span></div></div><div align="center"> (Loading... May take some time) </div>'
    $("#context_modal_header").text('Loading...')
    $("#panel_body_context").html(code)
    $("#context_modal").modal('show');

    $.ajax({
        url:  '/get_context',
        type: 'POST',
        data: {
            keyword:  JSON.stringify(keyword),
            cooccurrence: cooccurrence
        },
        dataType: 'json',
        traditional: true
    }).done(function (data) {
        var tweets = data.tweets;
        var index = 1

       $('#context_modal_header').html('Relation( { ' + keyword + ' } , ' + cooccurrence + ' )');

       function set_content(pos) {
           $('#panel_title_context').html('Context <span class="label label-warning pull-right"> Anzahl: ' + pos + ' / ' + tweets.length + '</span>');
           $('#panel_body_context').html('<blockquote><p>' + tweets[pos-1] + '</p></blockquote>');
       }

       set_content(index)

       $('#next_tweet_button').click(function() {
           console.log(index)
           console.log(tweets.length)
           if(index >= tweets.length) return;
           index += 1;
           set_content(index)
       });

    }).fail(function () {
        $('.nav a').css({color: 'red'});
    });
}


$(function () {
    $('#learn_more_button').click(function() {
        $('a[href=#main]').tab('show');
    })

    registerTypeaHeadWords('keyword_form_first');
    registerRemoveWordFromDiagramEvent();
    registerParameterEvents();
    registerGeneralButtonToggleEvents();
    registerAdvancedModeToggleButtonEvents();
});
