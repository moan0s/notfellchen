# Notfellchen

[notfellchen.org](https://notfellchen.org) ist eine Sammelstelle für Tier-Vermittlungen. Die Idee entstand, da in der
deutschsprachigen Rattencommunity ein wilder Mix aus Websites, Foren und Facebookgruppen besteht die Ratten vermitteln.
Diese Website soll die bestehende Communities NICHT ersetzten, jedoch ermöglichen, dass Menschen die Ratten aufnehmen
wollen Informationen einfach finden und nicht bereits in jeder Gruppe sein müssen.

Wir nehmen Angebote auf die

* von Rattenhilfen
* Tierheimen
* oder Privatpersonen die ihre Haltung aufgeben wollen
  kommen. Letzteren empfehlen wir den Weg über eine Rattenhilfe, denn so ist die Vertrauensbasis größer.

Rattenhilfen mit denen gute Erfahrungen bestehen werden von uns als "geprüft" markiert.

Wir legen großen Wert darauf, dass hier kommerzielle Angebote keinen Platz haben, genauso nicht erlaubt ist die
Vermittlung von Ratten aus geplanten Vermehrungen oder aus Zooladenkäufen die schwanger wurden. Wir wollen Zooladenkäufe
in keinem Fall unterstützen und empfehlen hier den Weg über eine Rattenhilfe.

Auch seriöse Züchter\*innen können hier nicht vermitteln, das Angebot ist für Ratten, die sonst kein artgerechtes
Zuhause finden können.

# Developer Notes

Because of a wired bug the initial migrations must run two times as the first time the permissions
for `create_active_adoption_notice` are created but can not yet be accessed and on the second time this permission will
be added to groups.

## Docker

Build latest image

```
docker build . -t moanos/notfellchen:latest
```

```
docker run -p8000:7345 moanos/notfellchen:latest
```

## Geocoding

Geocoding services (search map data by name, address or postcode) are provided via the
[Nominatim](https://nominatim.org/) API, powered by [OpenStreetMap](https://openstreetmap.org) data. Notfellchen uses
a selfhosted Nominatim instance to avoid overburdening the publicly hosted instance. Due to ressource constraints
geocoding is only supported for Germany right now.

ToDos
* [ ] Implement a report that shows the number of location strings that could not be converted into a location
* [ ] Add a management command to re-query location strings to fill location