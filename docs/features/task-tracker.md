# Task Tracker Feature - Documentation

**Version:** 1.0  
**Dernière mise à jour:** 2026-02-16  
**Status:** ✅ Terminé (V1)

---

## Vue d'ensemble

Le Task Tracker est un système de gestion de tâches intégré à l'application ezlife. Il permet de créer, organiser et suivre des tâches avec une intégration directe au tracker d'activités.

## Fonctionnalités implémentées (V1)

### 1. Gestion des statuts
- **Todo** → **In Progress** → **Done**
- Possibilité de revenir en arrière (undo) avec suppression automatique des activités liées
- Boutons d'action contextuels sur chaque carte

### 2. Intégration Activity Tracker
- Conversion d'une tâche en activité
- Pré-remplissage automatique des champs depuis la tâche
- Liaison bidirectionnelle (task ↔ activity)
- Suppression automatique lors du undo

### 3. Système de vues temporelles
Trois vues disponibles via sélecteur dans le header :

| Vue | Description | Filtre |
|-----|-------------|---------|
| **Today** | Tâches du jour | `!scheduledDate OR scheduledDate == today` |
| **Week** | Tâches de la semaine | `!scheduledDate OR (scheduledDate >= monday AND scheduledDate <= sunday)` |
| **All** | Toutes les tâches | Aucun filtre |

**Semaine** = Lundi à Dimanche (calculé dynamiquement)

### 4. Affichage des dates sur les cards
- **📅 Date planifiée** (CalendarCheck, violet) : `scheduledDate`
- **📅 Date d'échéance** (Calendar, rouge si dépassée) : `dueDate`
- Affichage conditionnel selon disponibilité

### 5. Pré-remplissage intelligent (Convert to Activity)
Quand on convertit une tâche en activité :
- **Date** : `scheduledDate` ou aujourd'hui
- **Heures** : `scheduledStartTime` / `scheduledEndTime`
- **Calcul auto** : Si `scheduledStartTime` + `estimatedDurationMinutes`
- **Fallback** : Maintenant + 30min
- **Notes** : `description` ou `title`

---

## Architecture

### Frontend (Vue 3 / TypeScript)

#### Fichiers principaux

```
front/src/
├── views/TasksView.vue              # Page principale, intègre le sélecteur de vues
├── components/features/
│   ├── TaskCard.vue                 # Carte individuelle (dates, actions, badges)
│   ├── TaskDialog.vue               # Création/édition d'une tâche
│   ├── TaskToActivityDialog.vue     # Conversion tâche → activité
│   └── TaskListSidebar.vue          # Sidebar des listes
├── stores/tasks.ts                  # Store Pinia avec logique de filtrage
└── lib/api/task.ts                  # API client pour les tâches
```

#### Store - État clés

```typescript
// stores/tasks.ts
const activeView = ref<TaskView>('today')  // 'today' | 'week' | 'all'
const activeListId = ref<string | null>(null)

// Computed avec filtrage temporel
const tasksByView = computed(() => {
  // Logique de filtrage selon activeView
})
```

#### Composants clés

**TaskCard.vue**
```vue
Props:
  - task: Task

Événements émis:
  - @complete → Marquer comme done/todo
  - @edit → Ouvrir édition
  - @delete → Supprimer
  - @convert-to-activity → Ouvrir dialog conversion
  - @status-change → Changer statut (todo/in_progress/done)
```

**TaskToActivityDialog.vue**
```vue
Props:
  - task: Task
  - open: boolean

Logique:
  - prefillFromTask() → Extrait et formate les données de la tâche
```

### Backend (Python / FastAPI)

#### Fichiers principaux

```
api/app/
├── services/task_service.py         # Logique métier (CRUD, conversion, récurrence)
├── repositories/task_repository.py  # Accès données
├── models/task.py                   # Modèles SQLAlchemy
├── schemas/task.py                  # Schémas Pydantic
└── api/v1/endpoints/tasks.py        # Routes API
```

#### Modèle de données

```python
# models/task.py - Champs temporels
scheduled_date: Optional[date]
scheduled_start_time: Optional[time]
scheduled_end_time: Optional[time]
estimated_duration_minutes: Optional[int]
due_date: Optional[date]

# Relations
activity_ids: List[UUID]  # Liens vers Activity
```

#### Endpoints clés

```
GET    /api/v1/tasks                    # Liste avec filtres optionnels
POST   /api/v1/tasks                    # Création
PUT    /api/v1/tasks/{id}               # Mise à jour
POST   /api/v1/tasks/{id}/complete      # Marquer done + optionnellement créer activity
POST   /api/v1/tasks/{id}/convert-to-activity  # Conversion explicite
POST   /api/v1/tasks/{id}/generate-occurrences # Générer occurrences récurrentes
POST   /api/v1/tasks/generate-rolling   # Cron job - génération automatique
```

---

## Flux principaux

### 1. Créer une tâche et la convertir

```
TasksView → TaskDialog (create) → tasksStore.createTask() → POST /tasks
                                                   ↓
User clique "Convert to Activity" sur TaskCard → TaskToActivityDialog
                                                   ↓
Pré-remplissage auto des champs → User valide → tasksStore.convertToActivity()
                                                   ↓
POST /tasks/{id}/convert-to-activity → Activity créée + TaskActivity link
```

### 2. Marquer done avec ajout au tracker

```
TaskCard → @complete → TasksView.handleCompleteTask()
                            ↓
                   Dialog de confirmation → User choisit "Oui"
                            ↓
                   tasksStore.completeTask({ addToTracker: true })
                            ↓
                   POST /tasks/{id}/complete → Activity auto-créée
```

### 3. Undo (revenir à todo)

```
TaskCard (status=done) → @status-change('todo') → TasksView.handleStatusChange()
                                                      ↓
                   Si task.activityIds.length > 0:
                      → activitiesStore.deleteActivity(id) pour chaque
                                                      ↓
                   tasksStore.updateTask({ status: 'todo' })
```

---

## Gestion des récurrences

### Principe
- Une tâche "mère" avec `recurrenceRule` (format iCal RRULE)
- Des occurrences générées comme tâches normales sans `recurrenceRule`
- Génération automatique via endpoint `POST /tasks/generate-rolling`
- Paramètres : horizon 14 jours, maintient 3 occurrences futures minimum

### Exemple de règle
```
FREQ=DAILY;INTERVAL=1          # Tous les jours
FREQ=WEEKLY;BYDAY=MO,WE,FR     # Lundi, Mercredi, Vendredi
FREQ=MONTHLY;BYMONTHDAY=15     # Le 15 de chaque mois
```

### Génération d'occurrences
```python
# task_service.py
generate_occurrences(task_id, count=10)
  → Parse recurrence_rule avec dateutil.rrule
  → Pour chaque occurrence future:
      - Crée une tâche avec scheduled_date = date occurrence
      - Copie tous les autres champs depuis la tâche mère
      - Évite les doublons (vérifie titre + date + list_id)
```

---

## Internationalisation (i18n)

### Clés de traduction

```json
// fr.json
{
  "tasks": {
    "views": {
      "today": "Aujourd'hui",
      "week": "Semaine",
      "all": "Tout"
    },
    "statuses": {
      "todo": "À faire",
      "in_progress": "En cours",
      "done": "Fait"
    },
    "completeDialog": {
      "title": "Terminer la tâche",
      "addToTrackerQuestion": "Ajouter au tracker ?"
    },
    "convertDialog": {
      "title": "Ajouter au tracker d'activités"
    }
  }
}
```

---

## Points d'attention / Edge Cases

### 1. Filtre temporel "Today"
- **Inclut** : Tâches sans date + tâches du jour
- **Exclut** : Tâches passées ou futures
- **Use case** : Voir ce qu'on a à faire aujourd'hui sans être pollué par le futur

### 2. Undo et suppression d'activités
- Si une tâche done a plusieurs activités liées, toutes sont supprimées
- Pas de confirmation de suppression (UX fluide)
- Les activités supprimées ne sont pas récupérables

### 3. Pré-remplissage des horaires
- Priorité : `scheduledStartTime`/`scheduledEndTime` > calcul depuis durée > fallback maintenant+30min
- Si `scheduledDate` est dans le futur, la date est quand même pré-remplie

### 4. Récurrences et vues
- Les occurrences générées apparaissent selon leur `scheduledDate`
- Une occurrence passée (non faite) disparaît de la vue "Today"
- La vue "Week" montre les tâches prévues cette semaine + tâches sans date

---

## Modifications futures possibles (V2+)

### Prioritaires
- [ ] Vue calendrier (type Google Calendar) pour voir les tâches sur une timeline
- [ ] Glisser-déposer (drag & drop) entre colonnes et dates
- [ ] Rappels/notifications pour les tâches à échéance proche
- [ ] Sous-tâches / checklist dans une tâche

### Améliorations UX
- [ ] Animation lors du changement de statut
- [ ] Mode sombre pour les cartes
- [ ] Filtres avancés (par priorité, catégorie, date)
- [ ] Recherche full-text dans les tâches

### Fonctionnalités avancées
- [ ] Templates de tâches récurrentes
- [ ] Partage de listes entre utilisateurs
- [ ] Time tracking intégré (timer dans la carte)
- [ ] Estimation vs temps réellement passé

---

## Dépannage

### Les tâches n'apparaissent pas dans "Today"
Vérifier que :
1. `scheduledDate` est aujourd'hui OU la tâche n'a pas de `scheduledDate`
2. La tâche n'est pas filtrée par la liste active
3. La vue active est bien "today" (`tasksStore.activeView`)

### Le pré-remplissage ne fonctionne pas
Vérifier que :
1. La tâche a bien un `scheduledDate`
2. Les champs `scheduledStartTime` et `scheduledEndTime` sont renseignés
3. La fonction `prefillFromTask()` est appelée (watcher sur `props.open`)

### L'undo ne supprime pas l'activité
Vérifier que :
1. `task.activityIds` contient bien les IDs des activités
2. `activitiesStore.deleteActivity()` est appelé AVANT le changement de statut
3. Le backend a bien créé le lien TaskActivity lors de la conversion

---

## Contact / Maintenance

Pour toute modification de cette feature :
1. Lire cette documentation
2. Vérifier les impacts sur les 5 fonctionnalités principales
3. Tester les cas limites (undo, récurrences, vues)
4. Mettre à jour cette doc si changement significatif

---

**Fichiers liés:**
- Frontend: `front/src/views/TasksView.vue`, `front/src/components/features/Task*.vue`, `front/src/stores/tasks.ts`
- Backend: `api/app/services/task_service.py`, `api/app/models/task.py`
- Tests: `api/tests/test_task_service.py`
