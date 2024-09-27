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

# Commands

Clean up empty locations by re-querying them

```shell
nf clean_locations
```

Populate the database with test data **DO NOT USE IN PRODUCTION**
```shell
nf populate_db
```

Query location data to debug
```shell
nf query_location <query>
```

# Texts

There is a system for customizing texts in Notfellchen. Not every change of a tet should mean an update of the software. But this should also not become a CMS.
Therefore, a solution is used where a number of predefined texts per site are supported. These markdown texts will then be included in the site, if defined.

| Textcode            | Location |
|---------------------|----------|
| `how_to`            | Index    |
| `introduction`      | Index    |
| `privacy_statement` | About    |
| `terms_of_service`  | About    |
| `imprint`           | About    |
| Any rule            | About    |

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
docker push moanos/notfellchen:latest
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
* [x] Add a management command to re-query location strings to fill location

## Maps

The map on the main homepage is powered by [Versatiles](https://versatiles.org), and rendered using [Maplibre](https://maplibre.org/).

## Translation

```zsh
nf makemessages -a
```

Use a program like `gtranslator` or `poedit` to start translations

## Permissions

| Action                              | Allowed for                         |
|-------------------------------------|-------------------------------------|
| Create adoption notice              | logged-in                           |
| Edit adoption notice                | User that created, Moderator, Admin |
| Edit animal                         | User that created, Moderator, Admin |
| Add animal/photo to adoption notice | User that created, Moderator, Admin |
