# Plan de Travail : Page de Paramétrage (Settings)

**Objectif** : Créer une page complète de paramétrage permettant de gérer les Catégories, les Groupes et les Contraintes Globales avec un comportement réel (appels API).

**Date de création** : 2026-01-25  
**Estimé** : 2-3h

---

## Contexte Technique

- **Framework** : Vue 3 + TypeScript (Composition API, `<script setup>`)
- **State** : Pinia (stores déjà créés et fonctionnels)
- **API** : Ky.js avec validation Zod
- **UI** : Shadcn-vue + Tailwind CSS v4 (thème pastel lilac/sage)
- **i18n** : Vue I18n (FR/EN - traductions déjà présentes)

**Stores existants** :

- ✅ `src/stores/categories.ts` - CRUD catégories
- ✅ `src/stores/groups.ts` - CRUD groupes
- ✅ `src/stores/globalConstraints.ts` - GET/UPDATE contraintes

**Schemas Zod existants** :

- ✅ `Category` : id, name, groupId, priority, minWeeklyHours, targetWeeklyHours, maxWeeklyHours, unit, mandatory
- ✅ `Group` : id, name, color
- ✅ `GlobalConstraints` : totalWeeklyHours, minSleepHours, underutilizationThreshold, overutilizationThreshold, wastedTimeThreshold

**Traductions i18n** : Toutes les clés `settings.*` existent déjà en FR/EN.

---

## Architecture de la Solution

```
SettingsView.vue (page principale)
├── Onglet 1: CategoryManager.vue (tableau CRUD catégories)
├── Onglet 2: GroupManager.vue (tableau CRUD groupes)
└── Onglet 3: GlobalConstraintsEditor.vue (formulaire contraintes)
```

**Pattern de navigation** : Tabs Shadcn-vue avec 3 onglets (state local, pas de routing)

---

## Tâches d'Implémentation

### ☐ **Task 1 : Créer SettingsView.vue (page conteneur)**

**Fichier** : `src/views/SettingsView.vue`

**Responsabilités** :

- Layout principal avec titre "Paramètres"
- Navigation par onglets (Tabs Shadcn-vue)
- 3 onglets : Catégories, Groupes, Contraintes Globales
- Responsive design

**Spécifications** :

```vue
<script setup lang="ts">
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import CategoryManager from '@/components/features/CategoryManager.vue'
import GroupManager from '@/components/features/GroupManager.vue'
import GlobalConstraintsEditor from '@/components/features/GlobalConstraintsEditor.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="container mx-auto py-8 px-4">
    <h1 class="text-3xl font-bold mb-6">{{ t('settings.title') }}</h1>

    <Tabs default-value="categories" class="w-full">
      <TabsList class="grid w-full grid-cols-3">
        <TabsTrigger value="categories">{{ t('settings.tabs.categories') }}</TabsTrigger>
        <TabsTrigger value="groups">{{ t('settings.tabs.groups') }}</TabsTrigger>
        <TabsTrigger value="constraints">{{ t('settings.tabs.constraints') }}</TabsTrigger>
      </TabsList>

      <TabsContent value="categories">
        <CategoryManager />
      </TabsContent>

      <TabsContent value="groups">
        <GroupManager />
      </TabsContent>

      <TabsContent value="constraints">
        <GlobalConstraintsEditor />
      </TabsContent>
    </Tabs>
  </div>
</template>
```

**Vérification** :

- [ ] Import des composants Tabs depuis `@/components/ui/tabs`
- [ ] Textes via i18n (`t('settings.*')`)
- [ ] Layout responsive avec `container mx-auto`
- [ ] TypeScript strict (pas d'erreur `vue-tsc`)

---

### ☐ **Task 2 : Créer CategoryManager.vue (CRUD catégories)**

**Fichier** : `src/components/features/CategoryManager.vue`

**Responsabilités** :

- Afficher tableau des catégories existantes
- Bouton "Ajouter une catégorie" → modal
- Actions par ligne : Éditer, Supprimer (avec confirmation)
- Appels API réels via `useCategoriesStore()`

**Colonnes du tableau** :
| Catégorie | Groupe | Priorité | Min Hebdo (h) | Cible Hebdo (h) | Max Hebdo (h) | Unité | Obligatoire | Actions |
|-----------|--------|----------|---------------|-----------------|---------------|-------|-------------|---------|

**Composants UI Shadcn à utiliser** :

- `Table` (tableau)
- `Button` (actions)
- `Dialog` (modales ajout/édition)
- `Input`, `Select`, `Checkbox` (formulaire)
- `Badge` (affichage du groupe avec couleur)

**Workflow** :

1. **onMounted** : charger `categoriesStore.fetchCategories()` + `groupsStore.fetchGroups()` (besoin des groupes pour le select)
2. **Ajouter** : ouvrir Dialog → formulaire → `categoriesStore.createCategory()`
3. **Éditer** : pré-remplir Dialog avec données → `categoriesStore.updateCategory(id, data)`
4. **Supprimer** : Dialog de confirmation → `categoriesStore.deleteCategory(id)`

**Spécifications détaillées** :

```vue
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useCategoriesStore } from '@/stores/categories'
import { useGroupsStore } from '@/stores/groups'
import { useI18n } from 'vue-i18n'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import type { CreateCategory } from '@/lib/api/schemas/category'

const { t } = useI18n()
const categoriesStore = useCategoriesStore()
const groupsStore = useGroupsStore()

const isAddDialogOpen = ref(false)
const isEditDialogOpen = ref(false)
const isDeleteDialogOpen = ref(false)
const editingCategoryId = ref<string | null>(null)
const deletingCategoryId = ref<string | null>(null)

// Formulaire (réutilisé pour ajout/édition)
const formData = ref<CreateCategory>({
  name: '',
  groupId: '',
  priority: 1,
  minWeeklyHours: 0,
  targetWeeklyHours: 0,
  maxWeeklyHours: 0,
  unit: 'hours',
  mandatory: false,
})

onMounted(async () => {
  await Promise.all([categoriesStore.fetchCategories(), groupsStore.fetchGroups()])
})

const resetForm = () => {
  formData.value = {
    name: '',
    groupId: '',
    priority: 1,
    minWeeklyHours: 0,
    targetWeeklyHours: 0,
    maxWeeklyHours: 0,
    unit: 'hours',
    mandatory: false,
  }
}

const handleAdd = async () => {
  await categoriesStore.createCategory(formData.value)
  isAddDialogOpen.value = false
  resetForm()
}

const openEditDialog = (categoryId: string) => {
  const category = categoriesStore.categories.find((c) => c.id === categoryId)
  if (category) {
    editingCategoryId.value = categoryId
    formData.value = {
      name: category.name,
      groupId: category.groupId,
      priority: category.priority,
      minWeeklyHours: category.minWeeklyHours,
      targetWeeklyHours: category.targetWeeklyHours,
      maxWeeklyHours: category.maxWeeklyHours,
      unit: category.unit,
      mandatory: category.mandatory,
    }
    isEditDialogOpen.value = true
  }
}

const handleEdit = async () => {
  if (editingCategoryId.value) {
    await categoriesStore.updateCategory(editingCategoryId.value, formData.value)
    isEditDialogOpen.value = false
    resetForm()
    editingCategoryId.value = null
  }
}

const openDeleteDialog = (categoryId: string) => {
  deletingCategoryId.value = categoryId
  isDeleteDialogOpen.value = true
}

const handleDelete = async () => {
  if (deletingCategoryId.value) {
    await categoriesStore.deleteCategory(deletingCategoryId.value)
    isDeleteDialogOpen.value = false
    deletingCategoryId.value = null
  }
}

const getGroupName = (groupId: string) => {
  return groupsStore.groups.find((g) => g.id === groupId)?.name ?? '-'
}

const getGroupColor = (groupId: string) => {
  return groupsStore.groups.find((g) => g.id === groupId)?.color
}
</script>

<template>
  <div class="space-y-4">
    <!-- Header avec bouton ajout -->
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-semibold">{{ t('settings.categories.title') }}</h2>

      <Dialog v-model:open="isAddDialogOpen">
        <DialogTrigger as-child>
          <Button @click="resetForm">{{ t('settings.categories.add') }}</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{{ t('settings.categories.add') }}</DialogTitle>
          </DialogHeader>

          <!-- Formulaire -->
          <div class="grid gap-4 py-4">
            <div class="grid gap-2">
              <Label for="name">{{ t('settings.categories.fields.name') }}</Label>
              <Input id="name" v-model="formData.name" />
            </div>

            <div class="grid gap-2">
              <Label for="group">{{ t('settings.categories.fields.group') }}</Label>
              <Select v-model="formData.groupId">
                <SelectTrigger>
                  <SelectValue :placeholder="t('settings.categories.fields.group')" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="group in groupsStore.groups" :key="group.id" :value="group.id">
                    {{ group.name }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div class="grid gap-2">
              <Label for="priority">{{ t('settings.categories.fields.priority') }}</Label>
              <Input id="priority" v-model.number="formData.priority" type="number" min="1" />
            </div>

            <div class="grid grid-cols-3 gap-2">
              <div class="grid gap-2">
                <Label for="minWeekly">{{ t('settings.categories.fields.minWeekly') }}</Label>
                <Input
                  id="minWeekly"
                  v-model.number="formData.minWeeklyHours"
                  type="number"
                  step="0.5"
                  min="0"
                />
              </div>

              <div class="grid gap-2">
                <Label for="targetWeekly">{{ t('settings.categories.fields.targetWeekly') }}</Label>
                <Input
                  id="targetWeekly"
                  v-model.number="formData.targetWeeklyHours"
                  type="number"
                  step="0.5"
                  min="0"
                />
              </div>

              <div class="grid gap-2">
                <Label for="maxWeekly">{{ t('settings.categories.fields.maxWeekly') }}</Label>
                <Input
                  id="maxWeekly"
                  v-model.number="formData.maxWeeklyHours"
                  type="number"
                  step="0.5"
                  min="0"
                />
              </div>
            </div>

            <div class="grid gap-2">
              <Label for="unit">{{ t('settings.categories.fields.unit') }}</Label>
              <Select v-model="formData.unit">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hours">{{ t('settings.categories.units.hours') }}</SelectItem>
                  <SelectItem value="minutes">{{
                    t('settings.categories.units.minutes')
                  }}</SelectItem>
                  <SelectItem value="count">{{ t('settings.categories.units.count') }}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div class="flex items-center gap-2">
              <Checkbox id="mandatory" v-model:checked="formData.mandatory" />
              <Label for="mandatory">{{ t('settings.categories.fields.mandatory') }}</Label>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" @click="isAddDialogOpen = false">{{
              t('common.cancel')
            }}</Button>
            <Button @click="handleAdd">{{ t('common.save') }}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>

    <!-- État de chargement -->
    <div v-if="categoriesStore.loading" class="text-center py-8">
      {{ t('common.loading') }}
    </div>

    <!-- Erreur -->
    <div v-else-if="categoriesStore.error" class="text-red-500 py-4">
      {{ categoriesStore.error }}
      <Button @click="categoriesStore.fetchCategories()" variant="outline" class="ml-4">
        {{ t('common.retry') }}
      </Button>
    </div>

    <!-- Tableau -->
    <div v-else class="border rounded-lg">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{{ t('settings.categories.fields.name') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.group') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.priority') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.minWeekly') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.targetWeekly') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.maxWeekly') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.unit') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.mandatory') }}</TableHead>
            <TableHead class="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="category in categoriesStore.categories" :key="category.id">
            <TableCell class="font-medium">{{ category.name }}</TableCell>
            <TableCell>
              <Badge :style="{ backgroundColor: getGroupColor(category.groupId) }">
                {{ getGroupName(category.groupId) }}
              </Badge>
            </TableCell>
            <TableCell>{{ category.priority }}</TableCell>
            <TableCell>{{ category.minWeeklyHours }}</TableCell>
            <TableCell>{{ category.targetWeeklyHours }}</TableCell>
            <TableCell>{{ category.maxWeeklyHours }}</TableCell>
            <TableCell>{{ t(`settings.categories.units.${category.unit}`) }}</TableCell>
            <TableCell>{{ category.mandatory ? t('common.yes') : t('common.no') }}</TableCell>
            <TableCell class="text-right space-x-2">
              <Button variant="ghost" size="sm" @click="openEditDialog(category.id)">
                {{ t('common.edit') }}
              </Button>
              <Button variant="ghost" size="sm" @click="openDeleteDialog(category.id)">
                {{ t('common.delete') }}
              </Button>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <!-- Dialog Édition (même formulaire que l'ajout) -->
    <Dialog v-model:open="isEditDialogOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ t('settings.categories.edit') }}</DialogTitle>
        </DialogHeader>

        <!-- Même formulaire que l'ajout -->
        <div class="grid gap-4 py-4">
          <div class="grid gap-2">
            <Label for="edit-name">{{ t('settings.categories.fields.name') }}</Label>
            <Input id="edit-name" v-model="formData.name" />
          </div>

          <div class="grid gap-2">
            <Label for="edit-group">{{ t('settings.categories.fields.group') }}</Label>
            <Select v-model="formData.groupId">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="group in groupsStore.groups" :key="group.id" :value="group.id">
                  {{ group.name }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="grid gap-2">
            <Label for="edit-priority">{{ t('settings.categories.fields.priority') }}</Label>
            <Input id="edit-priority" v-model.number="formData.priority" type="number" min="1" />
          </div>

          <div class="grid grid-cols-3 gap-2">
            <div class="grid gap-2">
              <Label for="edit-minWeekly">{{ t('settings.categories.fields.minWeekly') }}</Label>
              <Input
                id="edit-minWeekly"
                v-model.number="formData.minWeeklyHours"
                type="number"
                step="0.5"
                min="0"
              />
            </div>

            <div class="grid gap-2">
              <Label for="edit-targetWeekly">{{
                t('settings.categories.fields.targetWeekly')
              }}</Label>
              <Input
                id="edit-targetWeekly"
                v-model.number="formData.targetWeeklyHours"
                type="number"
                step="0.5"
                min="0"
              />
            </div>

            <div class="grid gap-2">
              <Label for="edit-maxWeekly">{{ t('settings.categories.fields.maxWeekly') }}</Label>
              <Input
                id="edit-maxWeekly"
                v-model.number="formData.maxWeeklyHours"
                type="number"
                step="0.5"
                min="0"
              />
            </div>
          </div>

          <div class="grid gap-2">
            <Label for="edit-unit">{{ t('settings.categories.fields.unit') }}</Label>
            <Select v-model="formData.unit">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="hours">{{ t('settings.categories.units.hours') }}</SelectItem>
                <SelectItem value="minutes">{{
                  t('settings.categories.units.minutes')
                }}</SelectItem>
                <SelectItem value="count">{{ t('settings.categories.units.count') }}</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="flex items-center gap-2">
            <Checkbox id="edit-mandatory" v-model:checked="formData.mandatory" />
            <Label for="edit-mandatory">{{ t('settings.categories.fields.mandatory') }}</Label>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="isEditDialogOpen = false">{{
            t('common.cancel')
          }}</Button>
          <Button @click="handleEdit">{{ t('common.save') }}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Dialog Suppression -->
    <Dialog v-model:open="isDeleteDialogOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ t('settings.categories.delete') }}</DialogTitle>
        </DialogHeader>
        <p>{{ t('settings.categories.confirmDelete') }}</p>
        <DialogFooter>
          <Button variant="outline" @click="isDeleteDialogOpen = false">{{
            t('common.cancel')
          }}</Button>
          <Button variant="destructive" @click="handleDelete">{{ t('common.delete') }}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
```

**Vérification** :

- [ ] Chargement initial des données (categories + groups)
- [ ] Formulaire d'ajout fonctionnel
- [ ] Édition avec pré-remplissage
- [ ] Suppression avec confirmation
- [ ] Gestion des états (loading, error)
- [ ] Badge avec couleur du groupe
- [ ] Tous les textes via i18n
- [ ] TypeScript strict

---

### ☐ **Task 3 : Créer GroupManager.vue (CRUD groupes)**

**Fichier** : `src/components/features/GroupManager.vue`

**Responsabilités** :

- Afficher tableau des groupes
- Ajouter/Éditer/Supprimer des groupes
- Color picker pour le champ `color`

**Colonnes du tableau** :
| Nom du Groupe | Couleur | Actions |
|---------------|---------|---------|

**Composants UI** :

- `Table`
- `Button`
- `Dialog`
- `Input`
- `Input` type="color" (native HTML color picker)
- `Badge` (affichage visuel de la couleur)

**Spécifications** :

```vue
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useGroupsStore } from '@/stores/groups'
import { useI18n } from 'vue-i18n'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import type { CreateGroup } from '@/lib/api/schemas/group'

const { t } = useI18n()
const groupsStore = useGroupsStore()

const isAddDialogOpen = ref(false)
const isEditDialogOpen = ref(false)
const isDeleteDialogOpen = ref(false)
const editingGroupId = ref<string | null>(null)
const deletingGroupId = ref<string | null>(null)

const formData = ref<CreateGroup>({
  name: '',
  color: '#8B5CF6', // Couleur par défaut (lilac)
})

onMounted(async () => {
  await groupsStore.fetchGroups()
})

const resetForm = () => {
  formData.value = {
    name: '',
    color: '#8B5CF6',
  }
}

const handleAdd = async () => {
  await groupsStore.createGroup(formData.value)
  isAddDialogOpen.value = false
  resetForm()
}

const openEditDialog = (groupId: string) => {
  const group = groupsStore.groups.find((g) => g.id === groupId)
  if (group) {
    editingGroupId.value = groupId
    formData.value = {
      name: group.name,
      color: group.color ?? '#8B5CF6',
    }
    isEditDialogOpen.value = true
  }
}

const handleEdit = async () => {
  if (editingGroupId.value) {
    await groupsStore.updateGroup(editingGroupId.value, formData.value)
    isEditDialogOpen.value = false
    resetForm()
    editingGroupId.value = null
  }
}

const openDeleteDialog = (groupId: string) => {
  deletingGroupId.value = groupId
  isDeleteDialogOpen.value = true
}

const handleDelete = async () => {
  if (deletingGroupId.value) {
    await groupsStore.deleteGroup(deletingGroupId.value)
    isDeleteDialogOpen.value = false
    deletingGroupId.value = null
  }
}
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-semibold">{{ t('settings.groups.title') }}</h2>

      <Dialog v-model:open="isAddDialogOpen">
        <DialogTrigger as-child>
          <Button @click="resetForm">{{ t('settings.groups.add') }}</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{{ t('settings.groups.add') }}</DialogTitle>
          </DialogHeader>

          <div class="grid gap-4 py-4">
            <div class="grid gap-2">
              <Label for="name">{{ t('settings.groups.fields.name') }}</Label>
              <Input id="name" v-model="formData.name" />
            </div>

            <div class="grid gap-2">
              <Label for="color">{{ t('settings.groups.fields.color') }}</Label>
              <div class="flex items-center gap-2">
                <Input id="color" v-model="formData.color" type="color" class="w-20 h-10" />
                <Input v-model="formData.color" type="text" placeholder="#8B5CF6" />
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" @click="isAddDialogOpen = false">{{
              t('common.cancel')
            }}</Button>
            <Button @click="handleAdd">{{ t('common.save') }}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>

    <!-- Loading -->
    <div v-if="groupsStore.loading" class="text-center py-8">
      {{ t('common.loading') }}
    </div>

    <!-- Error -->
    <div v-else-if="groupsStore.error" class="text-red-500 py-4">
      {{ groupsStore.error }}
      <Button @click="groupsStore.fetchGroups()" variant="outline" class="ml-4">
        {{ t('common.retry') }}
      </Button>
    </div>

    <!-- Table -->
    <div v-else class="border rounded-lg">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{{ t('settings.groups.fields.name') }}</TableHead>
            <TableHead>{{ t('settings.groups.fields.color') }}</TableHead>
            <TableHead class="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="group in groupsStore.groups" :key="group.id">
            <TableCell class="font-medium">{{ group.name }}</TableCell>
            <TableCell>
              <Badge :style="{ backgroundColor: group.color }">
                {{ group.color }}
              </Badge>
            </TableCell>
            <TableCell class="text-right space-x-2">
              <Button variant="ghost" size="sm" @click="openEditDialog(group.id)">
                {{ t('common.edit') }}
              </Button>
              <Button variant="ghost" size="sm" @click="openDeleteDialog(group.id)">
                {{ t('common.delete') }}
              </Button>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <!-- Edit Dialog -->
    <Dialog v-model:open="isEditDialogOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ t('settings.groups.edit') }}</DialogTitle>
        </DialogHeader>

        <div class="grid gap-4 py-4">
          <div class="grid gap-2">
            <Label for="edit-name">{{ t('settings.groups.fields.name') }}</Label>
            <Input id="edit-name" v-model="formData.name" />
          </div>

          <div class="grid gap-2">
            <Label for="edit-color">{{ t('settings.groups.fields.color') }}</Label>
            <div class="flex items-center gap-2">
              <Input id="edit-color" v-model="formData.color" type="color" class="w-20 h-10" />
              <Input v-model="formData.color" type="text" placeholder="#8B5CF6" />
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="isEditDialogOpen = false">{{
            t('common.cancel')
          }}</Button>
          <Button @click="handleEdit">{{ t('common.save') }}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Delete Dialog -->
    <Dialog v-model:open="isDeleteDialogOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ t('settings.groups.delete') }}</DialogTitle>
        </DialogHeader>
        <p>{{ t('settings.groups.confirmDelete') }}</p>
        <DialogFooter>
          <Button variant="outline" @click="isDeleteDialogOpen = false">{{
            t('common.cancel')
          }}</Button>
          <Button variant="destructive" @click="handleDelete">{{ t('common.delete') }}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
```

**Vérification** :

- [ ] CRUD complet fonctionnel
- [ ] Color picker natif HTML
- [ ] Affichage visuel de la couleur (Badge)
- [ ] États loading/error
- [ ] i18n complet

---

### ☐ **Task 4 : Créer GlobalConstraintsEditor.vue (formulaire contraintes)**

**Fichier** : `src/components/features/GlobalConstraintsEditor.vue`

**Responsabilités** :

- Afficher formulaire avec valeurs actuelles
- Bouton "Enregistrer" pour sauvegarder via API
- Appel API réel via `useGlobalConstraintsStore()`

**Champs du formulaire** :

- Heures totales semaine (défaut : 168h)
- Heures minimum sommeil (défaut : 56h)
- Seuil sous-utilisation (défaut : 0.80)
- Seuil sur-utilisation (défaut : 1.20)
- Seuil temps perdu (h) (défaut : 2.00)

**Spécifications** :

```vue
<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useGlobalConstraintsStore } from '@/stores/globalConstraints'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import type { UpdateGlobalConstraints } from '@/lib/api/schemas/globalConstraints'

const { t } = useI18n()
const constraintsStore = useGlobalConstraintsStore()

const formData = ref<UpdateGlobalConstraints>({
  totalWeeklyHours: 168,
  minSleepHours: 56,
  underutilizationThreshold: 0.8,
  overutilizationThreshold: 1.2,
  wastedTimeThreshold: 2,
})

const isSaving = ref(false)

onMounted(async () => {
  await constraintsStore.fetchConstraints()

  // Pré-remplir avec les données actuelles
  if (constraintsStore.constraints) {
    formData.value = {
      totalWeeklyHours: constraintsStore.constraints.totalWeeklyHours,
      minSleepHours: constraintsStore.constraints.minSleepHours,
      underutilizationThreshold: constraintsStore.constraints.underutilizationThreshold,
      overutilizationThreshold: constraintsStore.constraints.overutilizationThreshold,
      wastedTimeThreshold: constraintsStore.constraints.wastedTimeThreshold,
    }
  }
})

// Mettre à jour le formulaire si les données changent
watch(
  () => constraintsStore.constraints,
  (newConstraints) => {
    if (newConstraints) {
      formData.value = {
        totalWeeklyHours: newConstraints.totalWeeklyHours,
        minSleepHours: newConstraints.minSleepHours,
        underutilizationThreshold: newConstraints.underutilizationThreshold,
        overutilizationThreshold: newConstraints.overutilizationThreshold,
        wastedTimeThreshold: newConstraints.wastedTimeThreshold,
      }
    }
  },
)

const handleSave = async () => {
  isSaving.value = true
  try {
    await constraintsStore.updateConstraints(formData.value)
    // Succès (on pourrait ajouter un toast ici)
  } catch (error) {
    // Erreur gérée par le store
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <h2 class="text-2xl font-semibold">{{ t('settings.constraints.title') }}</h2>

    <!-- Loading -->
    <div v-if="constraintsStore.loading && !constraintsStore.constraints" class="text-center py-8">
      {{ t('common.loading') }}
    </div>

    <!-- Error -->
    <div v-else-if="constraintsStore.error" class="text-red-500 py-4">
      {{ constraintsStore.error }}
      <Button @click="constraintsStore.fetchConstraints()" variant="outline" class="ml-4">
        {{ t('common.retry') }}
      </Button>
    </div>

    <!-- Formulaire -->
    <div v-else class="max-w-2xl border rounded-lg p-6 space-y-6">
      <div class="grid gap-4">
        <div class="grid gap-2">
          <Label for="totalWeekly">{{ t('settings.constraints.fields.totalWeekly') }}</Label>
          <Input
            id="totalWeekly"
            v-model.number="formData.totalWeeklyHours"
            type="number"
            step="1"
            min="0"
            :disabled="isSaving"
          />
          <p class="text-sm text-gray-500">
            Nombre d'heures dans une semaine (défaut: 168h = 7j × 24h)
          </p>
        </div>

        <div class="grid gap-2">
          <Label for="minSleep">{{ t('settings.constraints.fields.minSleep') }}</Label>
          <Input
            id="minSleep"
            v-model.number="formData.minSleepHours"
            type="number"
            step="1"
            min="0"
            :disabled="isSaving"
          />
          <p class="text-sm text-gray-500">
            Heures minimales de sommeil par semaine (défaut: 56h = 8h/jour)
          </p>
        </div>

        <div class="grid gap-2">
          <Label for="underutilization">{{
            t('settings.constraints.fields.underutilization')
          }}</Label>
          <Input
            id="underutilization"
            v-model.number="formData.underutilizationThreshold"
            type="number"
            step="0.01"
            min="0"
            max="1"
            :disabled="isSaving"
          />
          <p class="text-sm text-gray-500">Seuil de sous-utilisation (0.80 = 80%)</p>
        </div>

        <div class="grid gap-2">
          <Label for="overutilization">{{
            t('settings.constraints.fields.overutilization')
          }}</Label>
          <Input
            id="overutilization"
            v-model.number="formData.overutilizationThreshold"
            type="number"
            step="0.01"
            min="1"
            :disabled="isSaving"
          />
          <p class="text-sm text-gray-500">Seuil de sur-utilisation (1.20 = 120%)</p>
        </div>

        <div class="grid gap-2">
          <Label for="wastedTime">{{ t('settings.constraints.fields.wastedTime') }}</Label>
          <Input
            id="wastedTime"
            v-model.number="formData.wastedTimeThreshold"
            type="number"
            step="0.5"
            min="0"
            :disabled="isSaving"
          />
          <p class="text-sm text-gray-500">Seuil de temps perdu (en heures)</p>
        </div>
      </div>

      <div class="flex justify-end">
        <Button @click="handleSave" :disabled="isSaving">
          {{ isSaving ? t('common.loading') : t('settings.constraints.save') }}
        </Button>
      </div>
    </div>
  </div>
</template>
```

**Vérification** :

- [ ] Chargement des données au mount
- [ ] Pré-remplissage du formulaire
- [ ] Sauvegarde fonctionnelle
- [ ] États loading/saving
- [ ] Textes d'aide (descriptions)
- [ ] i18n complet

---

### ☐ **Task 5 : Ajouter la route /settings dans le router**

**Fichier** : `src/router/index.ts`

**Action** : Ajouter une route protégée `/settings` utilisant `AuthenticatedLayout`.

**Code à ajouter** :

```typescript
import SettingsView from '@/views/SettingsView.vue'

// Dans le tableau routes[], ajouter :
{
  path: '/settings',
  component: SettingsView,
  meta: { requiresAuth: true }, // Route protégée
}
```

**Vérification** :

- [ ] Route accessible à `http://localhost:5173/settings`
- [ ] Redirection vers `/login` si non authentifié
- [ ] Navigation via sidebar AuthenticatedLayout fonctionne

---

### ☐ **Task 6 : Vérifier l'intégration complète**

**Actions** :

1. Lancer le serveur dev : `npm run dev`
2. Se connecter via Google OAuth
3. Accéder à `/settings`
4. Tester chaque onglet :
   - **Catégories** : Ajouter, éditer, supprimer une catégorie
   - **Groupes** : Ajouter, éditer, supprimer un groupe
   - **Contraintes** : Modifier et sauvegarder
5. Vérifier dans la console réseau que les appels API sont bien effectués
6. Vérifier les traductions FR/EN (changer de langue via le sélecteur)

**Vérification TypeScript** :

```bash
npm run type-check
```

**Build de production** :

```bash
npm run build
```

**Checklist finale** :

- [ ] Aucune erreur TypeScript
- [ ] Build de production réussit
- [ ] Appels API réels (pas de mock)
- [ ] Traductions FR/EN complètes
- [ ] UI responsive (mobile + desktop)
- [ ] États loading/error gérés
- [ ] Modales de confirmation pour suppression
- [ ] Color picker pour groupes

---

## Notes Importantes

1. **Pas de mock** : Tous les appels API doivent être réels. Les stores utilisent déjà les API clients configurés.

2. **Composants Shadcn** : Tous les composants UI (Table, Dialog, Input, etc.) doivent déjà être installés. S'ils manquent, les installer via :

   ```bash
   npx shadcn-vue@latest add table
   npx shadcn-vue@latest add dialog
   npx shadcn-vue@latest add input
   npx shadcn-vue@latest add label
   npx shadcn-vue@latest add select
   npx shadcn-vue@latest add checkbox
   npx shadcn-vue@latest add badge
   ```

3. **Gestion d'erreurs** : Les erreurs API sont capturées par les stores (état `error`). Afficher un message + bouton "Réessayer".

4. **Optimisations futures** (hors scope pour ce plan) :
   - Toast notifications (succès/erreur)
   - Validation côté client (Zod dans le formulaire)
   - Debounce sur les inputs
   - Cache des données (ne pas re-fetch à chaque ouverture d'onglet)

---

## Backend Requirements (FastAPI)

Le backend FastAPI doit exposer les endpoints suivants :

### **Groupes API**

```python
# GET /api/v1/groups
# Headers: Authorization: Bearer <token>
# Response: List[Group]

# POST /api/v1/groups
# Headers: Authorization: Bearer <token>
# Body: { "name": str, "color": str | null }
# Response: Group

# PATCH /api/v1/groups/{group_id}
# Headers: Authorization: Bearer <token>
# Body: { "name": str | null, "color": str | null }
# Response: Group

# DELETE /api/v1/groups/{group_id}
# Headers: Authorization: Bearer <token>
# Response: 204 No Content
# Error: 400 si des catégories référencent ce groupe
```

### **Catégories API**

```python
# GET /api/v1/categories
# Headers: Authorization: Bearer <token>
# Response: List[Category]

# POST /api/v1/categories
# Headers: Authorization: Bearer <token>
# Body: {
#   "name": str,
#   "groupId": str (UUID),
#   "priority": int (min 1),
#   "minWeeklyHours": float (min 0),
#   "targetWeeklyHours": float (min 0),
#   "maxWeeklyHours": float (min 0),
#   "unit": "hours" | "minutes" | "count",
#   "mandatory": bool
# }
# Response: Category

# PATCH /api/v1/categories/{category_id}
# Headers: Authorization: Bearer <token>
# Body: Partial de CreateCategory
# Response: Category

# DELETE /api/v1/categories/{category_id}
# Headers: Authorization: Bearer <token>
# Response: 204 No Content
```

### **Contraintes Globales API**

```python
# GET /api/v1/global-constraints
# Headers: Authorization: Bearer <token>
# Response: GlobalConstraints (singleton par utilisateur)
# Note: Créer automatiquement avec valeurs par défaut si n'existe pas

# PATCH /api/v1/global-constraints
# Headers: Authorization: Bearer <token>
# Body: {
#   "totalWeeklyHours": float | null,
#   "minSleepHours": float | null,
#   "underutilizationThreshold": float (0-1) | null,
#   "overutilizationThreshold": float (>1) | null,
#   "wastedTimeThreshold": float | null
# }
# Response: GlobalConstraints
```

**Modèles Pydantic (Backend)** :

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from uuid import UUID
from datetime import datetime

# Group
class GroupBase(BaseModel):
    name: str = Field(min_length=1)
    color: str | None = None

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    name: str | None = None
    color: str | None = None

class Group(GroupBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        # Aliases pour camelCase
        populate_by_name = True
        alias_generator = lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )

# Category
class CategoryBase(BaseModel):
    name: str = Field(min_length=1)
    group_id: UUID
    priority: int = Field(ge=1, default=1)
    min_weekly_hours: float = Field(ge=0, default=0)
    target_weekly_hours: float = Field(ge=0, default=0)
    max_weekly_hours: float = Field(ge=0, default=0)
    unit: Literal["hours", "minutes", "count"] = "hours"
    mandatory: bool = False

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: str | None = None
    group_id: UUID | None = None
    priority: int | None = Field(ge=1, default=None)
    min_weekly_hours: float | None = Field(ge=0, default=None)
    target_weekly_hours: float | None = Field(ge=0, default=None)
    max_weekly_hours: float | None = Field(ge=0, default=None)
    unit: Literal["hours", "minutes", "count"] | None = None
    mandatory: bool | None = None

class Category(CategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        alias_generator = lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )

# GlobalConstraints
class GlobalConstraintsBase(BaseModel):
    total_weekly_hours: float = Field(ge=0, default=168)
    min_sleep_hours: float = Field(ge=0, default=56)
    underutilization_threshold: float = Field(ge=0, le=1, default=0.8)
    overutilization_threshold: float = Field(ge=1, default=1.2)
    wasted_time_threshold: float = Field(ge=0, default=2)

class GlobalConstraintsUpdate(BaseModel):
    total_weekly_hours: float | None = Field(ge=0, default=None)
    min_sleep_hours: float | None = Field(ge=0, default=None)
    underutilization_threshold: float | None = Field(ge=0, le=1, default=None)
    overutilization_threshold: float | None = Field(ge=1, default=None)
    wasted_time_threshold: float | None = Field(ge=0, default=None)

class GlobalConstraints(GlobalConstraintsBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        alias_generator = lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )
```

**Points critiques** :

- ✅ **Authentication** : Toutes les routes nécessitent `Authorization: Bearer <token>`
- ✅ **Scope utilisateur** : Chaque utilisateur ne voit QUE ses propres données
- ✅ **CORS** : Configurer FastAPI pour accepter les requêtes depuis `http://localhost:5173`
- ✅ **camelCase** : Utiliser des alias Pydantic pour retourner du JSON en camelCase
- ✅ **Foreign Key** : Empêcher la suppression d'un groupe si des catégories le référencent (erreur 400)
- ✅ **GlobalConstraints singleton** : Créer automatiquement si n'existe pas pour l'utilisateur

---

## Résumé Checklist

- [ ] **Task 1** : SettingsView.vue créé avec tabs
- [ ] **Task 2** : CategoryManager.vue fonctionnel (CRUD)
- [ ] **Task 3** : GroupManager.vue fonctionnel (CRUD)
- [ ] **Task 4** : GlobalConstraintsEditor.vue fonctionnel
- [ ] **Task 5** : Route `/settings` ajoutée
- [ ] **Task 6** : Tests end-to-end passés
- [ ] TypeScript : `npm run type-check` ✅
- [ ] Build : `npm run build` ✅
- [ ] Backend : Tous les endpoints implémentés et testés

---

**FIN DU PLAN**
