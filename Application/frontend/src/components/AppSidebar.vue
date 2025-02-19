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
      <!--<template v-for="(sectionGroup, groupIndex) in sectionGroups" :key="'group-' + groupIndex">-->
      <li v-for="(section, index) in sidebarSections" :key="'section-' + index" class="list-group-item">
        <div
          class="d-flex justify-content-between align-items-center section-header"
          @click="handleCollapse(section.id)"
        >
          <span>
            <i class="bi me-2"
               :class="activeSection === section.id ? 'bi-caret-down-fill' : 'bi-caret-right-fill'">
            </i> {{ section.title }}
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
            <router-link :to=" {
                           path: item.link,
                           query: {
                             title: item.text,
                             videoId: item.videoId
                           }
                         }" class="no-link">
              <img v-if="item.icon" :src="item.icon" alt="" class="me-2" style="  width:16px;"/>
              {{ item.text }}
            </router-link>
          </li>
        </ul>
      </li>

      <!-- Mock Quiz 1 -->
      <li class="list-group-item mt-2">
        <router-link :to=" {
                       path: '/ga',
                       query: { title: 'Mock Quiz 1' }
                     }" class="no-link">
          <span><i class="bi bi-pencil-square me-2"></i> Generate Mock Quiz 1</span>
        </router-link>
      </li>

      <li v-for="(section, index) in sidebarSectionsAfterMockQuiz1" :key="'after1-' + index" class="list-group-item">
        <div
          class="d-flex justify-content-between align-items-center section-header"
          @click="handleCollapse(section.id)"
        >
          <span>
            <i class="bi me-2"
               :class="activeSection === section.id ? 'bi-caret-down-fill' : 'bi-caret-right-fill'">
            </i> {{ section.title }}
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
            <router-link :to=" {
                           path: item.link,
                           query: {
                             title: item.text,
                             videoId: item.videoId
                           }
                         }" class="no-link">
              <img v-if="item.icon" :src="item.icon" alt="" class="me-2" style="  width:16px;"/>
              {{ item.text }}
            </router-link>
          </li>
        </ul>
      </li>

      <!-- Mock Quiz 2 -->
      <li class="list-group-item mt-2">
        <router-link :to=" {
                       path: '/ga',
                       query: { title: 'Mock Quiz 2' }
                     }" class="no-link">
          <span><i class="bi bi-pencil-square me-2"></i> Generate Mock Quiz 2</span>
        </router-link>
      </li>

      <li v-for="(section, index) in sidebarSectionsAfterMockQuiz2" :key="'after2-' + index" class="list-group-item">
        <div
          class="d-flex justify-content-between align-items-center section-header"
          @click="handleCollapse(section.id)"
        >
          <span>
            <i class="bi me-2"
               :class="activeSection === section.id ? 'bi-caret-down-fill' : 'bi-caret-right-fill'">
            </i> {{ section.title }}
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
            <router-link :to=" {
                           path: item.link,
                           query: {
                             title: item.text,
                             videoId: item.videoId
                           }
                         }" class="no-link">
              <img v-if="item.icon" :src="item.icon" alt="" class="me-2" style="  width:16px;"/>
              {{ item.text }}
            </router-link>
          </li>
        </ul>
      </li>

      <!-- Additional Mock Quizzes -->
      <li class="list-group-item mt-2">
        <router-link :to=" {
                       path: '/ga',
                       query: { title: 'Mock End Term' }
                     }" class="no-link">
          <span><i class="bi bi-pencil-square me-2"></i> Generate Mock End Term</span>
        </router-link>
      </li>

      <li class="list-group-item mt-2">
        <router-link to='/generate-topic-mock' class="no-link">
          <span><i class="bi bi-pencil-square me-2"></i> Generate Topic Specific Mock</span>
        </router-link>
      </li>
      <li class="list-group-item mt-2">
        <router-link to='/kia' class="no-link">
          <span><i class="bi bi-pencil-square me-2"></i>Kia</span>
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import bookIcon from '@/assets/sidebar-modules-selected.svg';
import bootstrap from 'bootstrap/dist/js/bootstrap.bundle'
export default {
  name: 'AppSidebar',
  data() {
    return {
      activeSection: localStorage.getItem("activeSection") || null,
      collapseInstances: {},
      sidebarSections: [
        {
          id: 'week1Collapse',
          title: 'Week 1',
          items: [
            {
              icon: bookIcon,
              text: '1.1 Data Visualization',
              link: '/lecture',
              videoId: 'kIyxumBVo6o'
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
              text: '2.1 Data Preprocessing',
              link: '/lecture',
              videoId: '_PcVkfVsjuo'
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
              text: '3.1 Linear Regression',
              link: '/lecture',
              videoId: 'SFYn4UnZaSQ'
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
              text: '4.1 Polynomial Regression',
              link: '/lecture',
              videoId: 'dMHECW-BkIM'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 4',
              link: '/ga'
            },
            {
              icon: bookIcon,
              text: 'Programming Assignment 1',
              link: '/grpa'
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
              text: '5.1 Classification Functions in Scikit Learn',
              link: '/lecture',
              videoId: 'dhYydFzxfes'
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
              text: '6.1 Naive Bayes Classifier',
              link: '/lecture',
              videoId: 'uM-MNko46Zo'
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
              text: '7.1 K-Nearest Neighbors',
              link: '/lecture',
              videoId: 'gKiFTMLgZy4'
            },
            {
              icon: bookIcon,
              text: 'Graded Assignment 7',
              link: '/ga',
            },
          ],
        },
        {
          id: 'week8Collapse',
          title: 'Week 8',
          items: [
            {
              icon: bookIcon,
              text: '8.1 Decision Trees',
              link: '/lecture',
              videoId: '5OZc2zWS2cY'
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
              text: '9.1 Bagging and Random Forest',
              link: '/lecture',
              videoId: 'EZ5szvjQgWw'
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
              text: '10.1 K-means Clustering on Digit Dataset',
              link: '/lecture',
              videoId: '-tPSKI9nUf0'
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
              text: '11.1 Neural Networks: Multi-layer Perceptron',
              link: '/lecture',
              videoId: 'wphku4k1e90'
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
              text: '12.1 SVM',
              link: '/lecture',
              videoId: '5erlKOqL8Xk'
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
  computed: {
    sectionGroups() {
      return [
        this.sidebarSections,
        this.sidebarSectionsAfterMockQuiz1,
        this.sidebarSectionsAfterMockQuiz2
      ]
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.sectionGroups.flat().forEach((section) => {
        const element = document.getElementById(section.id);
        this.collapseInstances[section.id] = new bootstrap.Collapse(element, {
          toggle: false,
        });

        element.addEventListener("shown.bs.collapse", () => {
          this.activeSection = section.id;
          localStorage.setItem("activeSection", section.id);
        });

        element.addEventListener("hidden.bs.collapse", () => {
          if (this.activeSection === section.id) {
            this.activeSection = null;
            localStorage.removeItem("activeSection");
          }
        });
      });

      const storedSection = localStorage.getItem("activeSection");
      if (storedSection && this.collapseInstances[storedSection]) {
        this.collapseInstances[storedSection].show();
      }
    });
  },
  methods: {
    handleCollapse(sectionId) {
      if (this.activeSection === sectionId) {
        this.collapseInstances[sectionId].hide();
      } else {
        Object.keys(this.collapseInstances).forEach((id) => {
          if (id !== sectionId && this.collapseInstances[id]._isShown) {
            this.collapseInstances[id].hide();
          }
        });
        this.collapseInstances[sectionId].show();
      }
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
