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

      <template v-if="allSidebarSections.length > 0">
        <li v-for="(section, index) in allSidebarSections" :key="'section-' + index" class="list-group-item">
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
              <router-link
                :to="getItemLink(item)"
                class="no-link"
              >
                <img v-if="item.icon" :src="item.icon" alt="" class="me-2" style=" width:16px;"/>
                <span>{{ item.text }}</span>
                <!-- Show due date for assignments if available -->
                <small v-if="item.itemType === 'assignment' && item.dueDate" class="ms-2 text-danger">
                  Due: {{ formatDate(item.dueDate) }}
                </small>
              </router-link>
            </li>
          </ul>
        </li>
      </template>

      <!-- Loading State -->
      <div v-else class="text-center py-3">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Additional Mock Quizzes -->
      <li class="list-group-item mt-2">
        <router-link to="/mock-quiz" class="nav-link">
          <i class="bi bi-lightning-charge me-2"></i>
          Mock Quiz Generator
        </router-link>        
      </li>

      <li class="list-group-item mt-2">
        <router-link to='/generate-topic-mock' class="no-link">
          <span><i class="bi bi-pencil-square me-2"></i> Generate Topic Specific Questions</span>
        </router-link>
      </li>
      <li class="list-group-item mt-2">
        <router-link to='/kia' class="no-link">
          <span><i class="bi bi-pencil-square me-2"></i>Generate Short Notes</span>
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import bookIcon from '@/assets/sidebar-modules-selected.svg';
import bootstrap from 'bootstrap/dist/js/bootstrap.bundle'
import api from "@/services/api.js"
export default {
  name: 'AppSidebar',
  data() {
    return {
      activeSection: localStorage.getItem("activeSection") || null,
      collapseInstances: {},
      allSidebarSections: []
    };
  },
  computed: {
    sectionGroups() {
      return [
        this.allSidebarSections,
      ]
    }
  },
  async mounted() {
    await this.fetchWeeks();

    this.$nextTick(() => {
      this.allSidebarSections.forEach((section) => {
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
    // In your methods section
    async fetchWeeks() {
      try {
        // 1. Get all weeks
        const weeksResponse = await api.get('/weeks');

        if (!weeksResponse.data.success) {
          console.error('Failed to fetch weeks:', weeksResponse.data.message);
          return ;
        }

        // 2. Fetch details for each week in parallel
        const weekPromises = weeksResponse.data.weeks.map(week =>
          api.get(`/weeks/${week.id}`)
        );

        const weekDetails = await Promise.all(weekPromises);

        // 3. Fetch all assignments for additional details
        const assignmentsResponse = await api.get('/assignments');

        // Create a lookup map for quick access to assignment details
        const assignmentDetailsMap = {};
        if (assignmentsResponse.data.success) {
          assignmentsResponse.data.assignments.forEach(assignment => {
            assignmentDetailsMap[assignment.id] = assignment;
          });
        }

        // 4. Organize into section groups with enhanced assignment data
        this.organizeSections(
          weekDetails.map(res => res.data.week),
          assignmentDetailsMap
        );
      } catch (error) {
        console.error('Error fetching data:', error);
        // Show user-friendly error message
        this.$toast?.error('Failed to load course content. Please try again later.');
      }
    },

    organizeSections(weeks, assignmentDetailsMap = {}) {
      weeks.forEach(week => {
        const section = {
          id: `week${week.week_number}Collapse`,
          title: week.title,
          items: []
        };

        // Add lectures
        section.items.push(...week.lectures.map(lec => ({
          icon: bookIcon,
          text: `${week.week_number}.1 ${lec.title}`,
          link: '/lecture',
          videoId: lec.video_id,
          itemType: 'lecture'
        })));

        // Add assignments with enhanced details
        section.items.push(...week.assignments.map(assgn => {
          // Get additional assignment details if available
          const details = assignmentDetailsMap[assgn.id] || {};

          return {
            icon: this.getAssignmentIcon(assgn.assignment_type),
            text: assgn.title,
            link: `/assignment/${assgn.id}`,
            assignmentId: assgn.id,
            assignmentType: assgn.assignment_type,
            dueDate: details.due_date,
            totalPoints: details.total_points,
            itemType: 'assignment'
          };
        }));

        // Add all sections to a single array, sorted by week number
        this.allSidebarSections.push(section);
      });

      // Sort sections by week number if needed
      this.allSidebarSections.sort((a, b) => {
        const weekA = parseInt(a.id.replace('week', '').replace('Collapse', ''));
        const weekB = parseInt(b.id.replace('week', '').replace('Collapse', ''));
        return weekA - weekB;
      });
    },

    // New method to get the appropriate link based on item type
    getItemLink(item) {
      if (item.itemType === 'lecture') {
        return {
          path: item.link,
          query: {
            title: item.text,
            videoId: item.videoId
          }
        };
      } else if (item.itemType === 'assignment') {
        // Check assignment type for programming assignments
        if (item.assignmentType === 'programming') {
          return {
            path: `/programming/${item.assignmentId}`,
            query: { title: item.text }
          };
        } else {
          return { path: item.link };
        }
      } else {
        return { path: item.link };
      }
    },

    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      });
    },

    getAssignmentIcon(assignmentType) {
      // Return different icons based on assignment type
      switch (assignmentType) {
        case 'graded':
          return require('@/assets/assignment-svgrepo-com.svg');
        case 'practice':
          return require('@/assets/discuss.svg');
        case 'programming':
          return require('@/assets/programming-svgrepo-com.svg'); 
        default:
          return require('@/assets/discuss.svg');
      }
    },

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
