Vermittlungen
=============

Vermittlungen können von allen Nutzer\*innen mit Account erstellt werden. Vermittlungen normaler Nutzer*innen kommen dann in eine Warteschlange und werden vom Admin & Modertionsteam geprüft und sichtbar geschaltet.
Tierheime und Pflegestellen können auf Anfrage einen Koordinations-Status bekommen, wodurch sie Vermittlungsanzeigen erstellen können die direkt öffentlich sichtbar sind.

Jede Vermittlung hat ein "Zuletzt-geprüft" Datum, das anzeigt, wann ein Mensch zuletzt überprüft hat, ob die Anzeige noch aktuell ist.
Nach 3 Wochen ohne Prüfung werden Anzeigen automatisch von der Seite entfernt und nur dann wieder freigeschaltet, wenn eine manuelle Prüfung erfolgt.

Darüber hinaus werden einmal täglich die verlinkten Seiten automatisiert geprüft. Wenn eine Vermittlungs-Seite bei einem Tierheim oder einer Pflegestelle entfernt wurde, wird die Anzeige ebenfalls deaktiviert.

Vermittlungen können von allen Menschen, auch ohne Account gemeldet werden. Grund dafür kann sein, dass Informationen veraltet sind oder ein Verdacht von Tierwohlgefärdung. Gemeldete Vermittlungen werden vom Moderationsteam geprüft und ggf. entfernt.

Die Kommentarfunktion von Vermittlungen ermöglicht es angemeldeten Nutzer*innen zusätzliche Informationen hinzuzufügen oder Fragen zu stellen.
Ersteller*innen von Vermittlungen werden über neue Kommentare per Mail benachrichtigt, ebenso alle die die Vermittlung abonniert haben.

Kommentare können, wie Vermittlungen, gemeldet werden.

Adoption Notice Status Choices
++++++++++++++++++++++++++++++

Aktiv
-----

Aktive Vermittlungen die über die Suche auffindbar sind.

.. list-table::
   :header-rows: 1
   :width: 100%
   :widths: 1 1 2

   * - Value
     - Label
     - Description

   * - ``active_searching``
     - Searching
     -

   * - ``active_interested``
     - Interested
     - Jemand hat bereits Interesse an den Tieren.

Warte auf Aktion
----------------

Vermittlungen in diesem Status warten darauf, dass ein Mensch sie überprüft. Sie können nicht über die Suche gefunden werden.

.. list-table::
   :header-rows: 1
   :width: 100%
   :widths: 1 1 2

   * - ``awaiting_action_waiting_for_review``
     - Waiting for review
     - Neue Vermittlung die deaktiviert ist bis Moderator*innen sie überprüfen.

   * - ``awaiting_action_needs_additional_info``
     - Needs additional info
     - Deaktiviert bis Informationen nachgetragen werden.

   * - ``disabled_unchecked``
     - Unchecked
     - Vermittlung deaktiviert bis sie vom Team auf Aktualität geprüft wurde.

Geschlossen
-----------

Geschlossene Vermittlungen tauchen in keiner Suche auf. Sie werden aber weiterhin angezeigt, wenn der Link zu ihnen direkt aufgerufen wird.

.. list-table::
   :header-rows: 1
   :width: 100%
   :widths: 1 1 2

   * - ``closed_successful_with_notfellchen``
     - Successful (with Notfellchen)
     - Vermittlung erfolgreich abgeschlossen.

   * - ``closed_successful_without_notfellchen``
     - Successful (without Notfellchen)
     - Vermittlung erfolgreich abgeschlossen.

   * - ``closed_animal_died``
     - Animal died
     - Die zu vermittelnden Tiere sind über die Regenbrücke gegangen.

   * - ``closed_for_other_adoption_notice``
     - Closed for other adoption notice
     - Vermittlung wurde zugunsten einer anderen geschlossen.

   * - ``closed_not_open_for_adoption_anymore``
     - Not open for adoption anymore
     - Tier(e) stehen nicht mehr zur Vermittlung bereit.

   * - ``closed_link_to_more_info_not_reachable``
     - Der Link zu weiteren Informationen ist nicht mehr erreichbar.
     - Der Link zu weiteren Informationen ist nicht mehr erreichbar, die Vermittlung wurde daher automatisch deaktiviert.

   * - ``closed_other``
     - Other (closed)
     - Vermittlung geschlossen.

Deaktiviert
-----------

Deaktivierte Vermittlungen werden nur noch Moderator\*innen und Administrator\*innen angezeigt.

.. list-table::
   :header-rows: 1
   :width: 100%
   :widths: 1 1 2

   * - ``disabled_against_the_rules``
     - Against the rules
     - Vermittlung deaktiviert da sie gegen die Regeln verstößt.

   * - ``disabled_other``
     - Other (disabled)
     - Vermittlung deaktiviert.


