function compileHistory(data) {
  document.getElementById("history-pkmn-label").innerHTML = "Pokémons";

  var pkmnCount = []
  var pkmnTotal = 0

    $.each(data.pokemons, function(key, value) {

      pkmnCount[value['pokemon_id']] = {
        "ID": value['pokemon_id'],
        "Count": value['count'],
        "Name": value['pokemon_name'] + '(' + value['pokemon_rarity'] + ')'
      }
      pkmnTotal = pkmnTotal + value['count']
    })
    pkmnCount.sort(sort_by('Count', false))

      var pkmnListString = "<table><thead><tr><th>Icon</th><th>Name</th><th>Count</th><th>%</th></tr></thead><tbody><tr><td></td><td>Total</td><td>" + pkmnTotal + "</td><td></td></tr>"
      for (var i = 0; i < pkmnCount.length; i++) {
        if (pkmnCount[i] != null && pkmnCount[i].Count > 0) {
          pkmnListString += "<tr><td><img src=\"/static/icons/" + pkmnCount[i].ID + ".png\" /></td><td><a href='http://www.pokemon.com/us/pokedex/" + pkmnCount[i].ID + "' target='_blank' title='View in Pokedex' style=\"color: black;\">" + pkmnCount[i].Name + "</a></td><td>" + pkmnCount[i].Count + "</td><td>" + Math.round(pkmnCount[i].Count * 100 / pkmnTotal * 10) / 10 + "%</td></tr>"
        }
      }
      pkmnListString += "</tbody></table>"
      document.getElementById("historyList").innerHTML = pkmnListString

  
}

var sort_by = function(field, reverse, primer) {
  var key = primer
    ? function(x) {
      return primer(x[field])
    }
    : function(x) {
      return x[field]
    }

  reverse = !reverse ? 1 : -1

  return function(a, b) {
    return a = key(a), b = key(b), reverse * ((a > b) - (b > a))
  }
}
