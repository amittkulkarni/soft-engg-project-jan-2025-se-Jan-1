<template>
  <div class="col-3 bg-light min-vh-100 p-3">
    <h5 class="mb-3">Course Introduction</h5>
    <ul class="list-group">
      <!-- Non-collapsible Item: About the Course -->
      <li class="list-group-item">
        <router-link to="/course" class="no-link">
          <span><i class="bi bi-info-circle me-2"></i> About the Course</span>
        </router-link>
      </li>

      <!-- Collapsible Items -->
      <li v-for="(section, index) in sidebarSections" :key="index" class="list-group-item">
        <div
          class="d-flex justify-content-between align-items-center section-header"
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
        <ul :id="section.id"
            class="collapse list-group child-list mt-2"
        >
          <li
            v-for="(item, itemIndex) in section.items"
            :key="'child-' + itemIndex"
            class="list-group-item child-list-item"
          >
            <router-link :to="item.link" class="no-link">
              <img v-if="item.icon" :src="item.icon" alt="" class="me-2" style=" width:16px;"/>
              {{ item.text }}
            </router-link>
          </li>
        </ul>
      </li>

      <!-- Normal Sidebar Items -->
      <li class="list-group-item mt-2">
        <router-link :to=" {
                       path: '/ga',
                       query: {title: 'Mock Quiz 1'}
                     }" class="no-link">
          <span><i class="bi bi-pencil-square me-2"></i> Generate Mock Quiz 1</span>
        </router-link>
      </li>

      <li v-for="(section, index) in sidebarSectionsAfterMockQuiz1" :key="'after-' + index" class="list-group-item">
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
            :key="'child-after-' + itemIndex"
            class="list-group-item child-list-item"
          >
            <router-link :to="item.link" class="no-link">
              <img v-if="item.icon" :src="item.icon" alt="" class="me-2" style=" width:16px;"/>
              {{ item.text }}
            </router-link>
          </li>
        </ul>
      </li>

      <!-- Mock Quiz 2 -->
      <li class="list-group-item mt-2">
        <router-link :to=" {
                       path: '/ga',
                       query: {title: 'Mock Quiz 2'}
                     }" class="no-link">
          <span><i class="bi bi-pencil-square me-2"></i> Generate Mock Quiz 2</span>
        </router-link>
      </li>

      <li v-for="(section, index) in sidebarSectionsAfterMockQuiz2" :key="'after-' + index" class="list-group-item">
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
            :key="'child-after-' + itemIndex"
            class="list-group-item child-list-item"
          >
            <router-link :to="item.link" class="no-link">
              <img v-if="item.icon" :src="item.icon" alt="" class="me-2" style=" width:16px;"/>
              {{ item.text }}
            </router-link>
          </li>
        </ul>
      </li>
      <li class="list-group-item mt-2">
        <router-link :to=" {
                       path: '/ga',
                       query: {title: 'Mock End Term'}
                     }" class="no-link">
          <span><i class="bi bi-pencil-square me-2"></i> Generate Mock End Term</span>
        </router-link>
      </li>
      <li class="list-group-item mt-2">
        <router-link :to=" {
                       path: '/ga',
                       query: {title: 'Topic Specific Mock'}
                     }" class="no-link">
          <span><i class="bi bi-pencil-square me-2"></i> Generate Topic Specific Mock</span>
        </router-link>
      </li>
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
          id: 'week1Collapse',
          title: 'Week 1',
          items: [
            {
              icon: bookIcon,
              text: 'Lecture 1.1 Data Preprocessing with Pandas',
              link: '/lecture'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 1',
              link: '/ga'
            },
          ],
        },
        {
          id: 'week2Collapse',
          title: 'Week 2',
          items: [
            {
              icon: bookIcon,
              text: 'Lecture 2.1 Data Preprocessing with Pandas',
              link: '/lecture'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 2',
              link: '/ga'
            },
          ],
        },
        {
          id: 'week3Collapse',
          title: 'Week 3',
          items: [
            {
              icon: bookIcon,
              text: 'Lecture 3.1 Data Preprocessing with Pandas',
              link: '/lecture'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 3',
              link: '/ga'
            },
          ],
        },
        {
          id: 'week4Collapse',
          title: 'Week 4',
          items: [
            {
              icon: bookIcon,
              text: 'Lecture 4.1 Data Preprocessing with Pandas',
              link: '/lecture'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 4',
              link: '/ga'
            },
          ],
        },
      ],
      sidebarSectionsAfterMockQuiz1: [
        {
          id: 'week5Collapse',
          title: 'Week 5',
          items: [
            {
              icon: bookIcon,
              text: 'Lecture 5.1 Data Preprocessing with Pandas',
              link: '/lecture'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 5',
              link: '/ga'
            },
          ],
        },
        {
          id: 'week6Collapse',
          title: 'Week 6',
          items: [
            {
              icon: bookIcon,
              text: 'Lecture 6.1 Data Preprocessing with Pandas',
              link: '/lecture'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 6',
              link: '/ga'
            },
          ],
        },
        {
          id: 'week7Collapse',
          title: 'Week 7',
          items: [
            {
              icon: bookIcon,
              text: 'Lecture 7.1 Data Preprocessing with Pandas',
              link: '/lecture'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 7',
              link: '/ga'
            },
          ],
        },
        {
          id: 'week8Collapse',
          title: 'Week 8',
          items: [
            {
              icon: bookIcon,
              text: 'Lecture 8.1 Data Preprocessing with Pandas',
              link: '/lecture'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 8',
              link: '/ga'
            },
          ],
        },
      ],
      sidebarSectionsAfterMockQuiz2: [
        {
          id: 'week9Collapse',
          title: 'Week 9',
          items: [
            {
              icon: bookIcon,
              text: 'Lecture 9.1 Data Preprocessing with Pandas',
              link: '/lecture'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 9',
              link: '/ga'
            },
          ],
        },
        {
          id: 'week10Collapse',
          title: 'Week 10',
          items: [
            {
              icon: bookIcon,
              text: 'Lecture 10.1 Data Preprocessing with Pandas',
              link: '/lecture'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 10',
              link: '/ga'
            },
          ],
        },
        {
          id: 'week11Collapse',
          title: 'Week 11',
          items: [
            {
              icon: bookIcon,
              text: 'Lecture 11.1 Data Preprocessing with Pandas',
              link: '/lecture'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 11',
              link: '/ga'
            },
          ],
        },
        {
          id: 'week12Collapse',
          title: 'Week 12',
          items: [
            {
              icon: bookIcon,
              text: 'Lecture 12.1 Data Preprocessing with Pandas',
              link: '/lecture'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 12',
              link: '/ga'
            },
          ],
        }, ],
    };
  },
  methods: {
    navigateToMock(link, title) {
      this.$router.push({
        path: link,
        query: { title }
      });
    },
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

.list-group-item {
  cursor: pointer;
}

.list-group-item:hover {
  background-color: #f0f0f0;
}

.no-link {
  text-decoration: none;
  color: inherit;
}

.section-header {
  cursor: pointer;
}
</style>
