function ifdef(variable, prefix = "", suffix = "") {
    if (variable !== undefined) {
        return prefix + variable + suffix;
    } else {
        return "";
    }
}

function geojson_to_summary(location) {
    if (ifdef(location.properties.name) !== "") {
        return location.properties.name + ifdef(location.properties.city, " (", ")");
    } else {
        return ifdef(location.properties.street, "", ifdef(location.properties.housenumber, " ",""))  + ifdef(location.properties.city, ", ", "") + ifdef(location.properties.countrycode, ", ", "")
    }

}

function geojson_to_searchable_string(location) {
    return ifdef(location.properties.name, "", ", ") + ifdef(location.properties.street, "", ifdef(location.properties.housenumber, " ",", ")) + ifdef(location.properties.city, "", ", ") + ifdef(location.properties.country, "", "")
}

function truncate(str, n, url){
  return (str.length > n) ? str.slice(0, n-1) + '<a href="' + url + '">&hellip;</a>' : str;
};
