<!-- File: CoursePage.vue -->
<template>
  <!-- Navigation Bar -->
  <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom">
    <div class="container-fluid">
      <!-- Left side: Logo + Subject Name -->
      <a class="navbar-brand d-flex align-items-center" href="#">
        <img
          :src="logoPath"
          alt="Institute Logo"
          width="120"
          height="40"
          class="me-2"
        />
        <span>PDSA</span>
      </a>

      <!-- Right side: Support, Profile icons, etc. -->
      <ul class="navbar-nav ms-auto">
        <li class="nav-item me-3">
          <a class="nav-link" href="#">
            <i class="bi bi-question-circle"></i>
            Support
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="#">
            <i class="bi bi-person-circle"></i>
            Profile
          </a>
        </li>
      </ul>
    </div>
  </nav>

  <!-- Main Layout -->
  <div class="container-fluid">
    <div class="row">
      <!-- Sidebar -->
      <div class="col-3 bg-light min-vh-100 p-3">
        <h5 class="mb-3">Course Introduction</h5>
        <ul class="list-group">
          <!-- Collapsible Items with Dropdown Icon -->
          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#courseIntroCollapse"
            aria-expanded="false"
            aria-controls="courseIntroCollapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> About the Course
          </li>
          <ul class="collapse list-group child-list" id="courseIntroCollapse">
            <li class="list-group-item child-list-item">Lecture 1.1: Introduction</li>
          </ul>

          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#generalCollapse"
            aria-expanded="false"
            aria-controls="generalCollapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> General Instructions & Important Links
          </li>
          <ul class="collapse list-group child-list" id="generalCollapse">
            <li class="list-group-item child-list-item">Important PDF</li>
            <li class="list-group-item child-list-item">Resource Links</li>
          </ul>

          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#week1Collapse"
            aria-expanded="false"
            aria-controls="week1Collapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> Week 1
          </li>
          <ul class="collapse list-group child-list" id="week1Collapse">
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Lecture 1.1 Lists and Dictionaries
            </li>
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Graded Assignment 1
            </li>
          </ul>

          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#week2Collapse"
            aria-expanded="false"
            aria-controls="week2Collapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> Week 2
          </li>
          <ul class="collapse list-group child-list" id="week2Collapse">
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Lecture 2.1 Stacks
            </li>
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Graded Assignment 2
            </li>
          </ul>

          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#week3Collapse"
            aria-expanded="false"
            aria-controls="week3Collapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> Week 3
          </li>
          <ul class="collapse list-group child-list" id="week3Collapse">
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Lecture 3.1 Queues
            </li>
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Graded Assignment 3
            </li>
          </ul>
          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#week4Collapse"
            aria-expanded="false"
            aria-controls="week4Collapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> Week 4
          </li>
          <ul class="collapse list-group child-list" id="week4Collapse">
            <li class="list-group-item child-list-item">
              <img :src="bookIcon" alt="Book Icon" class="me-2" style="width:16px;"/>
              Lecture 4.1 Graphs
            </li>
            <li class="list-group-item child-list-item">
              <img :src="bookIcon" alt="Book Icon" class="me-2" style="width:16px;"/>
              Graded Assignment 4
            </li>
          </ul>

          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#week5Collapse"
            aria-expanded="false"
            aria-controls="week5Collapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> Week 5
          </li>
          <ul class="collapse list-group child-list" id="week5Collapse">
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Lecture 5.1 Graphs
            </li>
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Graded Assignment 5
            </li>
          </ul>

          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#week6Collapse"
            aria-expanded="false"
            aria-controls="week6Collapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> Week 6
          </li>
          <ul class="collapse list-group child-list" id="week6Collapse">
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Lecture 6.1 Trees
            </li>
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Graded Assignment 6
            </li>
          </ul>

          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#week7Collapse"
            aria-expanded="false"
            aria-controls="week7Collapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> Week 7
          </li>
          <ul class="collapse list-group child-list" id="week7Collapse">
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Lecture 7.1 Priority Queues
            </li>
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Graded Assignment 7
            </li>
          </ul>

          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#week8Collapse"
            aria-expanded="false"
            aria-controls="week8Collapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> Week 8
          </li>
          <ul class="collapse list-group child-list" id="week8Collapse">
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Lecture 8.1 Linked Lists
            </li>
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Graded Assignment 8
            </li>
          </ul>

          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#week9Collapse"
            aria-expanded="false"
            aria-controls="week9Collapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> Week 9
          </li>
          <ul class="collapse list-group child-list" id="week9Collapse">
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Lecture 9.1 Heaps
            </li>
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Graded Assignment 9
            </li>
          </ul>

          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#week10Collapse"
            aria-expanded="false"
            aria-controls="week10Collapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> Week 10 (Refresher Week)
          </li>
          <ul class="collapse list-group child-list" id="week10Collapse">
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Lecture 10.1 Revision
            </li>
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Graded Assignment 10
            </li>
          </ul>

          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#week11Collapse"
            aria-expanded="false"
            aria-controls="week11Collapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> Week 11
          </li>
          <ul class="collapse list-group child-list" id="week11Collapse">
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Lecture 11.1 Dynamic Programming
            </li>
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Graded Assignment 11
            </li>
          </ul>

          <li
            class="list-group-item"
            data-bs-toggle="collapse"
            data-bs-target="#week12Collapse"
            aria-expanded="false"
            aria-controls="week12Collapse"
          >
            <i class="bi bi-caret-right-fill me-2"></i> Week 12 (Extra Contents)
          </li>
          <ul class="collapse list-group child-list" id="week12Collapse">
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Lecture 12.1 Streamlit
            </li>
            <li class="list-group-item child-list-item"><img :src="bookIcon" alt="Book Icon" class="me-2"
                                                             style="width:16px;"/>Graded Assignment 12
            </li>
          </ul>
          <li class="list-group-item"><img :src="bookIcon" alt="Book Icon" class="me-2" style="width:16px;"/>Generate
            Mock Practice Problems
          </li>
        </ul>
      </div>

      <!-- Main Content -->
      <div class="col-9 p-4">
        <div class="d-flex align-items-center">
          <h4 class="mb-0 me-3">About the Course</h4>
          <div>
            <span class="me-1" style="color: #f0c929;">★</span>
            <span class="me-1" style="color: #f0c929;">★</span>
            <span class="me-1" style="color: #f0c929;">★</span>
            <span class="me-1 text-muted">★</span>
            <span class="me-1 text-muted">★</span>
            <span>3.2/5 (4 reviews)</span>
            <a href="#" class="ms-3">Submit a review</a>
          </div>
        </div>

        <p class="mt-3">
          This course will cover the following basic concepts of Data Structures and Algorithms
          using Python:-
          <br/>
          Asymptotic complexity, O() notation, sorting and searching algorithms
          <br/>
          Data structures: linked list, NumPy array, hashing, stack and queue
          <br/>
          Algorithms on graphs: exploration, connectivity, the shortest paths,
          directed acyclic graphs, spanning trees
          <br/>
          Data structures: heaps, union of disjoint sets, search trees
          <br/>
          Design techniques: greedy, divide and conquer, dynamic programming
          <br/>
          Pattern matching algorithms
          <br/>
          Linear programming, intractability
        </p>

        <p>Duration:- 12 Week</p>
        <p>
          Faculty:
          <br/>
          Prof. Amit Kulkarni, Director, IIT Madras
        </p>
        <p>
          Course instructors:
          <br/>
          Sandeep Kumar
          <br/>
          Siddharth Umathe
          <br/>
          Jyotiraditya Saha
        </p>
        <p>
          Reference books:
          <br/>
          Algorithm Design, by Kajol Singh and Anjali Galav
          <br/>
          Introduction to Algorithms, by Saima Shroff, Kajol Singh, Anjali Galav
          <br/>
          Algorithms, by A.Kulkarni, J. Saha
        </p>
        <p>
          To know more about course syllabus, Instructors and Prescribed Books please click on
          the below tab:
          <br/>
          <a href="https://onlinedegree.iitm.ac.in/course_pages/BCSCS2002.html">
            https://onlinedegree.iitm.ac.in/course_pages/BCSCS2002.html
          </a>
        </p>
        <p>
          Course specific calendar:
          <br/>
          Please click on the below tab to view the Course Specific Calendar.
          This will have details about all the live sessions and any other events related to the course.
          Add it to your Google calendar to keep track so that you don’t miss out on any important interactions.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import logoPath from '@/assets/iitm-logo@3x.png'
import bookIcon from '@/assets/sidebar-modules-selected.svg'

export default {
  name: 'CoursePage',
  data() {
    return {
      logoPath, bookIcon
    }
  }
}
</script>

<style scoped>
.min-vh-100 {
  min-height: 100vh;
}

/* Styles for child list items to stand out */
.child-list-item {
  font-size: 0.9rem;
  background-color: #fafafa;
}
</style>
