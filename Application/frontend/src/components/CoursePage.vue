<template>
  <div>
    <!-- Navbar -->
    <AppNavbar/>

    <!-- Main Layout -->
    <div class="container-fluid">
      <div class="row">
        <!-- Sidebar -->
        <AppSidebar/>

        <!-- Main Content -->
        <div class="col-9 p-4">
          <!-- Replace this with your main content -->
          <div class="d-flex align-items-center">
            <h4 class="mb-0 me-3">About the Course</h4>
            <div>
              <span class="me-1" style="  color: #f0c929;">★</span>
              <span class="me-1" style="  color: #f0c929;">★</span>
              <span class="me-1" style="  color: #f0c929;">★</span>
              <span class="me-1 text-muted">★</span>
              <span class="me-1 text-muted">★</span>
              <span>3.2/5 (4 reviews)</span>
              <a href="#" class="ms-3">Submit a review</a>
            </div>
          </div>
          <p>Duration:- 12 Week</p>
          <br/>
          <p>
            Faculty:
            <br/>
            Amit Kulkarni, IIT Madras
          </p>
          <br/>
          <p>
            Course instructors:
            <br/>
            Sandeep Kumar
            <br/>
            Siddharth Umathe
            <br/>
            Jyotiraditya Saha
          </p>
          <br/>
          <p>
            Reference books:
            <br/>
            Hands on Machine Learning with Scikit-Learn and Tensorflow by Kajol Singh, Saima Shroff and Anjali Galav
            <br/>
          </p>
          <br/>
          <p>
            To know more about course syllabus, Instructors and Prescribed Books please click on
            the below tab:
            <br/>
            <a href="https://onlinedegree.iitm.ac.in/course_pages/BCSCS2008.html">
              https://onlinedegree.iitm.ac.in/course_pages/BCSCS2008.html
            </a>
          </p>
          <p>
            The learners are advised to make best use of the interaction sessions with the course support members to clarify their doubts.
            <br/>
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
      <ChatWindow/>
    </div>
  </div>
</template>

<script>
import AppNavbar from '@/components/AppNavbar.vue';
import AppSidebar from '@/components/AppSidebar.vue';
import ChatWindow from "@/components/ChatWindow.vue";

export default {
  name: 'CoursePage',
  components: {
    AppNavbar,
    AppSidebar,
    ChatWindow
  },
};
</script>

<style scoped></style>