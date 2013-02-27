temps = []
powers = []
config = {}

mint = 999
maxt = 0

init = ->
    $.getJSON "/config", (data) ->
        config = data
        $('#food').html config["food"]
        $('#temp').html config["temp"] + "&deg;C"
        t = config["time"]
        hrs = Math.floor(t / 3600)
        mins = Math.floor((t % 3600) / 60)
        $('#time').html "#{hrs} hours and #{mins} minutes"
        window.setTimeout(get_data, 0)

get_data = ->
    $.getJSON "/data?since=#{temps.length}", (data) ->
        new_temps = (d[1] for d in data[0])
        new_max = Math.max.apply(Math, new_temps)
        new_min = Math.min.apply(Math, new_temps)
        maxt = new_max if new_max > maxt
        mint = new_min if new_min < mint
        temps = temps.concat(([d[0]*1000, d[1]] for d in data[0]))
        powers = powers.concat(([d[0]*1000, d[1]] for d in data[1]))
        render()
        window.setTimeout(get_data, 500)

render = ->
    $('#mintemp').html "#{mint.toFixed(2)}&deg;C"
    $('#maxtemp').html "#{maxt.toFixed(2)}&deg;C"
    $('#nowtemp').html "#{temps[temps.length - 1][1].toFixed(2)}&deg;C"

    $('#mintemp,#maxtemp,#nowtemp').css "color", "#5da423"

    if mint < 53.0
        $('#mintemp').css('color', '#c60f13')
    if temps[temps.length - 1][1] < 53.0
        $('#nowtemp').css('color', '#c60f13')
    
    start_time = temps[0][0]
    now_time = temps[temps.length - 1][0]
    elapsed = (now_time - start_time) / 1000
    remains = (config["time"] * 1000 - (now_time - start_time)) / 1000
    if remains < 0
        remains = 0
    elapsed_hrs = String("0"+Math.floor(elapsed / 3600)).slice(-2)
    elapsed_mns = String("0"+Math.floor((elapsed % 3600) / 60)).slice(-2)
    elapsed_scs = String("0"+Math.floor(elapsed % 60)).slice(-2)
    remains_hrs = String("0"+Math.floor(remains / 3600)).slice(-2)
    remains_mns = String("0"+Math.floor((remains % 3600) / 60)).slice(-2)
    remains_scs = String("0"+Math.floor(remains % 60)).slice(-2)
    $('#elapsedtime').html "#{elapsed_hrs}:#{elapsed_mns}:#{elapsed_scs}"
    $('#remainingtime').html "#{remains_hrs}:#{remains_mns}:#{remains_scs}"
    if remains <= 0
        $('#remainingtime').css('color', '#c60f13')
    render_flot()

render_flot = ->
    $.plot $("#flothere"), [
        {
            data: powers, label: "Power", yaxis: 2, color: "#2ba6cb",
            lines: {fill: true}
        } ,{
         data: temps, label: "Temperature", yaxis: 1, color: "#5da423",
         threshold: {below: 53.0, color: "#c60f13"}
        }
    ], {
        xaxis: {
            mode: "time"
        },
        yaxes: [
            {
                min: config["temp"]-5, max: config["temp"]+5,
                tickFormatter: (v, axis) ->
                    v.toFixed(axis.tickDecimals) + "°C"
            }, {
                min: 0, max: 100, position: "right",
                tickFormatter: (v, axis) ->
                    v.toFixed(axis.tickDecimals) + "%"
            }
        ],
        legend: {position: 'nw'}
    }

init()
