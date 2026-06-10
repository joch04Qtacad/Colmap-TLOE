# Colmap TLOE - Installation

## Installation

1. Ouvrir Blender
2. Edit > Preferences > Add-ons
3. Cliquer sur Install...
4. Sélectionner le fichier PY
5. Cocher 'ColmapTLOE'
6. Cliquer sur Save Preferences

## Mise à jour

Remplacez simplement le ZIP par une nouvelle version puis réinstallez-la.

## Modification demandée

Usage
juste après l'import d'un projet ColMap avec Blender-Addon-Photogrammetry-Importer sur une version 4.3 de Blender
il y a toujours qqs opérations à faire:
	1 lier les caméra à la time line  (ça permet de naviguer entre les cam avec les flèches du clavier) et régler la focale (opinel, je fait des relevés au grand angle)
	2 orienter l'ensemble pour le mettre dans un repère qui nous arrange
	3 lui donner une échelle 

Plutôt que de cliquer des pts, je passe par la création d'empty que l'on doit déplacer à la main (on peut mettre l'accrochage aux vertex pour se snapper sur les points du nuage c'est plus souple et plus visuel mais il faut penser à importer les mesh du nuage)
3 pts à placer au sol (le futur plan z=0 de blender) pour l'orientation et on valide (ils sont nommés et 00,X détermine l'axe des x)
2 pts pour l'échelle, à la validation ça affiche la cote mesurée et demande la cote réelle pour calculer le facteur d'échelle

il y a un bouton pour purger les empty quand on a fini, un pour tout basculer avec une rotation autour de X si le Z se retrouve pas dans le bon sens et un accrochage rapide aux vertex

une fois le modèle implanté, on peu dessiner dans la 3d des formes qui collent exactement au pts de vue des caméras, les pts 3d servant de support pour l'esquisse
