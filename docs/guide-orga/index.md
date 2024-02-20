# Editer des activités

---

Ce guide orga s'adresse aux personnels de l'ac-mayotte souhaitant créer des activités intractives en ligne, pour le développement de la pensée informatique et le renforcement des automatismes en Python, mais aussi en "web" (HTML/JS/CSS).

---

Un **parcours** : un ensemble d'activités

Une **activité** : un contenu (introduction, documentation) et un ensemble de "questions"

Une **"question"** : une question (voir [qcm](#les-qcm)) ou un objectif de programmation en [Python](#activite-python) ou ["web"](#activite-web)

## Contenu associé à une activité 

Rédaction en md

Pièces-jointes possibles (image, js, html, ...)

Astuce pour le js : il faut le mettre dans (ou l'appeler depuis) un html joint, puis intégré dans une iframe intégrée au md du contenu. 

## Les QCM

Attention, si la réponse est numérique, ne pas utiliser Mots-Clefs, mais Numérique...

## Activité Python

### Les tests de validation des réponses

Syntaxe : 

`expression;valeur attendue;aide`

Exemples de base : 

|Test|Description|
|--|--|
|`a;True`|Teste si `a==True` et informe sur le test réalisé *(voir note 1)*|
|`a;Chaîne sans guillemets`|Teste si `a == 'Chaîne sans guillemets'` et informe sur le test réalisé *(1)*|
|`int(a);2`|Teste si `int(a) == 2` *(2)* et informe sur le test réalisé *(1)*|
|`ma_super_fonction(2);2`|Teste si `ma_super_fonction(2)`renvoie `2` *(2)* et informe sur le test réalisé *(1)*| 
|`decal;65;La variable decal doit contenir 65 ` *(3)* |Teste si `decal == 65`, informe sur le test réalisé *(1)*, et affiche l'aide "La variable decal doit contenir 65"|
|`decal;65;hide`|Teste si `decal == 65` mais n'affiche pas d'information sur le test réalisé|

Supplément au tableau : 

1. Indique la valeur attendu et la valeur obtenue.
2. De nombreuses possibilités puisque toutes les fonctions natives peuvent être utilisées, ainsi que les fonctions ou les méthodes programmées ou importées dans l'éditeur.
3. Pas de guillemets non plus pour les chaînes d'aide




Autres exemples : 

|Test               |Description|Alteranative à |Remarque
|--|--|--|--|
|`'a' in globals();True` |Teste si la variable `a` est déclarée (ne pas oublier les guillemets)|`'x' in locals();True` |Les variables ne sont pas dans le programme qui exécute les tests donc `'x' in locals()` vaudra toujours `False`|
|`int(a)==int(b);True`   |Teste si `int(a) == int(b)`|`int(4);int(b)`|La valeur attendue ne peut pas utiliser de fonction, même si le résultat est une constante. Ainsi, `int(4);int(4)` ne fonctionnera pas.|
|`isinstance(a, bool);True` |Teste si `a` est un booléen|`type(a);bool` ||
|`message;Message super important` ou `message=='Message super important';True`|Teste si `message == 'Message super important'`|`message;'Message super important'`|Si la chaîne est dans la valeur attendue, elle ne doit pas contenir de guillemets|

Ne fonctionnent pas : 

|Test                   |Remarque   |
|--|--|
|`hash("a");-1727338940`   |`hash()` ne fonctionne pas et renvoie des valeurs différentes.|



## Activité Web

