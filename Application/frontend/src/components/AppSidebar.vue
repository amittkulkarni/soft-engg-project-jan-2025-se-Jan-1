<template>
  <div class="col-3 bg-light min-vh-100 p-3">
    <h5 class="mb-3">Course Introduction</h5>
    <ul class="list-group">
      <!-- Collapsible Items -->
      <li v-for="(section, index) in sidebarSections" :key="index" class="list-group-item">
        <div
          class="d-flex justify-content-between align-items-center"
          data-bs-toggle="collapse"
          :data-bs-target="'#' + section.id"
          aria-expanded="false"
          :aria-controls="section.id"
        >
          <span>
            <i class="bi bi-caret-right-fill me-2"></i> {{ section.title }}
          </span>
        </div>
        <!-- Collapsible Content -->
        <ul :id="section.id" class="collapse list-group child-list mt-2">
          <li
            v-for="(item, itemIndex) in section.items"
            :key="'item-' + itemIndex"
            class="list-group-item child-list-item"
          >
            <img v-if="item.icon" :src="item.icon" alt="" class="me-2" style="width:16px;" />
            {{ item.text }}
          </li>
        </ul>
      </li>
      <li class="list-group-item">Generate Practice Questions</li>
    </ul>
  </div>
</template>

<script>
import bookIcon from '@/assets/sidebar-modules-selected.svg';

export default {
  name: 'AppSidebar',
  data() {
    return {
      sidebarSections: [
        {
          id: 'courseIntroCollapse',
          title: 'About the Course',
          items: [{ text: 'Lecture 1.1: Introduction' }],
        },
        {
          id: 'generalCollapse',
          title: 'General Instructions & Important Links',
          items: [
            { text: 'Important PDF' },
            { text: 'Resource Links' },
          ],
        },
        {
          id: 'week1Collapse',
          title: 'Week 1',
          items: [
            { icon: bookIcon, text: 'Lecture 1.1 Data Preprocessing with Pandas' },
            { icon: bookIcon, text: 'Graded Assignment 1' },
          ],
        },
        {
            id: 'week2Collapse',
            title: 'Week 2',
            items: [
              { icon: bookIcon, text: 'Lecture 1.1 Data Preprocessing with Pandas' },
              { icon: bookIcon, text: 'Graded Assignment 1' },
            ],
          },
        {
            id: 'week3Collapse',
            title: 'Week 3',
            items: [
              { icon: bookIcon, text: 'Lecture 1.1 Data Preprocessing with Pandas' },
              { icon: bookIcon, text: 'Graded Assignment 1' },
            ],
          },
        {
            id: 'week4Collapse',
            title: 'Week 4',
            items: [
              { icon: bookIcon, text: 'Lecture 1.1 Data Preprocessing with Pandas' },
              { icon: bookIcon, text: 'Graded Assignment 1' },
            ],
          },
            {
                id: 'week5Collapse',
                title: 'Week 5',
                items: [
                  { icon: bookIcon, text: 'Lecture 1.1 Data Preprocessing with Pandas' },
                  { icon: bookIcon, text: 'Graded Assignment 1' },
                ],
              },
            {
                id: 'week6Collapse',
                title: 'Week 6',
                items: [
                  { icon: bookIcon, text: 'Lecture 1.1 Data Preprocessing with Pandas' },
                  { icon: bookIcon, text: 'Graded Assignment 1' },
                ],
              },
                {
                    id: 'week7Collapse',
                    title: 'Week 7',
                    items: [
                      { icon: bookIcon, text: 'Lecture 1.1 Data Preprocessing with Pandas' },
                      { icon: bookIcon, text: 'Graded Assignment 1' },
                    ],
                  },
                {
                    id: 'week8Collapse',
                    title: 'Week 8',
                    items: [
                      { icon: bookIcon, text: 'Lecture 1.1 Data Preprocessing with Pandas' },
                      { icon: bookIcon, text: 'Graded Assignment 1' },
                    ],
                  },
                {
                    id: 'week9Collapse',
                    title: 'Week 9',
                    items: [
                      { icon: bookIcon, text: 'Lecture 1.1 Data Preprocessing with Pandas' },
                      { icon: bookIcon, text: 'Graded Assignment 1' },
                    ],
                  },
                {
                    id: 'week10Collapse',
                    title: 'Week 10',
                    items: [
                      { icon: bookIcon, text: 'Lecture 1.1 Data Preprocessing with Pandas' },
                      { icon: bookIcon, text: 'Graded Assignment 1' },
                    ],
                  },
                {
                    id: 'week11Collapse',
                    title: 'Week 11',
                    items: [
                      { icon: bookIcon, text: 'Lecture 1.1 Data Preprocessing with Pandas' },
                      { icon: bookIcon, text: 'Graded Assignment 1' },
                    ],
                  },
                {
                    id: 'week12Collapse',
                    title: 'Week 12',
                    items: [
                      { icon: bookIcon, text: 'Lecture 1.1 Data Preprocessing with Pandas' },
                      { icon: bookIcon, text: 'Graded Assignment 1' },
                    ],
                  },      ],
    };
  },
};
</script>

<style scoped>
.min-vh-100 {
  min-height: 100vh;
}

.child-list-item {
  font-size: 0.9rem;
  background-color: #fafafa;
}
</style>
