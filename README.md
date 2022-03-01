# DMCA - Survivor
Vanden Bossche Loïc, SOARES Enzo

## Sujet de base :
Jeu type tower defense :

Le principe est simple, le joueur est au centre de la map, il se défend contre des hordes d’ennemis. Ces hordes sont de plus en plus difficiles. Le joueur peut augmenter sa défense ou des dégâts. Chaque ennemi aura un nom.

Pour récupérer les noms automatiquement, nous demandons au joueur une chaine youtube.

Nous récupérons le texte de toutes les vidéos et on le passe dans un algorithme de ML afin d’en extraire les ‘noms’ (Gaspard, Léodard, Jean-Marie, Staint-Michel …)

## Projet
Ceci est un jeu vidéo réalisé en python avec pygame.

Le jeu est caractérisé par sa manière complexe de récupérer les sprites et noms des enemies.
Le jeu est doté d'un menu principal, un écran de recherche de chaine, un menu de chaine, un écran de loading
et évidement du jeu en lui meme.

Le joueur peut sélectionner sa difficulté. La vie du joueur sera impactée.
Les scores seront enregistrés pour chaque difficulté à chaque fin de partie.

Le loader récupère une musique pour le jeu en lien avec la chaine.

Le loader utilise un algorithme de ml différent pour chaque langue pour extraire les personnes.

## Lancement

Le projet est lancé avec PyCharm avec cette configuration :

Script path : ... PycharmProjects\DMCA-Survivor\src\main.py
Working directory : ... PycharmProjects\DMCA-Survivor\src

Lancer le projet d'une autre manière peut occasionner des problèmes avec pygame_gui.

##Libraries principales

- pygame (library graphique)
- pygame_gui
- pytimeparse
- requests
- scikit_image (montage d'images en grille)
- spacy (NLP)
- youtube_dl (Pour télécharger les musiques)
- youtube_search_python
- youtube_transcript_api 
- yt_dlp
- beautifulsoup4 (Pour le scrapper Google image)

Voir fichier requirements.txt pour les versions.
