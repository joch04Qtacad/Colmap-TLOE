# Colmap TLOE - Installation

## Installation

1. Ouvrir Blender
2. Edit > Preferences > Add-ons
3. Cliquer sur Install...
4. Sélectionner le fichier PY
5. Cocher 'ColmapTLOE'
6. Cliquer sur Save Preferences

## Mise à jour

Remplacez simplement le PY par une nouvelle version puis réinstallez-la.

## Usage

juste après l'import d'un projet ColMap avec Blender-Addon-Photogrammetry-Importer sur une version 4.3 de Blender
il y a toujours qqs opérations à faire:
1. lier les caméra à la time line  (ça permet de naviguer entre les cam avec les flèches du clavier) et régler la focale (opinel, je fait des relevés au grand angle)
2. Orienter l'ensemble pour le mettre dans un repère qui nous arrange
3. Lui donner une échelle

Plutôt que de cliquer des pts, je passe par la création d'empty que l'on doit déplacer à la main (on peut mettre l'accrochage aux vertex pour se snapper sur les points du nuage c'est plus souple et plus visuel mais il faut penser à importer les "point as mesh" dans Photogrammetry-Importer)
- 3 pts à placer au sol (le futur plan z=0 de blender) pour l'orientation et on valide (ils sont nommés et 00,X détermine l'axe des x)
- 2 pts pour l'échelle, à la validation ça affiche la cote mesurée et demande la cote réelle pour calculer le facteur d'échelle
- Il y a un bouton pour purger les empty quand on a fini, un pour tout basculer avec une rotation autour de X si le Z se retrouve pas dans le bon sens et un accrochage rapide aux vertex

Nota
ne pas créer les repères quand on est en vue caméra dans la TL, elle s'acrochere à la clef, il faut les créer et les déplacer dans la vue 3d

Import brut
![Description](http://joch04.free.fr/qta-php/images/Colmap-TLOE/0-Import%20brut.png)

Time line et focale appliquée
![Description](http://joch04.free.fr/qta-php/images/Colmap-TLOE/1-TL_et_Focale_appliqué.png)

Orientation
![Description](http://joch04.free.fr/qta-php/images/Colmap-TLOE/2-Orientation.png)

Orientation appliqué
![Description](http://joch04.free.fr/qta-php/images/Colmap-TLOE/3-Orientation_appliquée.png)

Appliquer l'échelle
![Description](http://joch04.free.fr/qta-php/images/Colmap-TLOE/4-appliquer_échelle.png)

Au final, avec un peu de pratique sur la prise de relevés, on arrive à faire des modèles explotables avec 7 à 15 photo ce qui donne des workflow très faisable sur des petites config Une fois le modèle implanté, on peu dessiner dans la 3d des formes qui collent exactement au pts de vue des caméras, les pts 3d servant de support pour l'esquisse dans les vue 3d; la photo d'arrière plan aide à ajuster les formes quand on manque de pts. la précision est relative, mais pour qui a fait des relevés à la main, on y perd pas trop, et de toute façon il faut qqs cotes de ref pour controler et ajuster l'échelle. ça remplace pas un scanner 3d, mais ça dépanne...


